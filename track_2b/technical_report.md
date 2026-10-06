# Technical report — BriefKlar

Official letters, explained in your own language. An Apertus-based assistant that turns Swiss administrative letters into checked deadlines and plain-language explanations, including in low-resource languages.

- **Track:** Track 2B — BriefKlar
- **Event:** Online
- **Team:** BriefKlar — Shijin Zhou
- **Demo:** `TODO: link to video`

## 1. Summary

**Problem.** Migrants, refugees and other residents who don't read German, French or Italian regularly receive official letters with hard deadlines: tax bills, fines, residence-permit renewals, insurance reminders, debt collection. Missing a deadline costs money or legal standing. Machine translation translates words, but it doesn't say what to do by when, and it is weak in many of the languages these people speak (Tigrinya, Somali, Kurdish, ...).

**Approach.** BriefKlar uses Apertus to extract the letter's facts as JSON (dates, amounts, actions). Code then checks every date and amount against the letter text. Apertus writes an action-oriented explanation, and a separate Apertus call translates it into the user's language. The app also exports deadlines to a calendar, answers follow-up questions and drafts replies.

**Headline result.** ⟨RESULTS⟩

## 2. Architecture

```
Browser (single static page, no external assets)
   │  letter text / PDF
   ▼
FastAPI app (Docker image `briefklar`)
   1. extract   — Apertus → JSON facts (temperature 0)
   2. ground    — code: every date/amount re-found in the letter text, else flagged
   3. explain   — Apertus → English explanation; code rewrites dates to DD.MM.YYYY
   4. translate — Apertus → "<Language> (<native name>)", e.g. "Tigrinya (ትግርኛ)"
   5. extras    — Q&A, reply draft (Apertus); .ics calendar export (code)
   │
   ▼  OpenAI-compatible HTTP (LLM_BASE_URL, LLM_NAME, LLM_API_KEY)
Apertus: Hack Apertus endpoint, or vLLM with local weights (profile `local-gpu`)
```

The app keeps no state and writes no letters to disk. Its only outbound connection is `LLM_BASE_URL`.

### Target architecture (mandatory)

BriefKlar is deployable as **a) on-premise** and **b) air-gapped**, and the same images run on **c) a sovereign Swiss cloud**. Details are in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

- **a) On-premise:** `make run-local` starts the app and vLLM serving Apertus v1.5 from local weights (`models/apertus`) on the organisation's own GPU host.
- **b) Air-gapped:** the same stack with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` and vLLM usage stats disabled. The web page loads no CDN assets or fonts (a unit test checks this), and Swagger UI is off. Wheels, images and weights are prepared beforehand and copied in.
- **c) Sovereign Swiss cloud:** run the same compose file on a Swiss-operated GPU VM, or run only the app (`make run`) and point `LLM_BASE_URL` at a Swiss-hosted Apertus endpoint. During development we used the Hack Apertus inference endpoint. `TODO: confirm operator / jurisdiction / data-centre location with the organisers before claiming (c) for it.`

**External dependencies**

| | Build time | Runtime |
|---|---|---|
| Python packages (FastAPI, openai, pydantic, pypdf, ...) | PyPI or pre-downloaded wheels | — |
| Base images | `python:3.11-slim`, `vllm/vllm-openai` | — |
| Model weights | Hugging Face `swiss-ai/Apertus-v1.5-8B` / `-70B` | local files (a, b) |
| Inference | — | `LLM_BASE_URL` only |

## 3. Use of Apertus

- **Model:** `apertus-v1.5-70b` for all reported results (Hack Apertus endpoint). `apertus-v1.5-8b` works too (smoke-tested); it is the default for local GPU serving.
- **How it is used:** inference. Four task-specific prompts: extraction, explanation, translation, and Q&A/reply. No fine-tuning.
- **Where it runs:** hosted OpenAI-compatible endpoint during the hackathon; vLLM with local weights for on-premise and air-gapped deployment.

**Setup details** (all in `src/app/`):

- `prompts.py`: extraction returns a fixed JSON schema and is told never to compute dates ("within 10 days" stays a rule, not a date). The explanation follows a fixed five-section structure at about CEFR A2 level and keeps original official terms in parentheses.
- `pipeline.py`: JSON is parsed tolerantly (code fences, surrounding prose) with one repair retry. Temperature is 0 for extraction and translation and 0.2 for explanations.
- `languages.py`: every prompt names the target language natively as well, e.g. "Tigrinya (ትግርኛ)". See finding 2 below.
- `grounding.py`: deterministic parsing of DE/FR/IT/EN date formats and Swiss number formats (`2'486.40`, `Fr. 120.–`), plus non-Latin digits.

