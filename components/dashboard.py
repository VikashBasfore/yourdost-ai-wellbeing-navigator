"""Welcome dashboard."""

from __future__ import annotations

import streamlit as st

from components.common import PAGE_ABOUT, PAGE_CHECKIN, card, go_to, render_html
from config import APP_NAME


def render_dashboard() -> None:
    render_html(
        f"""
        <div class="yd-hero">
          <div class="yd-eyebrow">YourDOST &middot; Employee wellbeing</div>
          <h1>🌿 {APP_NAME}</h1>
          <p>Welcome. Not sure which kind of support is right for you right now? Take a short,
          confidential check-in and we'll help you understand what you're experiencing and
          suggest gentle, practical next steps.</p>
        </div>
        """
    )

    cta_col, link_col, _ = st.columns([1.3, 1.1, 2])
    cta_col.button(
        "Start Wellbeing Check-in",
        type="primary",
        use_container_width=True,
        on_click=go_to,
        args=(PAGE_CHECKIN,),
        key="home_start",
    )
    link_col.button(
        "How my data is handled",
        use_container_width=True,
        on_click=go_to,
        args=(PAGE_ABOUT,),
        key="home_privacy",
    )

    st.markdown("### How it works")
    cols = st.columns(4)
    steps = [
        ("1", "Check in", "Tell us how you feel and what's on your mind in about 2 minutes."),
        ("2", "Safety first", "A separate safety check looks for signs you may need urgent human help."),
        ("3", "Personal insight", "AI summarises your concern in plain language, without labels or diagnoses."),
        ("4", "Next steps", "Get self-help exercises, practical steps and counselling options."),
    ]
    for col, (num, title, text) in zip(cols, steps):
        with col:
            render_html(
                card(
                    f'<div class="yd-chip teal">Step {num}</div><h4>{title}</h4><p>{text}</p>',
                    "accent-teal",
                )
            )

    st.markdown("### Support available through YourDOST")
    cols = st.columns(4)
    offerings = [
        ("💬", "Online counselling", "Confidential conversations with trained professionals."),
        ("📚", "Self-help resources", "Exercises and guides you can use any time."),
        ("📋", "Wellbeing assessments", "Reflect on how you're doing with short assessments."),
        ("🌱", "Wellbeing programmes", "Guided programmes to build healthy habits."),
    ]
    for col, (icon, title, text) in zip(cols, offerings):
        with col:
            render_html(card(f'<div class="big">{icon}</div><h4>{title}</h4><p>{text}</p>', "soft-blue"))

    render_html(
        card(
            "<h4>🔐 Privacy &amp; safety</h4>"
            "<p><b>This is a wellbeing guide, not a medical service.</b> It doesn't diagnose, treat or replace a "
            "qualified counsellor, doctor or emergency services.</p>"
            "<p>We don't ask for your name, phone number or other identifiers. Your check-in stays in "
            "this browser session only, and the description you type is removed after your results appear. "
            "Please don't enter personal identifiers.</p>"
            "<p>When Groq AI is turned on, that same check-in (including what you type) is sent to "
            "Groq to create your summary. This app does not keep a copy. Use fictional details in this prototype.</p>"
            "<p><b>In an emergency, call 112 (India).</b> If you're worried about your safety or someone "
            "else's, please contact local emergency services or someone you trust right away.</p>"
            "<p class='yd-muted'>This prototype uses fictional, synthetic data for demonstration.</p>",
            "disclaimer",
        )
    )
