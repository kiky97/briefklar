# Deployment

The app has two parts:

1. **Web app** (FastAPI + one static HTML page). It makes no outbound requests: no CDN scripts or web fonts, and Swagger docs are off by default.
2. **Apertus inference**, reached over an OpenAI-compatible API at `APERTUS_BASE_URL`.

Because inference is just a URL, the same code runs in all three Track 2B architectures. Only where Apertus is served changes.

| Architecture | Web app runs on | Apertus served by |
|---|---|---|
| a) On-premise | the organisation's server | vLLM on the same server or LAN (`docker-compose.yml`) |
| b) Air-gapped | an isolated host | vLLM with local weights, offline flags set (`docker-compose.yml`) |
| c) Sovereign Swiss cloud | a VM or container on a Swiss-operated cloud | a Swiss-operated Apertus endpoint, or vLLM on a GPU VM in the same cloud |

## a) On-premise

Requirements: Linux host with Docker and the NVIDIA container toolkit. Apertus-8B needs a GPU with about 24 GB VRAM (bf16). Apertus-70B needs multiple GPUs or quantization.

```bash
# 1. Get the weights (needs internet once)
pip install -U "huggingface_hub[cli]"
huggingface-cli download swiss-ai/Apertus-8B-Instruct-2509 --local-dir models/apertus

# 2. Start
docker compose up -d
# 3. Open http://<host>:8000
```

## b) Air-gapped

Prepare everything on a connected machine, then transfer it:

```bash
# Python dependencies as wheels (build for the target platform)
pip download -r requirements.txt -d wheels

# Model weights
huggingface-cli download swiss-ai/Apertus-8B-Instruct-2509 --local-dir models/apertus

# Container images
docker compose build --build-arg PIP_ARGS="--no-index --find-links=wheels"
docker pull vllm/vllm-openai:latest
docker save vllm/vllm-openai:latest apertus-letter-helper-app -o images.tar
```

Copy the project folder (with `models/`) and `images.tar` to the isolated host, then:

```bash
docker load -i images.tar
docker compose up -d
```

At runtime nothing leaves the host:
- vLLM runs with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and usage stats disabled.
- The web page loads no external resources.
- Date and amount checks, PDF reading and calendar export all run locally.

Verify by running the stack with the network unplugged, or with `docker network create --internal`.

## c) Sovereign Swiss cloud

Deploy the same `docker-compose.yml` on a GPU VM from a cloud provider that is operated in Switzerland, under Swiss jurisdiction, with Swiss data residency. Alternatively, run only the `app` service there and point `APERTUS_BASE_URL` at a Swiss-operated Apertus endpoint.

For the submission, document for the chosen provider:
- the legal entity operating the service and its jurisdiction
- the data-centre location(s)
- the retention and logging policy for prompts and responses

## Data handling

- The app stores no letters. Requests are processed in memory and never written to disk. Uvicorn access logs record only paths, not request bodies.
- Check the request-logging settings of the vLLM version you pin, so prompts are not logged.
- The `.ics` file is generated per request and returned to the browser.
