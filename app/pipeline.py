import json
import re

from . import prompts
from .grounding import amount_in, find_amounts, find_dates, parse_amount, parse_date
from .schemas import DATE_KINDS, LETTER_TYPES, Amount, ChatTurn, Facts, KeyDate


def parse_json(text: str) -> dict:
    """Parse a JSON object from model output, tolerating code fences and surrounding prose."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("no JSON object in model output")
        return json.loads(text[start : end + 1])


def _normalize(data: dict) -> Facts:
    key_dates = []
    for item in data.get("key_dates") or []:
        if not isinstance(item, dict) or not (d := parse_date(str(item.get("date", "")))):
            continue
        kind = item.get("kind") if item.get("kind") in DATE_KINDS else "other"
        key_dates.append(KeyDate(date=d.isoformat(), kind=kind, what=str(item.get("what") or "")))

    amounts = []
    for item in data.get("amounts") or []:
        if not isinstance(item, dict) or (v := parse_amount(item.get("value"))) is None:
            continue
        amounts.append(Amount(value=v, currency=str(item.get("currency") or "CHF"), what=str(item.get("what") or "")))

    letter_type = data.get("letter_type") if data.get("letter_type") in LETTER_TYPES else "other"
    urgency = data.get("urgency") if data.get("urgency") in ("low", "medium", "high") else "medium"
    return Facts(
        sender=data.get("sender") or None,
        letter_language=str(data.get("letter_language") or "unknown"),
        letter_type=letter_type,
        summary_en=str(data.get("summary_en") or ""),
        key_dates=key_dates,
        amounts=amounts,
        reference_numbers=[str(r) for r in data.get("reference_numbers") or []],
        actions=[str(a) for a in data.get("actions") or []],
        urgency=urgency,
    )


def ground(facts: Facts, letter: str) -> Facts:
    """Mark which dates/amounts literally appear in the letter and warn about the rest."""
    letter_dates = {d.isoformat() for d in find_dates(letter)}
    letter_amounts = find_amounts(letter)
    for kd in facts.key_dates:
        kd.verified = kd.date in letter_dates
        if not kd.verified:
            facts.warnings.append(f"Date {kd.date} ({kd.what}) was not found literally in the letter - please double-check.")
    for am in facts.amounts:
        am.verified = amount_in(am.value, letter_amounts)
        if not am.verified:
            facts.warnings.append(f"Amount {am.currency} {am.value:.2f} was not found literally in the letter - please double-check.")
    return facts


def extract_facts(llm, letter: str) -> Facts:
    messages = [
        {"role": "system", "content": prompts.EXTRACT_SYSTEM},
        {"role": "user", "content": letter},
    ]
    raw = llm.chat(messages, task="extract", temperature=0.0)
    try:
        data = parse_json(raw)
    except (ValueError, json.JSONDecodeError):
        messages += [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": "That was not valid JSON. Return ONLY the JSON object, nothing else."},
        ]
        data = parse_json(llm.chat(messages, task="extract", temperature=0.0))
    return ground(_normalize(data), letter)


def _facts_json(facts: Facts) -> str:
    return facts.model_dump_json(exclude={"warnings"}, indent=1)


def explain(llm, letter: str, facts: Facts, language: str) -> str:
    messages = [
        {"role": "system", "content": prompts.EXPLAIN_SYSTEM.format(language=language)},
        {"role": "user", "content": prompts.facts_block(_facts_json(facts), letter)},
    ]
    return llm.chat(messages, task="explain").strip()


def ask(llm, letter: str, facts: Facts, language: str, question: str, history: list[ChatTurn]) -> str:
    messages = [
        {"role": "system", "content": prompts.ASK_SYSTEM.format(language=language)},
        {"role": "user", "content": prompts.facts_block(_facts_json(facts), letter)},
        {"role": "assistant", "content": "I have read the letter. What would you like to know?"},
    ]
    messages += [{"role": t.role, "content": t.content} for t in history[-8:]]
    messages.append({"role": "user", "content": question})
    return llm.chat(messages, task="ask").strip()


def draft_reply(llm, letter: str, facts: Facts, language: str, intent: str) -> str:
    messages = [
        {"role": "system", "content": prompts.REPLY_SYSTEM.format(language=language)},
        {"role": "user", "content": prompts.facts_block(_facts_json(facts), letter) + f"\n\nWHAT I WANT TO SAY:\n{intent}"},
    ]
    return llm.chat(messages, task="reply").strip()
