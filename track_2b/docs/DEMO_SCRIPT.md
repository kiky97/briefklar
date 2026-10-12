# BriefKlar — 2-minute demo script

About 270 words of narration, roughly 2 minutes at a calm pace. Each block gives the time, what to show, and what to say. The narration can also be pasted as subtitles.

## Before recording

- [ ] `cd track_2b` → `make run` (or `python -m uvicorn app.main:app --port 8000` in `src/`) → open http://localhost:8000
- [ ] Do one full test run so the endpoint is warm and you know it works
- [ ] Browser zoom 125–150 %, close other tabs, hide bookmarks bar
- [ ] **Close `.env` and anything that shows the API key**
- [ ] Have `technical_report.md` open at section 5.2 (the results table)
- [ ] Have a terminal open in `track_2b/` and `docker-compose.yml` open in an editor

---

## 0:00 – 0:15 · The problem

**Show:** the web app with the sample letter loaded (click **Load example**). Slowly scroll the German tax letter.

> Imagine you just moved to Switzerland and you receive this letter. It's in German. It contains a payment deadline and a deadline to object. Miss them, and you pay interest or lose your rights. For many migrants and refugees, letters like this arrive every month.

## 0:15 – 0:50 · Main flow: explain in Tigrinya

**Show:** type `Tigrinya` in the language box → click **Explain this letter**. *Cut or speed up the ~40 s wait; add the caption "≈40 s, sped up".* Then show the explanation, scroll down to **Key facts**, point at the green "found in letter" labels, and click **Add dates to calendar**.

> BriefKlar explains the letter in your own language, here Tigrinya, spoken by many Eritrean refugees in Switzerland. It's built entirely on Apertus, the open Swiss model. First, Apertus extracts the facts: deadlines, amounts and what you must do. Then our code checks every date and amount against the original letter. Anything the model cannot back up is flagged, never silently shown. One click puts the deadlines into your calendar.

## 0:50 – 1:05 · Follow-up and reply

**Show:** change the language box to `English`. Ask: `What happens if I pay late?` Then in **Draft a reply** type: `I agree with the amount but I would like to pay in two instalments.` Show the German reply and its English translation.

> You can ask follow-up questions, and BriefKlar drafts a polite reply in German, with a translation, so you know exactly what you're sending.

## 1:05 – 1:35 · What we learned (technical rigour)

**Show:** `technical_report.md`, section 5.2. Highlight the Tigrinya row: **0.25 → 1.00**.

> We evaluated it on twelve synthetic Swiss letters in German, French and Italian. Apertus found every deadline and invented no dates or amounts. But we also found a hidden failure. Asked to write Tigrinya directly, Apertus often wrote fluent Amharic instead: same script, different language. A facts-only metric gave it full marks. Our fix was to write in English first, then translate with the language named in its own script. Correct-language output went from three in twelve to twelve in twelve.

## 1:35 – 1:55 · Sovereign deployment

**Show:** the `Makefile` (the `run` target), then a terminal in `track_2b/` running `docker compose up --build app`, which is exactly what `make run` executes. This machine has no `make`. Run `docker compose down` first so port 8000 is free. Then show `docker-compose.yml` with the `apertus` vLLM service visible.

> BriefKlar runs in Docker with one command. For on-premise use, a counselling office or municipality runs the app and Apertus side by side on its own server, from open weights. Sensitive letters never leave the organisation.

## 1:55 – 2:00 · Close

**Show:** a title card: **BriefKlar**, "Official letters, explained in your language", the GitHub link and "Built with Apertus".

> BriefKlar. Official letters, explained in your language.

---

## Captions to add in the editor

| Time | Caption |
|---|---|
| 0:20 | Built on Apertus v1.5 70B |
| 0:30 | ≈40 s, sped up |
| 0:40 | ✓ every date and amount re-checked against the letter |
| 1:15 | 12 synthetic letters · DE / FR / IT · 4 target languages |
| 1:25 | Tigrinya in the right language: 3/12 → 12/12 |
| 1:40 | On-premise: app + Apertus (vLLM) on your own server |

## Notes

- All letters in the demo are fictional (from `data/letters.jsonl`); no real personal data is shown.
- If the endpoint is slow on the day, record the Tigrinya run once and reuse it; don't re-run live.
- Numbers quoted match `technical_report.md` §1 and §5. If you re-run the evaluation, update them.
