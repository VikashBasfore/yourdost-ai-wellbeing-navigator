"""YourDOST AI Wellbeing Navigator - Streamlit entry point.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import logging

import streamlit as st

from components.about import render_about
from components.common import (
    PAGE_ABOUT,
    PAGE_CHECKIN,
    PAGE_COUNSELLING,
    PAGE_HOME,
    PAGE_RECS,
    PAGES,
    apply_pending_navigation,
    clear_form_state,
    esc,
    init_state,
    inject_css,
    install_legacy_radio_fix,
    render_html,
    reset_checkin,
)
from components.counselling import render_counselling
from components.dashboard import render_dashboard
from components.recommendation_cards import render_recommendations
from components.wellbeing_checkin import render_checkin
from config import APP_NAME, EMERGENCY_NUMBER_INDIA, load_settings
from models import CheckinData
from services.pipeline import analyse_checkin

install_legacy_radio_fix()

# Privacy: log only operational events (never user messages).
logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_sidebar(settings) -> None:
    with st.sidebar:
        render_html('<div class="yd-sidebar-brand">🌿 YourDOST<br><span>AI Wellbeing Navigator</span></div>')
        st.write("")
        st.radio("Navigate", PAGES, key="nav", label_visibility="collapsed")
        st.divider()
        st.button("↺ Reset check-in", use_container_width=True, on_click=reset_checkin, key="sidebar_reset")
        st.divider()
        if settings.ai_enabled:
            render_html('<div class="yd-mode yd-mode-on">Groq AI is enabled</div>')
        else:
            render_html(
                '<div class="yd-mode yd-mode-off">Built-in guidance mode<br>Groq AI is offline</div>'
            )
        render_html(
            f"<p class='yd-muted'>🚨 In an emergency call <b>{esc(EMERGENCY_NUMBER_INDIA)}</b> (India). "
            "This app is not a medical or emergency service.</p>"
        )
        render_html("<p class='yd-muted'>🔒 No names or identifiers collected. Nothing is stored permanently.</p>")


def run_checkin_page(settings) -> None:
    def handle_submit(checkin: CheckinData) -> None:
        with st.spinner("Reflecting on your check-in… this usually takes a few seconds."):
            result = analyse_checkin(checkin, settings)
        st.session_state["analysis"] = result
        st.session_state["booking"] = None
        clear_form_state()  # the free-text description is not retained after analysis
        st.session_state["pending_nav"] = PAGE_RECS

    render_checkin(on_submit=handle_submit, ai_enabled=settings.ai_enabled)


def main() -> None:
    init_state()
    apply_pending_navigation()
    inject_css()
    settings = load_settings()
    render_sidebar(settings)

    page = st.session_state["nav"]
    result = st.session_state["analysis"]

    try:
        if page == PAGE_HOME:
            render_dashboard()
        elif page == PAGE_CHECKIN:
            run_checkin_page(settings)
        elif page == PAGE_RECS:
            render_recommendations(result)
        elif page == PAGE_COUNSELLING:
            render_counselling(result)
        elif page == PAGE_ABOUT:
            render_about(settings.ai_enabled, settings.model)
    except st.errors.StreamlitAPIException:
        raise
    except Exception as exc:  # noqa: BLE001 - show a friendly message, never raw details/content
        logging.getLogger(__name__).error("UI error (%s)", type(exc).__name__)
        st.error(
            "Something went wrong while showing this page. Please try again, or press Reset check-in. "
            f"If you are in immediate danger, please call {EMERGENCY_NUMBER_INDIA}."
        )


main()
