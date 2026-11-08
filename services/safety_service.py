"""Independent safety-checking layer.

This module runs BEFORE any AI recommendation is generated and does not depend on
the AI model. It is deliberately conservative: it only detects *language that suggests
possible immediate danger* and routes the user to human support. It does NOT diagnose
or assess clinical risk, and a "no match" result is never a statement that a person is
safe.

Privacy: matched text is never stored, returned or logged - only a coarse category.

Layers:
  1. Rule-based phrase/regex screening (always on, offline, deterministic).
  2. Optional OpenAI moderation check (self-harm categories only). It fails open: if the
     API is unavailable the rule-based result stands.

Design note: common workplace idioms ("my boss will kill me", "this workload is killing
me") are intentionally NOT treated as crisis language, otherwise ordinary work-stress
check-ins would be misrouted. Everything else errs on the side of showing human support.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass

from config import Settings

logger = logging.getLogger(__name__)

SELF_HARM = "self_harm"
HARM_TO_OTHERS = "harm_to_others"
IMMEDIATE_DANGER = "immediate_danger"

_PEOPLE = (
    r"(him|her|them|someone|somebody|everyone|everybody|people|others|"
    r"my (boss|manager|colleague|coworker|co-worker|team|wife|husband|partner|"
    r"spouse|ex|kids?|children|child|parents?|mother|father|mom|dad|family|brother|sister))"
)
# Skip matches that are negated, e.g. "I don't want to hurt my parents".
_NOT_NEGATED = r"(?<!n't )(?<!not )(?<!never )(?<!dont )"
_INTENT = r"(want to|wanna|going to|gonna|plan(ning)? to|ready to|about to|urge to|feel like|thinking (of|about))"

_RULES: dict[str, list[str]] = {
    SELF_HARM: [
        r"\bsuicid\w*",
        r"\bunaliv\w*",
        r"\bkill(ing)? my ?self\b",
        r"\bend(ing)? (my (own )?life|it all|my existence)\b",
        r"\btake my (own )?life\b",
        r"\b(want|wanted|wanna|need|wish)(ed|s)? (to )?(just )?(die|be dead)\b",
        r"\bfeel(ing)? like (dying|i should die|ending it)\b",
        r"\bwish (i|that i) (was|were|could be) (dead|gone|never born)\b",
        r"\bwish (i|that i) (could )?(just )?(die|disappear forever|not wake up|never wake up)\b",
        r"\b(don'?t|do not|dont|no longer|never) (want|wanna|wish) to (live|be alive|exist|be here anymore)\b",
        r"\b(don'?t|do not|dont) want to go on\b(?! (a|an|the|my|this|that|leave|vacation|holiday|trips?)\b)",
        r"\bbetter off (dead|without me)\b",
        r"\beveryone would be better off\b",
        r"\b(hurt|harm|cut|cutting|injure|injuring|punish) my ?self\b",
        r"\bself[- ]?(harm|injur|mutilat)\w*",
        r"\bno (reason|point) (in |to )?(living|live|going on|go on|being alive)\b",
        r"\b(life (isn'?t|is not) worth (living|it)|not worth living)\b",
        r"\b(hang|drown|shoot|poison|stab) my ?self\b",
        r"\b(slit|slash|cut) my (wrist|wrists|throat)\b",
        r"\bjump (off|from) (a |the |my )?(bridge|building|roof|balcony|terrace|cliff|train)\b",
        r"\boverdos\w*",
        r"\btake (all )?my (pills|tablets|medication|meds)\b",
        r"\bkms\b",
        # Common Hinglish phrasings
        r"\b(marna|mar jana|mar jaana) (chahta|chahti|chahte)\b",
        r"\bjeena nahi (chahta|chahti|chahte)\b",
        r"\bjeene ka mann nahi\b",
        r"\b(khudkushi|khud ?kushi|aatmahatya|atmahatya)\b",
        r"\bkhud ko (khatam|maar)\b",
    ],
    HARM_TO_OTHERS: [
        rf"\b(kill|murder|stab|poison|strangle)(ing)? {_PEOPLE}\b",
        rf"\bshoot(ing)? {_PEOPLE}\b(?! (an?|some|the|over|off)\b)",
        rf"{_NOT_NEGATED}\b{_INTENT} (hurt|harm|attack|beat up|assault|kill|murder|stab)\w* {_PEOPLE}\b",
        rf"{_NOT_NEGATED}\b{_INTENT} shoot\w* {_PEOPLE}\b(?! (an?|some|the|over|off)\b)",
        rf"{_NOT_NEGATED}\b(want to|wanna|going to|gonna|plan(ning)? to|ready to) (kill|murder|stab) (?!it\b|time\b|the\b|this\b|that\b|my ?self\b|my (day|presentation|interview|goals?)\b)",
        r"\bhomicid\w*",
        r"\b(bring|take|carry) (a )?(gun|knife|weapon) to (the )?(office|work|school|college|class|meeting)\b",
    ],
    IMMEDIATE_DANGER: [
        r"\b(i am|i'?m|im|we are|we'?re) (currently |right now )?(in|facing) (immediate |serious |real |great )?danger\b",
        r"\b(i am|i'?m|im) not safe\b",
        r"\bnot safe (at home|right now|here|anymore)\b",
        r"\bi (feel|am feeling) (unsafe|in danger)\b",
        r"\b(he|she|they|someone) (is|are|will|keeps|keep|is going to|are going to|wants to|threatens? to|threatened to) (hit|hitting|beat|beating|hurt|hurting|attack|attacking|rape|assault|assaulting) me\b",
        r"\b(he|she|they|someone) (threatens?|threatened) to kill me\b",
        r"\bi'?m being (abused|attacked|threatened|beaten|stalked|assaulted)\b",
        r"\b(about to|going to|gonna) (hurt|harm|kill|end) (myself|my life|it all)\b",
    ],
}

_COMPILED: dict[str, list[re.Pattern[str]]] = {
    category: [re.compile(p, re.IGNORECASE) for p in patterns]
    for category, patterns in _RULES.items()
}

# OpenAI moderation categories treated as self-harm signals.
_MODERATION_SELF_HARM_CATEGORIES = ("self-harm", "self-harm/intent", "self-harm/instructions")


@dataclass(frozen=True)
class SafetyResult:
    """Outcome of the safety screen. Intentionally holds no user text."""

    is_crisis: bool
    category: str | None = None
    source: str | None = None  # "rules" or "moderation"


def _normalise(text: str) -> str:
    """Lower-case, fold unicode look-alikes, drop invisible chars, normalise spacing."""
    text = unicodedata.normalize("NFKC", text)
    text = "".join(
        ch for ch in text if unicodedata.category(ch) not in {"Cf", "Cc"} or ch in "\n\t "
    )
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("`", "'")
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def check_text_rules(text: str) -> SafetyResult:
    """Rule-based screening. Deterministic, offline, no side effects."""
    if not text or not text.strip():
        return SafetyResult(is_crisis=False)

    normalised = _normalise(text)
    # All categories lead to the same human-support flow; the category only changes the
    # wording of the message. Priority: self-harm > harm to others > immediate danger.
    for category in (SELF_HARM, HARM_TO_OTHERS, IMMEDIATE_DANGER):
        for pattern in _COMPILED[category]:
            if pattern.search(normalised):
                return SafetyResult(is_crisis=True, category=category, source="rules")
    return SafetyResult(is_crisis=False)


def check_moderation(text: str, settings: Settings) -> SafetyResult:
    """Optional second layer using OpenAI moderation (self-harm categories only).

    Fails open: any error returns a non-crisis result so the rule-based layer remains
    the guaranteed baseline. Only the exception *type* is logged.
    """
    if not (settings.ai_enabled and settings.use_moderation):
        return SafetyResult(is_crisis=False)
    # Groq does not provide OpenAI's moderation endpoint. The rule-based layer above
    # is the safety check for Groq. Do not send the description to another provider.
    if "groq.com" in (settings.base_url or ""):
        return SafetyResult(is_crisis=False)
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.api_key,
            timeout=min(settings.timeout_seconds, 10.0),
            max_retries=0,
        )
        response = client.moderations.create(model="omni-moderation-latest", input=text)
        categories = response.results[0].categories
        for name in _MODERATION_SELF_HARM_CATEGORIES:
            attr = name.replace("/", "_").replace("-", "_")
            if getattr(categories, attr, False):
                return SafetyResult(is_crisis=True, category=SELF_HARM, source="moderation")
    except Exception as exc:  # noqa: BLE001 - fail open, never log content
        logger.warning("Moderation check unavailable (%s)", type(exc).__name__)
    return SafetyResult(is_crisis=False)


def check_safety(text: str, settings: Settings | None = None) -> SafetyResult:
    """Run all safety layers. Rules first; moderation only if rules found nothing."""
    result = check_text_rules(text)
    if result.is_crisis:
        return result
    if settings is not None:
        return check_moderation(text, settings)
    return result
