# Evaluation run — 2026-10-06 16:23

- Apertus model: `mock`
- Judge model: `none`
- Explanation strategy: `pivot`
- Letters: 12 (0 failed extraction)

## Fact extraction (letter → structured facts)

| metric | mean |
|---|---|
| type_correct | 0.00 |
| date_recall | 1.00 |
| date_precision | 0.95 |
| deadline_recall | 1.00 |
| amount_recall | 1.00 |
| amount_precision | 0.18 |
| action_recall | 0.00 |
| invented dates (total) | 0 |
| invented amounts (total) | 0 |

## Explanations by target language

| language | in requested language | critical facts preserved | structure ok |
|---|---|---|---|
| English | 1.00 | 1.00 | 0.00 |

## Per-letter extraction

| letter | type | dates R/P | amounts R/P | actions R | invented |
|---|---|---|---|---|---|
| de_tax_invoice | ✗ | 1.00/0.67 | 1.00/0.17 | 0.00 | 0 |
| de_parking_fine | ✗ | 1.00/1.00 | 1.00/0.12 | 0.00 | 0 |
| de_permit_renewal | ✗ | 1.00/1.00 | 1.00/0.25 | 0.00 | 0 |
| de_insurance_reminder | ✗ | 1.00/1.00 | 1.00/0.33 | 0.00 | 0 |
| de_debt_collection_no_date | ✗ | –/– | 1.00/0.29 | 0.00 | 0 |
| de_rav_appointment | ✗ | 1.00/1.00 | –/0.00 | 0.00 | 0 |
| de_tax_return_reminder | ✗ | 1.00/1.00 | 1.00/0.33 | 0.00 | 0 |
| fr_tax_documents | ✗ | 1.00/1.00 | –/0.00 | 0.00 | 0 |
| fr_school_camp | ✗ | 1.00/0.75 | 1.00/0.25 | 0.00 | 0 |
| fr_rent_increase | ✗ | 1.00/1.00 | 1.00/0.29 | 0.00 | 0 |
| it_premium_reduction | ✗ | 1.00/1.00 | –/0.00 | 0.00 | 0 |
| it_speeding_fine | ✗ | 1.00/1.00 | 1.00/0.10 | 0.00 | 0 |
