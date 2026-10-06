# BriefKlar — official letters, explained in your language

Hack Apertus · **Track 2B (own project)**. The project lives in [`track_2b/`](track_2b/).

BriefKlar helps migrants and refugees in Switzerland understand official letters (tax, fines, residence permits, health insurance, debt collection) in their own language, including low-resource languages such as Tigrinya. It is built entirely on **Apertus**, runs in Docker, and can be deployed on-premise, air-gapped, or on a sovereign Swiss cloud.

```bash
cd track_2b
cp .env.example .env   # set LLM_API_KEY
make run               # http://localhost:8000
```

- Technical report: [`track_2b/technical_report.md`](track_2b/technical_report.md)
- Overview and commands: [`track_2b/docs/OVERVIEW.md`](track_2b/docs/OVERVIEW.md)
- Deployment (on-premise / air-gapped / Swiss cloud): [`track_2b/docs/DEPLOYMENT.md`](track_2b/docs/DEPLOYMENT.md)

Built from the [Hack Apertus project template](https://github.com/HackApertus/project-template). Licensed under Apache-2.0 (see `LICENSE`).
