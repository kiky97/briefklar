# Submission report: Letter Helper · Apertus

> Template. Fill in the TODOs after running the evaluation.

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
| Apertus (`TODO exact id`, via TODO endpoint) | All product functionality: fact extraction, explanations, Q&A, reply drafting | **Yes, the only model** |
| TODO (e.g. another open-weights model) | Evaluation judge only: back-translates each explanation to English and scores date/amount correctness, hallucination and clarity. Never shown to users. | No |
| Regex grounding (`app/grounding.py`) | Deterministic check of dates/amounts against the letter; also the mock/baseline | Yes (not an LLM) |

## 5. Evaluation

**Data**: 12 synthetic, fully fictional letters (7 DE, 3 FR, 2 IT) across 9 letter types, with hand-written gold labels, including one "no explicit date" trap.

**Results**: TODO: paste `eval/results/run-*.md`.

**Findings**: TODO, for example:
- which target languages preserve critical facts best or worst
- whether the grounding check caught invented dates or amounts
- whether the judge model agrees with the automatic metrics; for low-resource languages, the judge's own reading ability is a limitation

## 6. Limitations and next steps

- OCR for photographed letters (currently text and PDFs with a text layer)
- A small synthetic test set; a next step is co-designing test letters with migrant counselling services
- Human evaluation by native speakers of low-resource languages
- Not legal advice; the UI says so and flags unverified facts

## 7. Timeline

Project started during the hackathon (see git history from the first commit).
