import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import Settings  # noqa: E402


@pytest.fixture
def ai_settings() -> Settings:
    return Settings(
        api_key="test-key-not-real",
        model="test-model",
        timeout_seconds=5,
        max_retries=0,
        use_moderation=False,
        force_offline=False,
    )


@pytest.fixture
def offline_settings() -> Settings:
    return Settings(
        api_key=None,
        model="test-model",
        timeout_seconds=5,
        max_retries=0,
        use_moderation=False,
        force_offline=False,
    )
