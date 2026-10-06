.PHONY: run demo eval test run-local stop

# Model access (Hack Apertus template): set LLM_NAME, LLM_BASE_URL, LLM_API_KEY in the
# environment or in a .env file next to this Makefile (see .env.example).

# Start the BriefKlar web app in Docker -> http://localhost:8000 (Ctrl+C to stop)
run:
	@echo ">> BriefKlar starting on http://localhost:$${PORT:-8000}  (model: $${LLM_NAME:-from .env or default})"
	docker compose up --build app

# End-to-end check without a browser: explain one sample letter in Ukrainian
demo:
	docker compose build app
	docker compose run --rm app python -m app.cli --language Ukrainian

# Reproduce the evaluation (results go to data/results/runs/)
eval:
	docker compose build app
	docker compose run --rm app python -m eval.run_eval --languages English,Ukrainian,Tigrinya,Arabic --strategy pivot
	docker compose run --rm app python -m eval.run_eval --languages English,Ukrainian,Tigrinya,Arabic --strategy direct

# Unit tests (offline, no model needed)
test:
	docker compose build app
	docker compose run --rm -e MOCK_LLM=1 app python -m pytest -q

# On-premise / air-gapped: serve Apertus locally with vLLM (NVIDIA GPU + ./models/apertus)
run-local:
	LLM_BASE_URL=http://apertus:8001/v1 LLM_API_KEY=local LLM_NAME=$${LLM_NAME:-apertus-v1.5-8b} \
		docker compose --profile local-gpu up --build

stop:
	docker compose --profile local-gpu down
