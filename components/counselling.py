"""Counselling support section. All booking actions are clearly simulated."""

from __future__ import annotations

import streamlit as st

from components.common import card, chip, esc, render_emergency_box, render_html
from config import CONCERN_CATEGORIES
from models import AnalysisResult

VIEW_EXPLORE = "explore"
VIEW_BOOK = "book"
VIEW_LEARN = "learn"


def _set_view(view: str) -> None:
    st.session_state["counselling_view"] = view


def _clear_booking() -> None:
    st.session_state["booking"] = None


def _render_explore() -> None:
    st.markdown("### Explore counselling support")
    c1, c2 = st.columns(2)
    with c1:
        render_html(
            card(
                "<h4>💬 What is counselling?</h4>"
                "<p>Counselling is a confidential, supportive conversation with a trained professional. "
                "It gives you space to talk through what's on your mind and to build practical ways of coping "
                "&ndash; without judgement.</p>",
                "accent-teal",
            )
        )
        render_html(
            card(
                "<h4>🧭 Concerns people talk about</h4>"
                "<p>Work stress &middot; Anxiety and overthinking &middot; Sleep difficulties &middot; "
                "Relationship and family issues &middot; Financial worries &middot; Low motivation &middot; "
                "Life changes and personal challenges</p>",
                "accent-teal",
            )
        )
    with c2:
        render_html(
            card(
                "<h4>🗓️ What a session might look like</h4>"
                + "".join(
                    f"<p>{n}. {esc(t)}</p>"
                    for n, t in enumerate(
                        [
                            "You choose a topic and preferred format (chat, audio or video).",
                            "You're matched with a suitable professional.",
                            "You talk at your own pace; you decide what to share.",
                            "You leave with ideas and practical next steps.",
                        ],
                        start=1,
                    )
                ),
                "accent-blue",
            )
        )
        render_html(
            card(
                "<h4>🙌 Is it for me?</h4><p>You don't need to be in crisis to talk to a counsellor. "
                "Many people reach out simply because they want support, perspective or a safe space.</p>",
                "accent-blue",
            )
        )


def _render_book(result: AnalysisResult | None) -> None:
    st.markdown("### Book a counselling session")
    render_html(
        card(
            f"{chip('Simulated demo', 'sim')}"
            "<p><b>This is a demonstration only.</b> No real appointment will be booked, no counsellor will be "
            "contacted, and none of the information below is stored or sent anywhere.</p>",
            "soft-blue",
        )
    )

    default_topic = result.concern_category if result and result.concern_category in CONCERN_CATEGORIES else None
    with st.form("demo_booking_form"):
        topic = st.selectbox(
            "Topic you'd like to talk about",
            CONCERN_CATEGORIES,
            index=CONCERN_CATEGORIES.index(default_topic) if default_topic else None,
            placeholder="Choose a topic...",
        )
        c1, c2 = st.columns(2)
        fmt = c1.radio(
            "Preferred format",
            ["Chat", "Audio call", "Video call"],
            horizontal=True,
            key="booking_format",
        )
        slot = c2.radio(
            "Preferred time",
            ["Morning", "Afternoon", "Evening"],
            horizontal=True,
            key="booking_time",
        )
        day = st.selectbox("Preferred day", ["Any day this week", "Weekday", "Weekend"])
        submit = st.form_submit_button("Request session (simulation)", type="primary")

    if submit:
        if not topic:
            st.error("Please choose a topic for the demo request.", icon="⚠️")
        else:
            st.session_state["booking"] = {"topic": topic, "format": fmt, "slot": slot, "day": day}

    booking = st.session_state.get("booking")
    if booking:
        render_html(
            card(
                f"{chip('Simulated action', 'sim')}"
                "<h4>✅ Demo request completed</h4>"
                "<p><b>No appointment has been booked.</b> In the real YourDOST product, this step would "
                "connect you to counsellor availability and confirm a session.</p>"
                f"<p class='yd-muted'>Demo selections: {esc(booking['topic'])} &middot; {esc(booking['format'])} "
                f"&middot; {esc(booking['slot'])} &middot; {esc(booking['day'])}</p>",
                "accent-teal",
            )
        )
        st.button("Clear demo request", on_click=_clear_booking, key="clear_booking")


def _render_learn() -> None:
    st.markdown("### Learn about professional support")
    with st.expander("Who can support my wellbeing?", expanded=True):
        st.markdown(
            "- **Counsellors** offer talk-based support for everyday challenges such as stress, relationships and coping.\n"
            "- **Psychologists** are trained to understand and support emotional and behavioural difficulties and may use "
            "structured therapies.\n"
            "- **Psychiatrists** are medical doctors who can assess and treat mental-health conditions, including with "
            "medication.\n\n"
            "A counsellor or doctor can help you work out which kind of support fits you best."
        )
    with st.expander("When might talking to a professional help?"):
        st.markdown(
            "- Feelings have lasted for weeks and aren't easing\n"
            "- Sleep, work, relationships or appetite are being affected\n"
            "- You feel stuck, overwhelmed or alone with a problem\n"
            "- Self-help tools aren't enough on their own\n"
            "- You'd simply like a confidential, neutral space to talk"
        )
    with st.expander("Common questions"):
        st.markdown(
            "**Do I need a diagnosis to start?** No. You can talk to a counsellor about anything on your mind.\n\n"
            "**Is it only for serious problems?** No. Many people use counselling to build resilience and perspective.\n\n"
            "**Can this app replace a professional?** No. This app offers general guidance only."
        )
    render_emergency_box("Need urgent help instead?")


def render_counselling(result: AnalysisResult | None) -> None:
    st.markdown("## Would you like to speak with a professional?")
    st.write(
        "Talking to someone can make a real difference. Choose an option below to explore support. "
        "Booking in this prototype is a **simulation**."
    )

    if result is not None and result.mode != "crisis":
        render_html(
            card(
                f"<p>Based on your check-in: <b>{esc(result.counselling_reason)}</b></p>",
                "soft-teal",
            )
        )

    st.session_state.setdefault("counselling_view", VIEW_EXPLORE)
    current = st.session_state["counselling_view"]
    c1, c2, c3 = st.columns(3)
    c1.button(
        "🔍 Explore counselling support",
        use_container_width=True,
        type="primary" if current == VIEW_EXPLORE else "secondary",
        on_click=_set_view,
        args=(VIEW_EXPLORE,),
        key="cs_explore",
    )
    c2.button(
        "📅 Book a counselling session (demo)",
        use_container_width=True,
        type="primary" if current == VIEW_BOOK else "secondary",
        on_click=_set_view,
        args=(VIEW_BOOK,),
        key="cs_book",
    )
    c3.button(
        "📖 Learn about professional support",
        use_container_width=True,
        type="primary" if current == VIEW_LEARN else "secondary",
        on_click=_set_view,
        args=(VIEW_LEARN,),
        key="cs_learn",
    )

    st.divider()
    if current == VIEW_BOOK:
        _render_book(result)
    elif current == VIEW_LEARN:
        _render_learn()
    else:
        _render_explore()
