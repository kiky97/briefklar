"""Evaluate the letter-helper pipeline on the synthetic letters.

    python -m eval.run_eval                              # extraction + explanations (EN, UK, TI)
    python -m eval.run_eval --languages English,Arabic   # choose target languages
    python -m eval.run_eval --judge                      # + LLM judge (needs JUDGE_MODEL)

Apertus (APERTUS_* env) does all the work being evaluated. The optional judge is a
DIFFERENT open-weights model (JUDGE_* env) that only scores explanations; it never
produces anything shown to users.
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import pipeline  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.grounding import amount_in, find_amounts, find_dates, normalize_digits  # noqa: E402
from app.llm import get_llm  # noqa: E402
from eval.dataset import LETTERS  # noqa: E402
from eval.langcheck import check_language  # noqa: E402

RESULTS = Path(__file__).parent / "results"

JUDGE_SYSTEM = """You are a strict evaluator. A person received an official letter and an assistant explained it to them in {language}.
You get the original letter, the correct key facts, and the explanation.

1. Translate the explanation into English (field "translation_en"). If you cannot read {language} well, say so in "notes".
2. Judge the explanation against the letter:
   - "dates_correct": true if every important date in the correct facts is stated correctly and no date is wrong.
   - "amounts_correct": true if every important amount is stated correctly and no amount is wrong.
   - "hallucination": true if the explanation states any fact, obligation or consequence that is NOT supported by the letter.
   - "clarity": 1-5, how easy it is for a non-expert to understand what to do (5 = very clear).
