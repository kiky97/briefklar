# Deployment

BriefKlar has two parts:

1. **Web app** (FastAPI + one static HTML page, image `briefklar`). It makes no outbound requests: no CDN scripts or web fonts, and Swagger docs are off by default.
2. **Apertus inference**, reached over an OpenAI-compatible API at `LLM_BASE_URL`, with model `LLM_NAME` and key `LLM_API_KEY`.

Because inference is just a URL, the same code runs in all three Track 2B architectures. Only where Apertus is served changes.

| Architecture | Web app runs on | Apertus served by | Command |
|---|---|---|---|
| a) On-premise | the organisation's server | vLLM on the same host (local weights) | `make run-local` |
| b) Air-gapped | an isolated host | vLLM with local weights, offline flags set | `make run-local` after offline preparation |
| c) Sovereign Swiss cloud | a container on a Swiss-operated cloud | a Swiss-hosted Apertus endpoint, or vLLM on a GPU VM in the same cloud | `make run` or `make run-local` |

## Build time vs. runtime dependencies

| | Build time (once, needs internet) | Runtime |
|---|---|---|
| Python packages | PyPI (or pre-downloaded wheels) | none |
| Container images | `python:3.11-slim`, `vllm/vllm-openai` | none |
| Model weights | Hugging Face `swiss-ai/Apertus-v1.5-8B` or `-70B` | local files only |
| Network | | only `LLM_BASE_URL`; on-premise and air-gapped, that is the local vLLM container |

## a) On-premise

Requirements: Linux host with Docker and the NVIDIA container toolkit. Apertus v1.5 8B needs a GPU with about 24 GB VRAM (bf16). 70B needs multiple GPUs or quantization.

```bash
# 1. Get the weights (needs internet once)
pip install -U "huggingface_hub[cli]"
huggingface-cli download swiss-ai/Apertus-v1.5-8B --local-dir models/apertus

# 2. Start the app + local vLLM
make run-local
# 3. Open http://<host>:8000
```

## b) Air-gapped

Prepare everything on a connected machine, then transfer it:

```bash
# Python dependencies as wheels (for the target platform)
pip download -r src/requirements.txt -d src/wheels

# Model weights
huggingface-cli download swiss-ai/Apertus-v1.5-8B --local-dir models/apertus

# Container images
docker compose build --build-arg PIP_ARGS="--no-index --find-links=wheels" app
docker pull vllm/vllm-openai:latest
docker save briefklar:latest vllm/vllm-openai:latest -o images.tar
```

Copy the project folder (with `models/`) and `images.tar` to the isolated host, then:

```bash
docker load -i images.tar
make run-local
```

At runtime nothing leaves the host:
- vLLM runs with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and usage stats disabled.
- The web page loads no external resources. A unit test checks this (`test_no_external_assets`).
- Date and amount checks, PDF reading and calendar export all run locally.

Verify by running the stack with the network unplugged.

## c) Sovereign Swiss cloud

Deploy the same compose file on a GPU VM from a cloud provider that is operated in Switzerland, under Swiss jurisdiction, with Swiss data residency (`make run-local`). Alternatively, run only the app there (`make run`) and point `LLM_BASE_URL` at a Swiss-hosted Apertus endpoint.

For the submission, document for the chosen provider:
- the legal entity operating the service and its jurisdiction
- the data-centre location(s)
- the retention and logging policy for prompts and responses

## Data handling

- The app stores no letters. Requests are processed in memory and never written to disk. Uvicorn access logs record only paths, not request bodies.
- Check the request-logging settings of the vLLM version you pin, so prompts are not logged.
- The `.ics` file is generated per request and returned to the browser.
