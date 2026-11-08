"""End-to-end journey tests using Streamlit's headless AppTest runner (no browser, no network)."""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from components.demo_scenarios import SCENARIOS
from services import pipeline
from services.ai_service import parse_ai_response

APP = str(Path(__file__).resolve().parent.parent / "app.py")

AI_JSON = {
    "concern_category": "Work-related stress",
    "concern_summary": "You are juggling a heavy workload <b>and</b> finding it hard to switch off.",
    "recommended_resources": [
        {"title": "Short breathing exercise", "type": "Exercise", "description": "Reset between tasks."},
        {"title": "Counselling option", "type": "Counselling", "description": "Confidential support."},
    ],
    "practical_next_steps": ["Pick three priorities", "Take a short break"],
    "counselling_recommendation": {"level": "consider", "reason": "It is affecting your days."},
    "urgency_level": "moderate",
    "supportive_message": "You are not alone.",
}


@pytest.fixture(autouse=True)
def offline_env(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("FORCE_OFFLINE_MODE", "true")


def new_app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception, at.exception
    return at


def all_text(at: AppTest) -> str:
    parts = [m.value for m in at.markdown] + [i.value for i in at.info] + [e.value for e in at.error]
    parts += [x.label for x in at.expander]
    return "\n".join(parts)


def session_snapshot(at: AppTest) -> dict:
    """All user-visible session values (incl. widget values), across Streamlit versions.

    Older AppTest exposes ``SafeSessionState.filtered_state``; newer versions expose a
    mapping with ``items()``.
    """
    ss = at.session_state
    if hasattr(type(ss), "filtered_state"):
        return dict(ss.filtered_state)
    return dict(ss.items())


def click(at: AppTest, key: str) -> AppTest:
    at.button(key=key).click().run()
    assert not at.exception, at.exception
    return at


def fill_and_submit(at: AppTest, sample_name: str | None = None, **override) -> AppTest:
    sample = {**SCENARIOS[sample_name], **override} if sample_name else override
    v = at.session_state["form_version"]
    if "mood" in sample:
        at.radio(key=f"mood_{v}").set_value(sample["mood"])
    if "concern" in sample:
        at.selectbox(key=f"concern_{v}").set_value(sample["concern"])
    if "duration" in sample:
        at.radio(key=f"duration_{v}").set_value(sample["duration"])
    if "impact" in sample:
        at.radio(key=f"impact_{v}").set_value(sample["impact"])
    if "description" in sample:
        at.text_area(key=f"description_{v}").set_value(sample["description"])
    submit = next(b for b in at.button if b.label == "Submit check-in")
    submit.click().run()
    assert not at.exception, at.exception
    return at


def test_home_page_has_required_content():
    at = new_app()
    text = all_text(at)
    assert "AI Wellbeing Navigator" in text
    assert "How it works" in text
    assert "Privacy" in text and "112" in text
    assert any(b.label == "Start Wellbeing Check-in" for b in at.button)


def test_start_button_opens_checkin():
    at = click(new_app(), "home_start")
    assert at.session_state["nav"].endswith("Wellbeing Check-in")
    assert any(b.label == "Submit check-in" for b in at.button)


@pytest.mark.parametrize("name", [n for n in SCENARIOS if not n.startswith("5.")])
def test_ordinary_scenarios_get_relevant_recommendations(name):
    at = click(new_app(), "home_start")
    at = fill_and_submit(at, name)
    assert at.session_state["nav"].endswith("My Recommendations")
    result = at.session_state["analysis"]
    assert result.mode == "fallback"  # offline: built-in guidance
    assert result.concern_category == SCENARIOS[name]["concern"]
    text = all_text(at)
    assert "Recommended resources" in text and "Practical next steps" in text
    assert "Try it now" in text
    assert "professional" in text.lower()
    assert "112" in text
    # free text is not retained after analysis
    state = session_snapshot(at)
    assert state, "session state snapshot should not be empty"
    assert not any(SCENARIOS[name]["description"] in str(v) for v in state.values())


def test_safety_scenario_shows_human_support_only():
    at = click(new_app(), "home_start")
    at = fill_and_submit(at, "5. Safety test (fictional)")
    result = at.session_state["analysis"]
    assert result.mode == "crisis"
    text = all_text(at)
    assert "112" in text and "Tele-MANAS" in text
    assert "We're here for you" in text
    # no ordinary recommendations
    assert "Recommended resources" not in text
    assert "Practical next steps" not in text
    assert "Try it now" not in text
    assert not result.recommended_resources


def test_ai_mode_renders_cards_and_escapes_html(monkeypatch):
    monkeypatch.setattr(pipeline, "analyse_with_ai", lambda c, s: parse_ai_response(json.dumps(AI_JSON), c))
    at = click(new_app(), "home_start")
    at = fill_and_submit(at, "1. Workload stress")
    assert at.session_state["analysis"].mode == "ai"
    text = all_text(at)
    assert "Short breathing exercise" in text
    assert "&lt;b&gt;and&lt;/b&gt;" in text  # model output is escaped, never rendered as HTML
    assert "<b>and</b>" not in text


def test_validation_blocks_incomplete_submission():
    at = click(new_app(), "home_start")
    at = fill_and_submit(at, description="zq marker")
    assert len(at.error) >= 4
    assert at.session_state["analysis"] is None
    assert at.session_state["nav"].endswith("Wellbeing Check-in")
    # Control for the privacy assertion: session_snapshot() can see committed form text.
    assert any("zq marker" in str(v) for v in session_snapshot(at).values())


def test_reset_clears_everything():
    at = click(new_app(), "home_start")
    at = fill_and_submit(at, "1. Workload stress")
    assert at.session_state["analysis"] is not None
    at = click(at, "recs_reset")
    assert at.session_state["analysis"] is None
    assert at.session_state["nav"].endswith("Wellbeing Check-in")
    assert at.radio(key=f"mood_{at.session_state['form_version']}").value is None


def test_counselling_flow_and_simulated_booking():
    at = click(new_app(), "home_start")
    at = fill_and_submit(at, "1. Workload stress")
    at = click(at, "recs_counselling")
    assert at.session_state["nav"].endswith("Counselling Support")
    assert "Would you like to speak with a professional?" in all_text(at)

    at = click(at, "cs_learn")
    assert "Learn about professional support" in all_text(at)

    at = click(at, "cs_book")
    text = all_text(at)
    assert "Simulated demo" in text
    next(b for b in at.button if b.label == "Request session (simulation)").click().run()
    assert not at.exception
    text = all_text(at)
    assert "No appointment has been booked" in text
    assert "Simulated action" in text


def test_load_sample_and_reset_keep_radio_values_valid():
    """Loading a sample and resetting must not feed a label string to radio deserialization."""
    at = click(new_app(), "home_start")
    next(b for b in at.button if b.label == "Load sample into form").click().run()
    assert not at.exception, at.exception
    version = at.session_state["form_version"]
    assert at.radio(key=f"mood_{version}").value == "Stressed"
    assert at.radio(key=f"duration_{version}").value == "A few weeks"
    assert at.radio(key=f"impact_{version}").value == "Moderately"
    at.button(key="reset_on_checkin").click().run()
    assert not at.exception, at.exception
    version = at.session_state["form_version"]
    assert at.radio(key=f"mood_{version}").value is None
    assert at.radio(key=f"duration_{version}").value is None
    assert at.radio(key=f"impact_{version}").value is None
    assert not any(
        SCENARIOS["1. Workload stress"]["description"] in str(v)
        for v in session_snapshot(at).values()
    )


def test_about_page_renders():
    at = new_app()
    at.session_state["nav"] = at.session_state["nav"].replace("Home", "About & Privacy")
    at.session_state["nav"] = "🔒 About & Privacy"
    at.run()
    assert not at.exception
    assert len(at.tabs) == 3
