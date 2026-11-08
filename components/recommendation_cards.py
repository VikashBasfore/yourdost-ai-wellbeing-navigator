"""Personalised recommendation page and the safety (crisis) support view."""

from __future__ import annotations

import streamlit as st

from components.common import (
    PAGE_CHECKIN,
    PAGE_COUNSELLING,
    card,
    chip,
    esc,
    go_to,
    numbered_steps,
    render_emergency_box,
    render_html,
    reset_checkin,
)
from config import MOOD_EMOJI
from models import AnalysisResult
from services.recommendation_service import get_exercises
from services.safety_service import HARM_TO_OTHERS, IMMEDIATE_DANGER

_TYPE_ICON = {
    "Self-help": "📚",
    "Exercise": "🧘",
    "Assessment": "📋",
    "Programme": "🌱",
    "Counselling": "💬",
}
_PRIORITY_LABEL = {
    "low": ("Self-help may be enough for now", ""),
    "moderate": ("Worth considering talking to someone", "warn"),
    "high": ("Talking to someone soon would help", "high"),
}
_COUNSELLING_HEADLINE = {
    "optional": "Counselling is available if you'd like it",
    "consider": "Speaking with a counsellor could help",
    "recommended": "We encourage you to speak with a professional counsellor",
}

_CRISIS_INTRO = {
    "self_harm": (
        "Thank you for sharing something so difficult. What you wrote suggests you may be in a lot of "
        "pain right now, and you deserve care and support from a real person. You don't have to go "
        "through this alone."
    ),
    HARM_TO_OTHERS: (
        "Thank you for being honest. What you wrote suggests you may be feeling intense distress or "
        "anger right now. It can help to step away from the situation and talk to a person who can "
        "support you, before anyone gets hurt."
    ),
    IMMEDIATE_DANGER: (
        "Thank you for telling us. What you wrote suggests you may not feel safe right now, and your "
        "safety matters most."
    ),
}


def render_crisis_support(result: AnalysisResult) -> None:
    """Human-support view. Deliberately shows NO ordinary self-help recommendations."""
    intro = _CRISIS_INTRO.get(result.safety_category, _CRISIS_INTRO["self_harm"])
    st.markdown("## We're here for you 💙")
    render_html(card(f'<p class="yd-crisis-intro">{esc(intro)}</p>', "soft-blue"))

    render_emergency_box("Please reach out for help right now")

    render_html(
        card(
            "<h4>What you can do right now</h4>"
            + numbered_steps(
                [
                    "If you or someone else is in immediate danger, call 112 (India) or go to the nearest hospital.",
                    "Contact a person you trust (a friend, family member or colleague) and ask them to stay with you or "
                    "be on a call with you.",
                    "Reach out to a qualified mental health professional or a helpline, such as Tele-MANAS (14416), who "
                    "can talk with you right away.",
                    "If you can, move away from anything you could use to hurt yourself or others.",
                ]
            ),
            "accent-teal",
        )
    )
    render_html(
        card(
            "<p>We haven't generated routine self-help tips because speaking with a person matters more right now. "
            "This is <b>not an assessment</b> of your situation or a diagnosis. We simply want you to have "
            "human support. This tool can't replace emergency services or qualified professionals.</p>",
            "disclaimer",
        )
    )

    c1, c2, _ = st.columns([1.4, 1.2, 2])
    c1.button(
        "Explore professional counselling",
        type="primary",
        use_container_width=True,
        on_click=go_to,
        args=(PAGE_COUNSELLING,),
        key="crisis_counselling",
    )
    c2.button(
        "Start over",
        use_container_width=True,
        on_click=reset_checkin,
        key="crisis_reset",
    )


def _resource_html(title: str, rtype: str, desc: str) -> str:
    icon = _TYPE_ICON.get(rtype, "📚")
    return (
        f'<div class="yd-resource"><div class="title"><span>{icon} {esc(title)}</span>'
        f'<span class="yd-chip teal">{esc(rtype)}</span></div>'
        f'<div class="desc">{esc(desc)}</div></div>'
    )


