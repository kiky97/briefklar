FROM python:3.11-slim

WORKDIR /srv
# For air-gapped installs, pre-download wheels with
#   pip download -r requirements.txt -d wheels
# and build with: docker compose build --build-arg PIP_ARGS="--no-index --find-links=wheels"
ARG PIP_ARGS=""
COPY requirements.txt .
COPY wheels ./wheels
RUN pip install --no-cache-dir $PIP_ARGS -r requirements.txt

COPY pytest.ini ./
COPY app ./app
COPY eval ./eval
COPY scripts ./scripts
COPY tests ./tests
ENV PYTHONUNBUFFERED=1 DATA_DIR=/data
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
