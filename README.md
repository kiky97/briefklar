# Letter Helper · Apertus

**Understand official letters in your own language.** Paste a letter from a tax office, migration office, health insurer, landlord or school (German, French, Italian), pick your language, and get:

1. A plain-language explanation (A2 level) in your language: what the letter is, what you must do, by when, how much it costs, and what to do if you disagree.
2. Key facts (dates, amounts, reference numbers, actions), each **checked against the letter text**. Anything the model produced that isn't literally in the letter is flagged.
3. A calendar file (.ics) with reminders 3 days before deadlines.
4. Follow-up Q&A in your language.
5. A draft reply in the letter's language, with a translation so you know what you are sending.

Built on **Apertus**, the fully open Swiss LLM. Its multilingual coverage (1000+ languages, including many low-resource ones such as Tigrinya and Somali) is what makes this useful for migrants and refugees. Its open weights mean it can be self-hosted, so sensitive letters never have to leave your infrastructure.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env          # then put your Apertus API key in .env
python scripts/list_models.py # check the exact Apertus model id on your endpoint
uvicorn app.main:app --reload # open http://127.0.0.1:8000
```

No key? Set `MOCK_LLM=1` in `.env` to click through the UI with a regex stand-in.

## How it works

```
letter text ──► [Apertus] extract facts as JSON ──► normalize ──► grounding check (regex, no LLM)
                                                                    │  dates/amounts not found in the
                                                                    │  letter → flagged as unverified
                                                                    ▼
             [Apertus] explain in target language using letter + checked facts
             [Apertus] follow-up Q&A  ·  [Apertus] draft reply  ·  .ics export
```

- `app/pipeline.py`: extraction, explanation, Q&A, reply drafting
- `app/grounding.py`: deterministic date/amount parsing for DE/FR/IT/EN formats, Swiss number formats (`2'486.40`, `Fr. 120.–`), and non-Latin digits
- `app/prompts.py`: all prompts
- `app/llm.py`: OpenAI-compatible client (Public AI gateway, vLLM, ...) plus offline mock

## Evaluation

`eval/dataset.py` holds 12 synthetic, fully fictional letters (7 DE, 3 FR, 2 IT) with hand-written gold labels. They include a trap: a debt-collection order with relative deadlines only ("within 10 days"), where the correct output has **no** dates.

```bash
python -m eval.run_eval --languages English,Ukrainian,Tigrinya,Arabic
JUDGE_MODEL=<other open model> python -m eval.run_eval --judge
```

Metrics:
- **Extraction** (automatic): letter type accuracy, date/deadline/amount recall and precision, action recall, invented dates and amounts.
- **Explanation** (automatic): share of critical facts (deadlines and amounts) that survive into the target-language explanation, plus structure compliance.
- **Explanation** (optional LLM judge): a different open-weights model checks dates, amounts, hallucination and clarity. See REPORT.md for its role.

Results are written to `eval/results/`.

## Deployment

The app runs on-premise, air-gapped, or on a sovereign Swiss cloud. It makes no outbound requests besides the configured Apertus endpoint. See [DEPLOYMENT.md](DEPLOYMENT.md) and `docker-compose.yml` (app + vLLM with local Apertus weights).

## Tests

```bash
pytest
```

## Disclaimer

This is a hackathon prototype, not legal advice. Always verify deadlines with the original letter or the sender.
