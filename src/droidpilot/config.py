from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-3.5-flash", alias="GEMINI_MODEL")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    provider: str = Field(default="gemini", alias="DROIDPILOT_PROVIDER")
    max_steps: int = Field(default=20, alias="DROIDPILOT_MAX_STEPS")
    screenshot_dir: str = Field(default="./screenshots", alias="DROIDPILOT_SCREENSHOT_DIR")
    device_id: str | None = Field(default=None, alias="DROIDPILOT_DEVICE_ID")
    confirmation_mode: bool = Field(default=True, alias="DROIDPILOT_CONFIRMATION_MODE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def is_llm_enabled(self) -> bool:
        return bool(self.google_api_key) and self.provider.lower() == "gemini"


settings = Settings()


def ensure_dirs() -> None:
    Path(settings.screenshot_dir).mkdir(parents=True, exist_ok=True)
