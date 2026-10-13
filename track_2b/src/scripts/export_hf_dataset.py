"""Build the Hugging Face dataset files required by Hack Apertus from data/.

    python scripts/export_hf_dataset.py

Writes data/hf_dataset/:
  test_cases.jsonl       evaluation dataset: one row per letter with gold labels
  model_responses.jsonl  model response dataset: one row per letter x task x strategy x language
  metadata.jsonl         metadata: provenance and instance-level licensing per test case
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.dataset import DATA_DIR, LETTERS  # noqa: E402

# The runs reported in technical_report.md section 5
RUNS = ["run-20261006-142305-pivot", "run-20261006-141428-direct"]
OUT = DATA_DIR / "hf_dataset"
LICENSE = "CC-BY-4.0"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{path.name}: {len(rows)} rows")


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    test_cases = [
        {
            "test_case_id": l["id"],
            "letter_language": l["lang"],
            "letter_type": l["type"],
            "letter_text": l["text"],
            "gold_dates": l["dates"],
            "gold_deadlines": l["deadlines"],
            "gold_amounts": l["amounts"],
            "gold_action_keywords": l["actions"],
        }
        for l in LETTERS
    ]

    responses = []
    for run_id in RUNS:
        strategy = run_id.rsplit("-", 1)[-1]
        run = json.loads((DATA_DIR / "results" / "runs" / f"{run_id}.json").read_text(encoding="utf-8"))
        for item in run:
            if "extraction" not in item:
                continue
            responses.append({
                "response_id": f"{run_id}/{item['id']}/extraction",
                "test_case_id": item["id"],
                "run_id": run_id,
                "model": "apertus-v1.5-70b",
                "task": "extraction",
                "strategy": None,
                "target_language": None,
                "response": json.dumps(item["facts"], ensure_ascii=False),
                "latency_s": item.get("extract_seconds"),
                "scores": item["extraction"],
            })
            for language, e in item["explanations"].items():
                if "text" not in e:
                    continue
                responses.append({
                    "response_id": f"{run_id}/{item['id']}/explanation/{language}",
                    "test_case_id": item["id"],
                    "run_id": run_id,
                    "model": "apertus-v1.5-70b",
                    "task": "explanation",
                    "strategy": strategy,
                    "target_language": language,
                    "response": e["text"],
                    "latency_s": e.get("seconds"),
                    "scores": {k: v for k, v in e.items() if k not in ("text", "seconds")},
                })

    metadata = [
        {
            "test_case_id": l["id"],
            "source": "synthetic; written by the BriefKlar team for Hack Apertus 2026",
            "creation_method": "hand-written in the style of Swiss administrative mail; gold labels hand-annotated",
            "license": LICENSE,
            "contains_personal_data": False,
            "entities_fictional": True,
            "letter_language": l["lang"],
            "letter_type": l["type"],
            "is_trap_case": not l["dates"],
            "notes": "relative deadlines only; correct output contains no calendar date" if not l["dates"] else "",
        }
        for l in LETTERS
    ]

    write_jsonl(OUT / "test_cases.jsonl", test_cases)
    write_jsonl(OUT / "model_responses.jsonl", responses)
    write_jsonl(OUT / "metadata.jsonl", metadata)


if __name__ == "__main__":
    main()
