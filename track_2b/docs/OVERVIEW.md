# BriefKlar — overview

**Understand official letters in your own language.** Paste a letter from a tax office, migration office, health insurer, landlord or school (German, French, Italian), pick your language, and get:

1. A plain-language explanation (A2 level) in your language: what the letter is, what you must do, by when, how much it costs, and what to do if you disagree.
2. Key facts (dates, amounts, reference numbers, actions), each **checked against the letter text**. Anything the model produced that isn't literally in the letter is flagged.
3. A calendar file (.ics) with reminders 3 days before deadlines.
4. Follow-up Q&A in your language.
5. A draft reply in the letter's language, with a translation so you know what you are sending.

## Commands (from `track_2b/`)

```bash
cp .env.example .env   # set LLM_API_KEY (and LLM_NAME / LLM_BASE_URL if needed)
make run               # web app on http://localhost:8000
make demo              # one sample letter end-to-end in the terminal
make eval              # reproduce the evaluation -> data/results/runs/
make test              # offline unit tests
make run-local         # on-premise / air-gapped: app + Apertus on local vLLM (GPU)
```

## How it works

```
letter text ──► [Apertus] extract facts as JSON ──► normalize ──► grounding check (code, no LLM)
                                                                    │  dates/amounts not found in the
                                                                    │  letter → flagged as unverified
                                                                    ▼
   [Apertus] explain in English using letter + checked facts ──► dates → DD.MM.YYYY (code)
                                                                    ▼
   [Apertus] translate into "<Language> (<native name>)", e.g. "Tigrinya (ትግርኛ)"
   [Apertus] follow-up Q&A  ·  [Apertus] draft reply  ·  .ics export
```

## Code map (`src/`)

| Path | What |
|---|---|
| `app/pipeline.py` | extraction, explanation (pivot / direct), translation, Q&A, reply drafting |
| `app/grounding.py` | deterministic date and amount parsing (DE/FR/IT/EN, Swiss `2'486.40`, non-Latin digits), date normalization |
| `app/languages.py` | native language names used in prompts |
| `app/prompts.py` | all prompts |
| `app/llm.py` | OpenAI-compatible client (`LLM_*` env) plus offline mock |
| `app/main.py`, `app/static/` | web API and single-page UI |
| `app/cli.py` | terminal end-to-end run (`make demo`) |
| `eval/` | evaluation runner, dataset loader, Tigrinya/Amharic language check |
| `tests/` | unit and API tests |

## Data (`data/`)

- `letters.jsonl`: 12 synthetic, fully fictional letters (7 DE, 3 FR, 2 IT) with gold labels.
- `results/runs/`: model outputs and scores for every evaluation run (`.json` = all responses, `.md` = summary).

## Disclaimer

This is a hackathon prototype, not legal advice. Always verify deadlines with the original letter or the sender.
