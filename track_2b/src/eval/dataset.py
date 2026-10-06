"""Loads the synthetic evaluation letters from data/letters.jsonl.

All senders, people, addresses and reference numbers are fictional. The letters imitate
the style of real Swiss administrative mail (DE/FR/IT) but contain no real personal data.

Gold fields per letter:
  type            expected letter_type
  dates           every calendar date that matters (ISO)
  deadlines       subset of `dates` that are deadlines for the recipient
  amounts         every money amount that matters
  actions         list of action groups; a group counts as found if ANY of its keywords
                  appears (case-insensitive) in the model's English action list
"""

import json
import os
from pathlib import Path

# track_2b/data locally; /data inside the Docker container (see docker-compose.yml)
DATA_DIR = Path(os.getenv("DATA_DIR") or Path(__file__).resolve().parents[2] / "data")


def load_letters(path: Path = DATA_DIR / "letters.jsonl") -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


LETTERS = load_letters()