**Other models:** none. No other LLM was used in the product or in the evaluation. The eval harness can call an optional judge model (`--judge`), but it was **not** used for any result in this report. The language check in the evaluation is a deterministic heuristic, not a model.

## 4. Data

- `data/letters.jsonl`: **12 synthetic letters written for this project** (7 German, 3 French, 2 Italian; 9 letter types: tax, fine, residence permit, health insurance, debt collection, employment office, school, housing, social services). They imitate the style of Swiss administrative mail. All names, addresses, institutions and reference numbers are **fictional**, so there is no personal data. Each letter has hand-written gold labels: dates, deadlines, amounts, letter type and required actions. One letter is a deliberate trap: a debt-collection order with only relative deadlines ("within 10 days"), where the correct output contains no date.
- `data/results/runs/`: the full model responses and scores for every evaluation run.
- License: CC-BY-4.0 (created by the team).

## 5. Evaluation

⟨EVAL⟩

## 6. Limitations

- **Small synthetic test set** (12 letters, written by the team). Real letters are longer, contain tables, and arrive as photos.
- **No OCR yet.** The app accepts text and PDFs with a text layer only.
- **The language check is a heuristic.** Script detection plus Tigrinya/Amharic marker words. Tigrinya outputs have not yet been reviewed by a native speaker.
- **Q&A and reply drafting generate directly** in the target language. For Tigrinya they may show the same drift as direct explanations (finding 1); they should use the translation step too.
- **Secondary facts are sometimes missed**, e.g. expiry dates and side fees. Deadlines were always found, but the UI should invite users to check the original letter.
- **Latency.** Pivot plus translation takes about 2× as long; a Tigrinya explanation took about 40 s.
- **Not legal advice.** The UI says so and flags unverified facts.

## 7. Reproducibility

- **Run:** `cp .env.example .env`, set `LLM_API_KEY`, then `make run` (web app on :8000) or `make demo` (terminal, one letter end-to-end).
- **Numbers:** `make eval` runs both strategies over `data/letters.jsonl` and writes `data/results/runs/run-<timestamp>-<strategy>.{json,md}`.
- **Tests:** `make test` (offline, mock model).
- **Hardware:** any machine with Docker for the hosted-endpoint setup; an NVIDIA GPU with ≥24 GB VRAM for `make run-local` with the 8B model.
- **Settings:** `apertus-v1.5-70b`, temperature 0 (extraction, translation) / 0.2 (explanation), max 1500 tokens. The endpoint does not guarantee determinism, so expect small run-to-run variation.
- **Commit:** `TODO: final commit hash`

## 8. Next steps

- Native-speaker review of Tigrinya, Somali and Arabic outputs, and co-design of test letters with migrant counselling services
- Route Q&A and reply drafting through the translation step for low-resource languages
- OCR for photographed letters, running locally in the same container
- Compare Apertus v1.5 8B against 70B on cost per letter, to support small on-premise deployments
- A request queue for the endpoint's parallel-request limit

## License

Creative Commons Attribution 4.0 (CC-BY-4.0). All HackApertus projects are open-sourced.

## References

- Hack Apertus project template: https://github.com/HackApertus/project-template
- Apertus v1.5 models: https://huggingface.co/swiss-ai/Apertus-v1.5-8B, https://huggingface.co/swiss-ai/Apertus-v1.5-70B