Return ONLY a JSON object with keys: translation_en, dates_correct, amounts_correct, hallucination, clarity, notes."""


class Judge:
    def __init__(self):
        s = get_settings()
        self.model = os.environ["JUDGE_MODEL"]
        self.client = OpenAI(
            base_url=os.getenv("JUDGE_BASE_URL", s.base_url),
            api_key=os.getenv("JUDGE_API_KEY", s.api_key) or "missing-key",
            timeout=180,
            default_headers={"User-Agent": "apertus-letter-helper-eval/0.1"},
        )

    def chat(self, messages, task="", temperature=0.0, max_tokens=1500):
        r = self.client.chat.completions.create(model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens)
        return r.choices[0].message.content or ""


def _ratio(hit: int, total: int):
    return None if total == 0 else hit / total


def score_extraction(letter: dict, facts) -> dict:
    pred_dates = {kd.date for kd in facts.key_dates}
    pred_deadlines = {kd.date for kd in facts.key_dates if kd.kind == "deadline"}
    gold_dates, gold_deadlines = set(letter["dates"]), set(letter["deadlines"])
    pred_amounts = {round(a.value, 2) for a in facts.amounts}
    actions_text = " ".join(facts.actions).lower()
    return {
        "type_correct": facts.letter_type == letter["type"],
        "date_recall": _ratio(len(pred_dates & gold_dates), len(gold_dates)),
        "date_precision": _ratio(len(pred_dates & gold_dates), len(pred_dates)),
        "deadline_recall": _ratio(len(pred_deadlines & gold_deadlines), len(gold_deadlines)),
        "invented_dates": sum(not kd.verified for kd in facts.key_dates),
        "amount_recall": _ratio(sum(amount_in(a, pred_amounts) for a in letter["amounts"]), len(letter["amounts"])),
        "amount_precision": _ratio(sum(amount_in(a, set(letter["amounts"])) for a in pred_amounts), len(pred_amounts)),
        "invented_amounts": sum(not a.verified for a in facts.amounts),
        "action_recall": _ratio(sum(any(k in actions_text for k in group) for group in letter["actions"]), len(letter["actions"])),
    }


def score_explanation(letter: dict, text: str, language: str = "English") -> dict:
    norm = normalize_digits(text)
    dates_found = find_dates(norm)
    amounts_found = find_amounts(norm)
    critical = [("date", d) for d in letter["deadlines"]] + [("amount", a) for a in letter["amounts"]]
    hits = sum(
        (date.fromisoformat(v) in dates_found) if kind == "date" else amount_in(v, amounts_found)
        for kind, v in critical
    )
    return {
        "critical_facts_preserved": _ratio(hits, len(critical)),
        "has_structure": text.count("## ") >= 4,
        **check_language(text, language),
        "chars": len(text),
    }


def run_letter(llm, judge, letter: dict, languages: list[str], strategy: str) -> dict:
    out = {"id": letter["id"], "lang": letter["lang"]}
    t0 = time.time()
    try:
        facts = pipeline.extract_facts(llm, letter["text"])
    except Exception as e:
        out["error"] = f"extract: {type(e).__name__}: {e}"
        return out
    out["extract_seconds"] = round(time.time() - t0, 1)
    out["facts"] = facts.model_dump()
    out["extraction"] = score_extraction(letter, facts)
    out["explanations"] = {}
    for language in languages:
        entry = {}
        try:
            t0 = time.time()
            text = pipeline.explain(llm, letter["text"], facts, language, strategy)
            entry = {"text": text, "seconds": round(time.time() - t0, 1), **score_explanation(letter, text, language)}
            if judge:
                gold = {k: letter[k] for k in ("dates", "deadlines", "amounts")}
                raw = judge.chat(
                    [
                        {"role": "system", "content": JUDGE_SYSTEM.format(language=language)},
                        {"role": "user", "content": f"LETTER:\n{letter['text']}\n\nCORRECT FACTS:\n{json.dumps(gold)}\n\nEXPLANATION ({language}):\n{text}"},
                    ],
                    task="judge",
                )
                entry["judge"] = pipeline.parse_json(raw)
        except Exception as e:
            entry["error"] = f"{type(e).__name__}: {e}"
        out["explanations"][language] = entry
    return out


def _mean(values):
    values = [float(v) for v in values if v is not None]
    return None if not values else sum(values) / len(values)


def _fmt(v):
    return "–" if v is None else f"{v:.2f}"


def summarize(results: list[dict], languages: list[str], model: str, judge_model: str | None, strategy: str) -> str:
    ok = [r for r in results if "extraction" in r]
    ex = [r["extraction"] for r in ok]
    lines = [
        f"# Evaluation run — {time.strftime('%Y-%m-%d %H:%M')}",
        "",
        f"- Apertus model: `{model}`",
        f"- Judge model: `{judge_model or 'none'}`",
        f"- Explanation strategy: `{strategy}`",
        f"- Letters: {len(results)} ({len(results) - len(ok)} failed extraction)",
        "",
        "## Fact extraction (letter → structured facts)",
        "",
        "| metric | mean |",
        "|---|---|",
    ]
    for key in ["type_correct", "date_recall", "date_precision", "deadline_recall", "amount_recall", "amount_precision", "action_recall"]:
        lines.append(f"| {key} | {_fmt(_mean(e[key] for e in ex))} |")
    lines.append(f"| invented dates (total) | {sum(e['invented_dates'] for e in ex)} |")
    lines.append(f"| invented amounts (total) | {sum(e['invented_amounts'] for e in ex)} |")
    lines += ["", "## Explanations by target language", ""]
    header = "| language | in requested language | critical facts preserved | structure ok |"
    sep = "|---|---|---|---|"
    if judge_model:
        header += " judge: dates ok | judge: amounts ok | judge: hallucination | judge: clarity (1-5) |"
        sep += "---|---|---|---|"
    lines += [header, sep]
    for lang in languages:
        es = [r["explanations"].get(lang, {}) for r in ok]
        es = [e for e in es if "error" not in e and e]
        row = f"| {lang} | {_fmt(_mean(e['language_ok'] for e in es))} | {_fmt(_mean(e['critical_facts_preserved'] for e in es))} | {_fmt(_mean(e['has_structure'] for e in es))} |"
        if judge_model:
            js = [e["judge"] for e in es if isinstance(e.get("judge"), dict)]
            row += " " + " | ".join(
                _fmt(_mean(j.get(k) for j in js)) for k in ("dates_correct", "amounts_correct", "hallucination", "clarity")
            ) + " |"
        lines.append(row)
    lines += ["", "## Per-letter extraction", "", "| letter | type | dates R/P | amounts R/P | actions R | invented |", "|---|---|---|---|---|---|"]
    for r in results:
        if "extraction" not in r:
            lines.append(f"| {r['id']} | ERROR: {r.get('error', '')[:80]} | | | | |")
            continue
        e = r["extraction"]
        lines.append(
            f"| {r['id']} | {'✓' if e['type_correct'] else '✗'} | {_fmt(e['date_recall'])}/{_fmt(e['date_precision'])} | "
            f"{_fmt(e['amount_recall'])}/{_fmt(e['amount_precision'])} | {_fmt(e['action_recall'])} | {e['invented_dates'] + e['invented_amounts']} |"
        )
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--languages", default="English,Ukrainian,Tigrinya")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--judge", action="store_true", help="score explanations with JUDGE_MODEL")
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--strategy", choices=pipeline.STRATEGIES, default="pivot")
    args = p.parse_args()

    languages = [l.strip() for l in args.languages.split(",") if l.strip()]
    letters = LETTERS[: args.limit] if args.limit else LETTERS
    settings = get_settings()
    llm = get_llm()
    judge = None
    if args.judge:
        if settings.mock:
            from app.llm import MockLLM
            judge = MockLLM()
        elif not os.getenv("JUDGE_MODEL"):
            sys.exit("--judge needs JUDGE_MODEL (an open-weights model other than Apertus).")
        else:
            judge = Judge()
    judge_model = ("mock" if settings.mock else os.getenv("JUDGE_MODEL")) if judge else None
    model = "mock" if settings.mock else settings.model

    print(f"Evaluating {len(letters)} letters × {len(languages)} languages with {model}…")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda l: run_letter(llm, judge, l, languages, args.strategy), letters))
    for r in results:
        print(f"  {r['id']:<30} {'ERROR ' + r['error'] if 'error' in r else 'ok'}")

    RESULTS.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    (RESULTS / f"run-{stamp}-{args.strategy}.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    summary = summarize(results, languages, model, judge_model, args.strategy)
    (RESULTS / f"run-{stamp}-{args.strategy}.md").write_text(summary, encoding="utf-8")
    print("\n" + summary)
    print(f"Saved to eval/results/run-{stamp}-{args.strategy}.json and .md")


if __name__ == "__main__":
    main()