def render_recommendations(result: AnalysisResult | None) -> None:
    if result is not None and result.mode == "crisis":
        render_crisis_support(result)
        return

    heading = (
        "Your recommended next steps"
        if result is not None and result.mode == "fallback"
        else "Your personalised recommendations"
    )
    st.markdown(f"## {heading}")

    if result is None:
        render_html(
            card(
                "<h4>No check-in yet</h4><p>Complete a short wellbeing check-in and your personalised "
                "summary and recommendations will appear here.</p>",
                "soft-blue",
            )
        )
        st.button(
            "Start Wellbeing Check-in",
            type="primary",
            on_click=go_to,
            args=(PAGE_CHECKIN,),
            key="recs_start",
        )
        return

    # --- Overview chips -------------------------------------------------------
    priority_text, priority_variant = _PRIORITY_LABEL.get(result.urgency_level, _PRIORITY_LABEL["moderate"])
    chips_html = (
        chip(f"Topic: {result.concern_category}")
        + chip(f"{MOOD_EMOJI.get(result.mood, '')} Feeling {result.mood.lower()}", "teal")
        + chip(f"Duration: {result.duration}", "teal")
        + chip(f"Impact: {result.impact}", "teal")
        + chip(priority_text, priority_variant)
    )
    render_html(f'<div class="yd-chips">{chips_html}</div>')

    if result.mode == "fallback":
        detail = result.fallback_reason or "AI analysis is not available."
        st.info(
            f"Built-in guidance is active. {detail} These next steps are general and were not "
            "written by AI from your own words.",
            icon="ℹ️",
        )

    if result.urgency_level == "high":
        render_html(
            card(
                "<h4>💙 Talking to someone soon could really help</h4>"
                "<p>Based on how long this has been going on and how much it's affecting you, we'd gently "
                "encourage you to speak with a professional counsellor or someone you trust. If at any point "
                "you feel unsafe, please call <b>112</b> (India).</p>",
                "soft-teal",
            )
        )

    # --- Summary + supportive message ----------------------------------------------
    left, right = st.columns([1.35, 1])
    with left:
        render_html(
            card(
                f"<h4>🔎 What we understood</h4><p>{esc(result.concern_summary)}</p>",
                "accent-blue",
            )
        )
    with right:
        render_html(
            card(
                f'<h4>💬 A note for you</h4><p class="yd-quote">{esc(result.supportive_message)}</p>',
                "soft-teal",
            )
        )

    # --- Resources + next steps ---------------------------------------------------------
    col_res, col_steps = st.columns(2)
    with col_res:
        body = "".join(_resource_html(r.title, r.type, r.description) for r in result.recommended_resources)
        render_html(card(f"<h4>📚 Recommended resources</h4>{body}"))
    with col_steps:
        render_html(card("<h4>✅ Practical next steps</h4>" + numbered_steps(result.practical_next_steps)))

    # --- Smart recommendations (curated, always shown) ----------------------------------
    st.markdown("### Try it now")
    st.caption("Short, curated exercises matched to your topic. Tap to expand.")
    for exercise in get_exercises(result.concern_category):
        with st.expander(f"🧘 {exercise.title}  ·  {exercise.duration}"):
            st.write(exercise.why)
            for i, step in enumerate(exercise.steps, start=1):
                st.markdown(f"{i}. {step}")

    # --- Counselling ---------------------------------------------------------------------
    headline = _COUNSELLING_HEADLINE.get(result.counselling_level, _COUNSELLING_HEADLINE["consider"])
    render_html(
        card(
            '<p class="yd-kicker">Professional support</p>'
            "<h3>Would you like to speak with a professional?</h3>"
            f'<p class="yd-counsel-line">{esc(headline)}.</p>'
            f"<p>{esc(result.counselling_reason)}</p>",
            "counsel",
        )
    )
    c1, c2 = st.columns([2, 1])
    c1.button(
        "Explore counselling support",
        type="primary",
        use_container_width=True,
        on_click=go_to,
        args=(PAGE_COUNSELLING,),
        key="recs_counselling",
    )
    c2.button(
        "↺ Reset check-in",
        use_container_width=True,
        on_click=reset_checkin,
        key="recs_reset",
    )

    source = "AI-assisted" if result.mode == "ai" else "built-in"
    render_html(
        card(
            f"<p class='yd-small'><b>Please note:</b> these {source} recommendations are informational "
            "only. They are not medical or psychological advice or a diagnosis, and don't replace a "
            "qualified professional. If you ever feel unsafe, call <b>112</b> (India) or contact someone "
            "you trust.</p>",
            "disclaimer",
        )
    )
