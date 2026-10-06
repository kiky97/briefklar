"""List the models your endpoint serves, to find the exact Apertus model id."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI  # noqa: E402

from app.config import get_settings  # noqa: E402

s = get_settings()
if not s.api_key:
    sys.exit("Set LLM_API_KEY (environment or .env) first.")
client = OpenAI(base_url=s.base_url, api_key=s.api_key, default_headers={"User-Agent": "apertus-letter-helper/0.1"})
ids = sorted(m.id for m in client.models.list().data)
for mid in ids:
    print(("* " if "apertus" in mid.lower() else "  ") + mid)
print(f"\nConfigured LLM_NAME={s.model} -> {'found' if s.model in ids else 'NOT FOUND, update .env'}")
