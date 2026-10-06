"""Command-line end-to-end run: letter in, checked facts + explanation out.

    python -m app.cli --language Tigrinya            # built-in sample letter
    python -m app.cli --language Arabic letter.txt   # your own letter (text file)
    python -m app.cli --sample fr_school_camp        # another sample from data/letters.jsonl
"""

import argparse
import sys
import time

from . import pipeline
from .config import get_settings
from .llm import get_llm


def main():
    p = argparse.ArgumentParser(description="Explain an official letter with Apertus.")
    p.add_argument("file", nargs="?", help="text file with the letter (default: a sample letter)")
    p.add_argument("--language", default="Ukrainian")
    p.add_argument("--sample", default="de_tax_invoice", help="sample id from data/letters.jsonl")
    p.add_argument("--strategy", choices=pipeline.STRATEGIES, default="pivot")
    args = p.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            letter = f.read()
    else:
        from eval.dataset import LETTERS

        letter = next(l["text"] for l in LETTERS if l["id"] == args.sample)

    s = get_settings()
    if not s.mock and not s.api_key:
        sys.exit("LLM_API_KEY is not set. Put it in .env (see .env.example) or export it.")
    print(f"Model: {'mock' if s.mock else s.model} @ {s.base_url}\n")
    print("=" * 70 + "\nLETTER\n" + "=" * 70 + f"\n{letter.strip()}\n")

    llm = get_llm()
    t = time.time()
    facts = pipeline.extract_facts(llm, letter)
    print("=" * 70 + f"\nKEY FACTS (checked against the letter)  [{time.time() - t:.1f}s]\n" + "=" * 70)
    for d in facts.key_dates:
        print(f"  {d.date}  {d.kind:<11} {d.what}  [{'found in letter' if d.verified else 'NOT FOUND - check!'}]")
    for a in facts.amounts:
        print(f"  {a.currency} {a.value:.2f}  {a.what}  [{'found in letter' if a.verified else 'NOT FOUND - check!'}]")
    for action in facts.actions:
        print(f"  -> {action}")
    for w in facts.warnings:
        print(f"  ! {w}")

    t = time.time()
    text = pipeline.explain(llm, letter, facts, args.language, args.strategy)
    print("\n" + "=" * 70 + f"\nEXPLANATION ({args.language})  [{time.time() - t:.1f}s]\n" + "=" * 70)
    print(text)


if __name__ == "__main__":
    main()
