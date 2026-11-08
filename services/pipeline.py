"""End-to-end analysis pipeline: safety first, then AI, then safe fallback.

    check-in ──► safety layer ──crisis──► human-support result (no AI, no ordinary tips)
                      │ clear
                      ▼
                 AI analysis ──error──► built-in fallback guidance
"""

from __future__ import annotations

import logging

from config import Settings
from models import AnalysisResult, CheckinData
from services.ai_service import AIServiceError, analyse_with_ai
from services.recommendation_service import build_fallback_analysis
from services.safety_service import check_safety

logger = logging.getLogger(__name__)


def analyse_checkin(checkin: CheckinData, settings: Settings) -> AnalysisResult:
    """Analyse a check-in. Never raises; always returns a displayable result."""
    # 1. Independent safety layer runs BEFORE any recommendation is generated.
    safety = check_safety(checkin.description, settings)
    if safety.is_crisis:
        logger.info("Safety layer triggered (category=%s, source=%s)", safety.category, safety.source)
        return AnalysisResult(
            mode="crisis",
            safety_category=safety.category or "",
            mood=checkin.mood,
        )

    # 2. Ordinary AI analysis, with safe fallback.
    try:
        return analyse_with_ai(checkin, settings)
    except AIServiceError as exc:
        return build_fallback_analysis(checkin, reason=exc.user_reason)
    except Exception as exc:  # noqa: BLE001 - last-resort guard; never log content
        logger.warning("Unexpected pipeline error (%s)", type(exc).__name__)
        return build_fallback_analysis(checkin, reason="Something unexpected happened.")
