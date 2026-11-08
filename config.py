"""Central configuration: app constants, check-in options and secure settings loading.

The Groq API key is read from, in order:
  1. Environment variables (including a local ``.env`` file loaded by python-dotenv)
  2. Streamlit secrets (``.streamlit/secrets.toml`` or Streamlit Cloud secrets)

Nothing sensitive is hardcoded here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # no-op if there is no .env file

APP_NAME = "YourDOST AI Wellbeing Navigator"
APP_TAGLINE = "Find the right support, at the right time."

# ---------------------------------------------------------------------------
# Check-in options (exactly as specified in the product brief)
# ---------------------------------------------------------------------------
MOODS = ["Happy", "Calm", "Okay", "Stressed", "Anxious", "Overwhelmed", "Sad"]
MOOD_EMOJI = {
    "Happy": "😊",
    "Calm": "😌",
    "Okay": "🙂",
    "Stressed": "😣",
    "Anxious": "😟",
    "Overwhelmed": "😵",
    "Sad": "😔",
}

CONCERN_CATEGORIES = [
    "Work-related stress",
    "Anxiety and overthinking",
    "Sleep problems",
    "Relationship difficulties",
    "Family problems",
    "Financial stress",
    "Lack of motivation",
    "Personal challenges",
    "Other",
]

DURATIONS = ["Today", "A few days", "A few weeks", "Several months"]
IMPACT_LEVELS = ["Slightly", "Moderately", "Significantly"]

# ---------------------------------------------------------------------------
# Input limits
# ---------------------------------------------------------------------------
MIN_DESCRIPTION_CHARS = 15
MAX_DESCRIPTION_CHARS = 1500

# ---------------------------------------------------------------------------
# Safety / emergency information (India)
# ---------------------------------------------------------------------------
EMERGENCY_NUMBER_INDIA = "112"
# Verify helpline numbers before any production use; they can change.
HELPLINES_INDIA = [
    ("Emergency services (police / ambulance / fire)", "112"),
    ("Tele-MANAS (Govt. of India, 24x7 mental health support)", "14416"),
]

# ---------------------------------------------------------------------------
# Controlled vocabularies for AI output
# ---------------------------------------------------------------------------
URGENCY_LEVELS = ["low", "moderate", "high"]
COUNSELLING_LEVELS = ["optional", "consider", "recommended"]
RESOURCE_TYPES = ["Self-help", "Exercise", "Assessment", "Programme", "Counselling"]

# Groq's OpenAI-compatible API. llama-3.3-70b-versatile is enterprise-only and is
# not on the free-tier rate-limit table (checked against Groq's models and rate-limit
# docs, November 2026). openai/gpt-oss-120b is a supported free-tier text model.
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
_PLACEHOLDER_KEYS = {
    "your_groq_api_key",
    "your-groq-api-key",
    "your-openai-api-key-here",
    "your-api-key-here",
}


def _read_streamlit_secret(name: str) -> str | None:
    """Read a value from Streamlit secrets without failing if none are configured."""
    try:
        import streamlit as st

        value = st.secrets.get(name)  # raises if no secrets.toml exists
        return str(value) if value else None
    except Exception:  # noqa: BLE001 - missing secrets file / not running in Streamlit
        return None


def get_setting(name: str, default: str | None = None) -> str | None:
    """Return a setting from the environment, then Streamlit secrets, then default."""
    value = os.getenv(name)
    if value:
        return value.strip()
    secret = _read_streamlit_secret(name)
    if secret:
        return secret.strip()
    return default


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_float(value: str | None, default: float) -> float:
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default


def _as_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


def _usable_key(value: str | None) -> str | None:
    """Return a real key, or None for blanks and example placeholders."""
    if not value:
        return None
    cleaned = value.strip().strip('"').strip("'")
    if not cleaned or cleaned.lower() in _PLACEHOLDER_KEYS or cleaned.lower().startswith("your_"):
        return None
    return cleaned


@dataclass(frozen=True)
class Settings:
    """Runtime settings. ``api_key`` is never displayed or logged."""

    api_key: str | None
    model: str
    timeout_seconds: float
    max_retries: int
    use_moderation: bool
    force_offline: bool
    base_url: str = ""

    @property
    def ai_enabled(self) -> bool:
        return bool(self.api_key) and not self.force_offline

    def __repr__(self) -> str:  # never leak the key through repr/logging
        return (
            f"Settings(model={self.model!r}, ai_enabled={self.ai_enabled}, "
            f"timeout_seconds={self.timeout_seconds}, max_retries={self.max_retries})"
        )


def load_settings() -> Settings:
    """Load settings fresh (cheap), so changes to env/secrets are picked up on rerun."""
    return Settings(
        api_key=_usable_key(get_setting("GROQ_API_KEY")),
        model=get_setting("GROQ_MODEL", DEFAULT_GROQ_MODEL) or DEFAULT_GROQ_MODEL,
        timeout_seconds=_as_float(get_setting("GROQ_TIMEOUT_SECONDS"), 25.0),
        max_retries=_as_int(get_setting("GROQ_MAX_RETRIES"), 1),
        # Groq has no OpenAI moderation endpoint. The rule-based safety layer still runs first.
        use_moderation=_as_bool(get_setting("SAFETY_USE_MODERATION"), False),
        force_offline=_as_bool(get_setting("FORCE_OFFLINE_MODE"), False),
        base_url=get_setting("GROQ_BASE_URL", GROQ_BASE_URL) or GROQ_BASE_URL,
    )
