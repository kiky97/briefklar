import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# Hack Apertus endpoint used during development; judges override via LLM_* env vars.
DEFAULT_BASE_URL = "https://hackapertus.livemap.sh/v1"
DEFAULT_MODEL = "apertus-v1.5-70b"


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str
    model: str
    mock: bool
    temperature: float
    max_tokens: int


def _flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def get_settings() -> Settings:
    """Read settings from the environment on every call so tests and scripts can override them.

    Variable names follow the Hack Apertus template: LLM_NAME, LLM_BASE_URL, LLM_API_KEY.
    """
    return Settings(
        base_url=os.getenv("LLM_BASE_URL") or DEFAULT_BASE_URL,
        api_key=os.getenv("LLM_API_KEY", ""),
        model=os.getenv("LLM_NAME") or DEFAULT_MODEL,
        mock=_flag("MOCK_LLM"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1500")),
    )
