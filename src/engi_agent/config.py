"""Environment-backed runtime configuration."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    deepseek_api_key: str
    model: str = "deepseek-chat"
    temperature: float = 0.0
    max_retries: int = 2

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv(PROJECT_ROOT / ".env")
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key or api_key == "your_deepseek_api_key_here":
            raise ConfigurationError(
                "DEEPSEEK_API_KEY is missing. Add it to the local .env file."
            )

        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
        if model != "deepseek-chat":
            raise ConfigurationError(
                "This MVP requires DEEPSEEK_MODEL=deepseek-chat because tool "
                "calling is part of the core workflow."
            )

        return cls(deepseek_api_key=api_key, model=model)
