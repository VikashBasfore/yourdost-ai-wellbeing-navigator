"""Wellbeing check-in form with input validation."""

from __future__ import annotations

import re
from collections.abc import Callable

import streamlit as st

from components.common import render_html, reset_checkin, stage_checkin_values
from components.demo_scenarios import SCENARIOS
from config import (
    CONCERN_CATEGORIES,
    DURATIONS,
    IMPACT_LEVELS,
    MAX_DESCRIPTION_CHARS,
    MIN_DESCRIPTION_CHARS,
    MOOD_EMOJI,
    MOODS,
)
from models import CheckinData

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"(?<!\d)(\+?\d[\d\s\-()]{8,}\d)(?!\d)")


def validate_checkin(
    mood: str | None,
    concern: str | None,
    duration: str | None,
    impact: str | None,
    description: str | None,
) -> list[str]:
    """Return a list of user-friendly validation errors (empty if valid)."""
    errors: list[str] = []
    if not mood:
        errors.append("Please choose how you are feeling today.")
    if not concern:
        errors.append("Please choose what is bothering you the most.")
    if not duration:
        errors.append("Please tell us how long you have been experiencing this.")
    if not impact:
        errors.append("Please tell us how much this is affecting your daily life.")

    text = (description or "").strip()
    if len(text) < MIN_DESCRIPTION_CHARS:
        errors.append(
            f"Please describe what you are experiencing (at least {MIN_DESCRIPTION_CHARS} characters)."
        )
    elif len(text) > MAX_DESCRIPTION_CHARS:
        errors.append(f"Please keep your description under {MAX_DESCRIPTION_CHARS} characters.")
    if _EMAIL_RE.search(text) or _PHONE_RE.search(text):
        errors.append(
            "Your description seems to contain an email address or phone number. "
            "For your privacy, please remove personal identifiers and try again."
        )
    return errors


def _key(name: str) -> str:
    return f"{name}_{st.session_state.get('form_version', 0)}"


def _format_mood(mood: str) -> str:
    """Display label for a mood option. The radio value itself stays the raw mood."""
    return f"{MOOD_EMOJI[mood]} {mood}"


def _load_sample(scenario_key: str) -> None:
    """Callback: pre-fill a new form with a fictional scenario.

    The new form's radios do not exist yet, so their session values are the
    option strings (not display labels or indexes).
    """
    sample = SCENARIOS[scenario_key]
    stage_checkin_values({**sample, "sample_choice": scenario_key})


def _handle_submit(on_submit: Callable[[CheckinData], None]) -> None:
    """Form-submit callback. Runs before the next script pass, so the page that follows
    (results or the form with errors) renders cleanly without a mid-script rerun."""
    values = {name: st.session_state.get(_key(name)) for name in ("mood", "concern", "duration", "impact", "description")}
    errors = validate_checkin(**values)
    if errors:
        st.session_state["checkin_errors"] = errors
        return
    on_submit(
        CheckinData(
            mood=values["mood"],
            concern_category=values["concern"],
            duration=values["duration"],
            impact=values["impact"],
            description=(values["description"] or "").strip(),
        )
    )


def render_checkin(on_submit: Callable[[CheckinData], None], *, ai_enabled: bool = False) -> None:
    """Render the form. ``on_submit`` is called with validated ``CheckinData`` on submit."""
    st.markdown("## Wellbeing check-in")
    st.write("Take your time. There are no right or wrong answers, and you can skip anything you're not comfortable sharing.")
    if ai_enabled:
        notice = (
            "Please don't include names, phone numbers or other personal identifiers. "
            "When you submit, this check-in is sent to Groq to create your recommendations. "
            "This app removes your description after the results are shown and does not keep a copy."
        )
    else:
        notice = (
            "Please don't include names, phone numbers or other personal identifiers. "
            "Groq AI is offline, so this check-in is not sent to Groq. "
            "This app removes your description after the results are shown."
        )
    render_html(f'<p class="yd-muted">🔒 {notice}</p>')

    with st.expander("🧪 Demo: load a fictional sample scenario"):
        st.caption("All samples are fictional and for demonstration only.")
        choice = st.selectbox("Sample scenario", list(SCENARIOS), key=_key("sample_choice"))
        st.button("Load sample into form", on_click=_load_sample, args=(choice,), key=_key("load_sample"))

    with st.form(key=f"checkin_form_{st.session_state.get('form_version', 0)}"):
        st.radio(
            "1. How are you feeling today?",
            MOODS,
            index=None,
            horizontal=True,
            format_func=_format_mood,
            key=_key("mood"),
        )
        st.selectbox(
            "2. What is bothering you the most?",
            CONCERN_CATEGORIES,
            index=None,
            placeholder="Choose one...",
            key=_key("concern"),
        )
        st.radio(
            "3. How long have you been experiencing this?",
            DURATIONS,
            index=None,
            horizontal=True,
            key=_key("duration"),
        )
        st.radio(
            "4. How much is this affecting your daily life?",
            IMPACT_LEVELS,
            index=None,
            horizontal=True,
            key=_key("impact"),
        )
        st.text_area(
            "5. Describe what you are experiencing.",
            height=160,
            max_chars=MAX_DESCRIPTION_CHARS,
            placeholder="In your own words, what's been happening and how it's affecting you? "
            "(Please avoid names or contact details.)",
            key=_key("description"),
        )
        st.form_submit_button(
            "Submit check-in", type="primary", on_click=_handle_submit, args=(on_submit,)
        )

    for message in st.session_state.pop("checkin_errors", None) or []:
        st.error(message, icon="⚠️")

    st.button("↺ Reset check-in", on_click=reset_checkin, kwargs={"navigate": True}, key="reset_on_checkin")
