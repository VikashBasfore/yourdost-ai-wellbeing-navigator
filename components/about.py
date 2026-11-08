"""About and privacy pages."""

from __future__ import annotations

import streamlit as st

from components.common import card, render_emergency_box, render_html
from config import APP_NAME


def render_about(ai_enabled: bool, model: str) -> None:
    st.markdown("## About & Privacy")

    tab_about, tab_privacy, tab_safety = st.tabs(["About", "How your information is handled", "Safety"])

    with tab_about:
        render_html(
            card(
                f"<h4>🌿 {APP_NAME}</h4>"
                "<p>This prototype helps employees understand what they're experiencing and discover the most "
                "relevant YourDOST support &ndash; self-help, assessments, programmes or counselling &ndash; "
                "so the next step is clearer.</p>",
                "accent-teal",
            )
        )
        st.markdown(
            "**How it works**\n"
            "1. You complete a short check-in.\n"
            "2. An independent safety layer screens your message for signs you may need urgent human help.\n"
            "3. If clear, an AI model summarises your concern and suggests resources and steps. "
            "If the AI is unavailable, built-in guidance is shown instead.\n"
            "4. You can explore counselling options (booking here is simulated)."
        )
        st.markdown("**This tool is not**: a diagnosis, a clinical assessment, medical advice or an emergency service.")
        status = (
            f"Groq AI: **enabled** (model: `{model}`)"
            if ai_enabled
            else "Groq AI: **offline**, so built-in guidance is used."
        )
        st.caption(status)

    with tab_privacy:
        render_html(
            card(
                "<h4>🔒 Your information</h4>"
                "<ul>"
                "<li><b>No identifiers:</b> we don't ask for your name, phone number, email or employee ID, and the "
                "check-in blocks obvious contact details.</li>"
                "<li><b>No permanent storage in this app:</b> answers stay in this browser session and are "
                "cleared when you press <i>Reset check-in</i> or close the tab.</li>"
                "<li><b>Your written description:</b> after results are shown, this app deletes that text from the "
                "session. It is not saved to a database and it is not written to logs.</li>"
                "<li><b>When Groq AI is enabled:</b> your check-in is sent to Groq for processing. That includes how "
                "you feel, the concern you chose, how long it has lasted, how much it affects daily life, and the "
                "description you typed. It is used only to create your recommendations. This app does not keep the "
                "description afterwards. How long Groq retains a request depends on your Groq account settings, "
                "which this prototype does not control. Use fictional, synthetic details when trying the prototype.</li>"
                "<li><b>When Groq AI is offline:</b> nothing is sent to Groq. Built-in guidance uses the options "
                "you selected. The description is still removed from the session after results appear.</li>"
                "<li><b>No sensitive logging:</b> the app does not write your messages to logs.</li>"
                "<li><b>Credentials:</b> API keys are read from environment variables or Streamlit secrets and are "
                "never shown in the app.</li>"
                "<li><b>Demo data:</b> use fictional information when trying this prototype.</li>"
                "</ul>",
                "accent-blue",
            )
        )

    with tab_safety:
        st.markdown(
            "- A separate safety layer runs **before** any AI recommendation.\n"
            "- If your message suggests possible immediate danger, self-harm or harm to others, you'll see "
            "human-support guidance instead of ordinary tips.\n"
            "- The safety layer does **not** diagnose or judge risk. It simply points you to people who can help.\n"
            "- Automated screening can miss things. If you're worried about your safety, please don't rely on this app."
        )
        render_emergency_box()
