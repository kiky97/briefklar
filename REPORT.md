# Submission report: Letter Helper · Apertus

> Draft. Remaining TODOs: section 6 (c) provider details.

## 1. Problem

People who don't speak the local official language (migrants, refugees, international workers, some elderly people) regularly receive letters in German, French or Italian that carry hard deadlines and real consequences: tax bills, fines, residence-permit renewals, insurance reminders, debt collection. Missing a deadline can mean late fees, debt-collection records or problems with a residence permit. Existing translation tools translate words, but they don't explain what to do and by when, and they are weak for many low-resource languages (Tigrinya, Somali, Kurdish, ...).

## 2. Solution

A web app that turns a letter into an action-oriented explanation in the user's language, with machine-checked deadlines, a calendar export, follow-up Q&A and reply drafting. See README.md.

## 3. Why Apertus

- **Language coverage**: Apertus was trained on 1000+ languages, so it serves the languages of the people who need this most.
- **Open weights, self-hostable**: official letters contain sensitive personal data. Counselling offices or municipalities can run Apertus on their own servers.
- **Transparent training data**: auditable provenance matters for a public-interest tool.

## 4. Use of models

| Model | Role | Used in the product? |
|---|---|---|
| Apertus `apertus-v1.5-70b` (Hack Apertus inference endpoint) | All product functionality: fact extraction, explanations, translation, Q&A, reply drafting. All reported results use this model. | **Yes, the only model** |
| Apertus `apertus-v1.5-8b` | Smoke-tested only (1 letter); a candidate for cheaper self-hosting | Not in reported results |
| Regex grounding (`app/grounding.py`) | Deterministic check of dates/amounts against the letter; date normalization to DD.MM.YYYY | Yes (not an LLM) |
| Heuristic language check (`eval/langcheck.py`) | Evaluation only: script detection plus Tigrinya/Amharic marker words | No (not an LLM) |

**No other LLM was used**, either in the product or in evaluation. The evaluation harness supports an optional judge model (`--judge`, `JUDGE_*` env), but it was not used for the results below.

## 5. Evaluation

**Data**: 12 synthetic, fully fictional letters (7 DE, 3 FR, 2 IT) across 9 letter types, with hand-written gold labels, including one "no explicit date" trap.

**Model**: `apertus-v1.5-70b`, temperature 0 for extraction and translation, 0.2 for explanations. Full outputs are in `eval/results/`.

### 5.1 Fact extraction (letter → structured facts)

| metric | value |
|---|---|
| letter type accuracy | 0.92 |
| deadline recall | **1.00** |
| date recall / precision | 0.91 / 1.00 |
| amount recall / precision | 0.89 / 1.00 |
| action recall | 0.98 |
| invented dates / amounts | **0 / 0** |
| "no explicit date" trap (debt collection) | passed: no date invented, the 10-day rule appears as an action |

Misses were all secondary facts: a permit expiry date and an offence date (both non-deadline dates), a CHF 30 reminder fee, and the old rent in a rent-increase notice. Every deadline was found.

### 5.2 Explanations: direct generation vs. English pivot + translation

Critical facts are the deadlines and amounts from the gold labels. "In requested language" is checked by script and, for Ge'ez script, by Tigrinya-vs-Amharic marker words.

| target language | in requested language (direct) | in requested language (pivot) | critical facts kept (direct) | critical facts kept (pivot) |
|---|---|---|---|---|
| English | 1.00 | 1.00 | 1.00 | 1.00 |
| Ukrainian | 1.00 | 1.00 | 0.94 | 1.00 |
| **Tigrinya** | **0.17** | **1.00** | 1.00 | 1.00 |
| Arabic | 1.00 | 1.00 | 1.00 | 1.00 |

Average latency per explanation (pivot): English 6.8 s, Ukrainian 16.9 s, Arabic 13.8 s, Tigrinya 39.9 s.

### 5.3 Findings

1. **Silent language drift in a low-resource language.** Asked for Tigrinya, direct generation produced fluent **Amharic** in 10 of 12 letters. Amharic is a related, higher-resource language written in the same script. Date and amount metrics did not notice, because the numbers were correct. A user who reads only Tigrinya would get a polished but partly incomprehensible answer.
2. **Naming the language in its own script fixes translation.** A plain translation prompt that said "Tigrinya" produced Oromo (Latin script). Saying "Tigrinya (ትግርኛ)" produced Tigrinya in every trial. The app now always names the target language natively (`app/languages.py`).
3. **Pivot strategy is the default.** The app writes the explanation in English, normalizes dates in code, then runs a focused translation call. This gave 12/12 correct-language outputs for Tigrinya and kept 100% of critical facts in all four languages. The cost is roughly one extra model call, so it is about 2× slower for non-English targets.
4. **Code-level grounding is cheap insurance.** Across all runs, extraction invented no dates or amounts. The check still runs on every request and flags anything not found literally in the letter.
5. **Format instructions are followed unevenly.** The model often wrote "November 30, 2026" despite being asked for DD.MM.YYYY. We now rewrite dates in code instead of relying on the prompt.

Caveat: the Tigrinya/Amharic check is a heuristic. Native-speaker review of the Tigrinya outputs is the most important next validation step.

## 6. Deployment architecture (Track 2B)

The app reaches Apertus only through a configurable OpenAI-compatible URL and makes no other outbound requests, so the same code runs in all three architectures. See DEPLOYMENT.md.

- **a) On-premise / b) Air-gapped** (primary): `docker-compose.yml` runs the app and vLLM serving local Apertus weights, with offline flags set and no external assets.
- **c) Sovereign Swiss cloud**: TODO: name the provider used during development or demo, its operating legal entity and jurisdiction, its data-centre location (e.g. Zurich), and its retention policy, with a link to the provider's documentation.

## 7. Limitations and next steps

- OCR for photographed letters (currently text and PDFs with a text layer)
- A small synthetic test set; a next step is co-designing test letters with migrant counselling services
- Human evaluation by native speakers of low-resource languages, especially Tigrinya
- Q&A and reply drafting still generate directly in the target language. Apply the pivot or translation step there too for low-resource languages
- The hackathon endpoint allows 5 parallel requests per key. The client retries on 429, but production needs a request queue
- Not legal advice; the UI says so and flags unverified facts

## 8. Timeline

Project started during the hackathon (see git history from the first commit).
