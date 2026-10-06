"""Thin wrapper around an OpenAI-compatible chat endpoint serving Apertus.

Works with the Public AI gateway, a local vLLM / llama.cpp server, or any other
OpenAI-compatible host: only LLM_BASE_URL / LLM_NAME change.
"""

import json
import re

from openai import OpenAI

from .config import Settings, get_settings
from .grounding import find_amounts, find_dates


class ApertusLLM:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            base_url=settings.base_url,
            api_key=settings.api_key or "missing-key",
            timeout=180,
            max_retries=6,  # backs off on 429s (hackathon endpoint: 5 parallel requests per key)
            default_headers={"User-Agent": "apertus-letter-helper/0.1"},
        )

    def chat(self, messages, task: str = "", temperature=None, max_tokens=None) -> str:
        limit = max_tokens or self.settings.max_tokens
        for attempt in range(2):
            resp = self.client.chat.completions.create(
                model=self.settings.model,
                messages=messages,
                temperature=self.settings.temperature if temperature is None else temperature,
                max_tokens=limit,
            )
            choice = resp.choices[0]
            # Non-Latin scripts cost far more tokens (Tigrinya: ~2 tokens per character), so a
            # limit sized for English silently cuts translations off. Retry once with more room.
            if choice.finish_reason != "length" or attempt == 1:
                return choice.message.content or ""
            limit = min(limit * 3, 8192)
        return ""


class MockLLM:
    """Offline stand-in used for UI development and unit tests. Not a model; pure regex."""

    def chat(self, messages, task: str = "", temperature=None, max_tokens=None) -> str:
        user = messages[-1]["content"]
        if task == "extract":
            dates = sorted(find_dates(user))
            amounts = sorted(a for a in find_amounts(user) if a >= 10 and not 1900 <= a <= 2100)
            return json.dumps(
                {
                    "sender": None,
                    "letter_language": "de",
                    "letter_type": "other",
                    "summary_en": "(mock) An official letter.",
                    "key_dates": [{"date": d.isoformat(), "kind": "deadline", "what": "(mock)"} for d in dates],
                    "amounts": [{"value": a, "currency": "CHF", "what": "(mock)"} for a in amounts],
                    "reference_numbers": [],
                    "actions": ["(mock) Read the letter carefully."],
                    "urgency": "medium",
                }
            )
        if task == "explain":
            m = re.search(r"FACTS:\n(\{.*?\})\n\nLETTER:", user, re.S)
            facts = json.loads(m[1]) if m else {}
            lines = ["## What is this letter?", "(mock explanation)", "## Important dates"]
            for d in facts.get("key_dates", []):
                y, mo, da = d["date"].split("-")
                lines.append(f"- {da}.{mo}.{y}: {d.get('what', '')}")
            lines.append("## Money")
            for a in facts.get("amounts", []):
                lines.append(f"- {a['currency']} {a['value']:.2f}")
            return "\n".join(lines)
        if task == "translate":
            return user
        if task == "judge":
            return json.dumps(
                {"translation_en": "(mock)", "dates_correct": True, "amounts_correct": True,
                 "hallucination": False, "clarity": 3, "notes": "mock"}
            )
        return f"(mock {task or 'answer'})"


def get_llm():
    settings = get_settings()
    return MockLLM() if settings.mock else ApertusLLM(settings)
