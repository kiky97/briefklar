# Evaluation runs

Each run has a `.json` file (every model response plus per-item scores) and a `.md` summary. All runs cover 12 letters and use `apertus-v1.5-70b`, except the mock baseline.

| Run | What changed | Used in report |
|---|---|---|
| `20261004-214948-direct` | first real run; English-only language names; no language check yet | history |
| `20261004-215545-pivot` | pivot without native names → Tigrinya came out as Oromo | history (finding 2) |
| `20261004-220613-pivot` | native names ("Tigrinya (ትግርኛ)"), date normalization | history |
| `20261004-221106-direct` | same, direct strategy | history |
| `20261006-141008-pivot` | prompt example removed; showed Tigrinya truncation at 1,500 tokens | history (finding 4) |
| `20261006-141428-direct` | final prompts, direct strategy | **yes** (direct column) |
| `20261006-142305-pivot` | final prompts + truncation fix, pivot strategy (app default) | **yes** (pivot column, extraction) |
| `20261006-162345-mock-regex-baseline` | no model: regex-only stand-in | **yes** (baseline) |

Reproduce with `make eval` from `track_2b/`.
