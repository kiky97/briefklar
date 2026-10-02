import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


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
    """Read settings from the environment on every call so tests and scripts can override them."""
    return Settings(
        base_url=os.getenv("APERTUS_BASE_URL", "https://api.publicai.co/v1"),
        api_key=os.getenv("APERTUS_API_KEY", ""),
        model=os.getenv("APERTUS_MODEL", "swiss-ai/apertus-v1.5-8b"),
        mock=_flag("MOCK_LLM"),
        temperature=float(os.getenv("APERTUS_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("APERTUS_MAX_TOKENS", "1500")),
    )
