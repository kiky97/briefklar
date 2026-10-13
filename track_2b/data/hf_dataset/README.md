---
license: cc-by-4.0
language:
  - de
  - fr
  - it
  - en
  - uk
  - ti
  - ar
pretty_name: BriefKlar — Swiss official letters, explained
size_categories:
  - n<1K
task_categories:
  - text-generation
  - translation
tags:
  - apertus
  - hack-apertus
  - low-resource-languages
  - information-extraction
  - synthetic
configs:
  - config_name: test_cases
    data_files: test_cases.jsonl
  - config_name: model_responses
    data_files: model_responses.jsonl
  - config_name: metadata
    data_files: metadata.jsonl
---

# BriefKlar — Swiss official letters, explained

Evaluation data for **BriefKlar** (Hack Apertus 2026, Track 2B). BriefKlar is an Apertus-based assistant that explains Swiss administrative letters to people in their own language.

- Code and technical report: https://github.com/kiky97/briefklar
- Model evaluated: Apertus v1.5 70B (`apertus-v1.5-70b`)

## Contents

| File | Rows | What |
|---|---|---|
| `test_cases.jsonl` | 12 | **Evaluation dataset.** One synthetic letter per row (7 German, 3 French, 2 Italian) with hand-written gold labels: dates, deadlines, amounts, letter type and required actions (as keyword groups). |
| `model_responses.jsonl` | 120 | **Model responses.** For each letter and each of 2 strategies (`pivot`, `direct`): one extraction response (JSON facts) and explanations in English, Ukrainian, Tigrinya and Arabic, each with its automatic scores. |
| `metadata.jsonl` | 12 | **Metadata.** Provenance, creation method, instance-level license, personal-data flag and trap-case flag for every test case. |

### Fields

**test_cases:** `test_case_id`, `letter_language`, `letter_type`, `letter_text`, `gold_dates`, `gold_deadlines`, `gold_amounts`, `gold_action_keywords`

**model_responses:** `response_id`, `test_case_id`, `run_id`, `model`, `task` (`extraction` | `explanation`), `strategy` (`pivot` | `direct`, explanations only), `target_language`, `response`, `latency_s`, `scores`

**metadata:** `test_case_id`, `source`, `creation_method`, `license`, `contains_personal_data`, `entities_fictional`, `letter_language`, `letter_type`, `is_trap_case`, `notes`

## How the data was created

The BriefKlar team wrote all 12 letters by hand for this hackathon, imitating the style of Swiss administrative mail: tax office, police fines, migration office, health insurer, debt-collection office, employment office, school, property management and social insurance. **All people, addresses, institutions and reference numbers are fictional.** No real letters or personal data were used. Gold labels were annotated by hand.

One letter (`de_debt_collection_no_date`) is a trap case. It contains only relative deadlines ("within 10 days"), so the correct extraction contains no calendar date.

Model responses were produced with Apertus v1.5 70B through the Hack Apertus inference endpoint (temperature 0 for extraction and translation, 0.2 for explanations). They were scored with the deterministic checks in the project repository (`src/eval/`).

- **Extraction:** recall and precision of dates and amounts, letter type, action recall, invented values.
- **Explanation:** whether it is in the requested language (script check plus a Tigrinya/Amharic marker heuristic), share of gold deadlines and amounts preserved, structure compliance.

No other model was used.

## Key result

With `direct` generation, 9 of 12 "Tigrinya" explanations were actually Amharic. With `pivot` (English first, then translation with the language named natively, "Tigrinya (ትግርኛ)"), 12 of 12 were Tigrinya. Deadline recall was 1.00, and the model invented no dates or amounts.

## Intended use and limitations

- Intended use: evaluating LLMs on explaining administrative letters across languages, and in particular on detecting language drift in low-resource languages.
- The set is small (12 letters) and synthetic. Real letters are longer and often scanned.
- The Tigrinya/Amharic check is a heuristic. Tigrinya outputs have not been reviewed by a native speaker.
- Model responses are not legal advice.

## License

CC-BY-4.0 for all files. Every test case has its license recorded in `metadata.jsonl`.
