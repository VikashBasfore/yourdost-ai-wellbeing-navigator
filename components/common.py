"""Shared UI helpers: navigation, theme/CSS, HTML helpers and session-state reset."""

from __future__ import annotations

import html as _html

import streamlit as st

from config import EMERGENCY_NUMBER_INDIA, HELPLINES_INDIA

PAGE_HOME = "🏠 Home"
PAGE_CHECKIN = "📝 Wellbeing Check-in"
PAGE_RECS = "💡 My Recommendations"
PAGE_COUNSELLING = "🧑‍⚕️ Counselling Support"
PAGE_ABOUT = "🔒 About & Privacy"
PAGES = [PAGE_HOME, PAGE_CHECKIN, PAGE_RECS, PAGE_COUNSELLING, PAGE_ABOUT]

# Palette: calming blue, teal and white
BLUE = "#1E5AA8"
DEEP_BLUE = "#17324D"
TEAL = "#139A93"
SOFT_TEAL = "#E3F5F3"
SOFT_BLUE = "#E6F0FA"
WHITE = "#FFFFFF"

_CSS = f"""
<style>
.block-container {{ padding-top: 4rem; padding-bottom: 3rem; max-width: 1100px; }}
h1, h2, h3 {{ color: {DEEP_BLUE}; letter-spacing: -0.01em; }}
[data-testid="stHeaderActionElements"] {{ display: none; }}

.yd-hero {{
  background: linear-gradient(135deg, {BLUE} 0%, {TEAL} 100%);
  color: {WHITE}; border-radius: 22px; padding: 2.2rem 2rem; margin-bottom: 1.4rem;
  box-shadow: 0 10px 30px rgba(30, 90, 168, 0.25);
}}
.yd-hero h1 {{ color: {WHITE}; margin: 0 0 .4rem 0; font-size: clamp(1.6rem, 4vw, 2.4rem); }}
.yd-hero p {{ color: rgba(255,255,255,.95); font-size: 1.08rem; margin: 0; max-width: 46rem; }}
.yd-eyebrow {{ text-transform: uppercase; letter-spacing: .12em; font-size: .75rem; opacity: .85; margin-bottom: .5rem; }}

.yd-card {{
  background: {WHITE}; border: 1px solid #D9E8EE; border-radius: 16px;
  padding: 1.15rem 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 10px rgba(23,50,77,.06);
  color: {DEEP_BLUE};
}}
.yd-card h3, .yd-card h4 {{ margin: 0 0 .4rem 0; color: {DEEP_BLUE}; line-height: 1.3; }}
.yd-card h4 {{ font-size: 1.12rem; }}
.yd-card h3 {{ font-size: 1.35rem; }}
.yd-card p {{ margin: .25rem 0; color: #38536D; line-height: 1.6; }}
.yd-card.accent-teal {{ border-left: 6px solid {TEAL}; }}
.yd-card.accent-blue {{ border-left: 6px solid {BLUE}; }}
.yd-card.soft-teal {{ background: {SOFT_TEAL}; border-color: #BFE6E2; }}
.yd-card.soft-blue {{ background: {SOFT_BLUE}; border-color: #C6DBF1; }}
.yd-card.crisis {{ background: #FFF6F3; border: 1.5px solid #E08A73; border-left: 8px solid #D9674C; }}
.yd-card.disclaimer {{ background: #F2F7FB; border-style: dashed; }}
.yd-card.counsel {{ background: linear-gradient(180deg, #F3FBFA 0%, {WHITE} 70%); border: 1.5px solid #9ED4CF; border-left: 8px solid {TEAL}; padding: 1.35rem 1.4rem; }}
.yd-card .big {{ font-size: 1.6rem; }}
.yd-kicker {{ text-transform: uppercase; letter-spacing: .08em; font-size: .75rem; font-weight: 700; color: {TEAL}; margin: 0 0 .35rem 0; }}
.yd-counsel-line {{ font-size: 1.05rem; color: {DEEP_BLUE}; font-weight: 600; }}

.yd-chips {{ display: flex; flex-wrap: wrap; gap: .45rem; margin: .15rem 0 1rem; }}
.yd-chip {{
  display: inline-block; padding: .28rem .75rem; border-radius: 999px; font-size: .82rem;
  font-weight: 600; margin: 0 .4rem .4rem 0; background: {SOFT_BLUE}; color: {BLUE};
  border: 1px solid #C6DBF1; line-height: 1.3;
}}
.yd-chips .yd-chip {{ margin: 0; }}
.yd-chip.teal {{ background: {SOFT_TEAL}; color: #0B756F; border-color: #BFE6E2; }}
.yd-chip.warn {{ background: #FFF1D6; color: #8A5A00; border-color: #F1D8A0; }}
.yd-chip.high {{ background: #FDE8E2; color: #A8432B; border-color: #F0C0B3; }}
.yd-chip.sim {{ background: #FFF1D6; color: #8A5A00; border-color: #F1D8A0; text-transform: uppercase; letter-spacing:.05em; }}

.yd-step {{ display: flex; gap: .8rem; align-items: flex-start; margin: .55rem 0; }}
.yd-step .num {{
  flex: 0 0 auto; width: 1.9rem; height: 1.9rem; border-radius: 50%; background: {TEAL};
  color: {WHITE}; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .9rem;
}}
.yd-step .txt {{ color: #29445D; line-height: 1.5; padding-top: .15rem; }}

.yd-resource {{
  background: #F7FBFC; border: 1px solid #D5E6EC; border-left: 4px solid {TEAL};
  border-radius: 12px; padding: .8rem .95rem; margin: .7rem 0 0;
}}
.yd-resource .title {{
  font-weight: 700; color: {DEEP_BLUE}; font-size: 1rem; line-height: 1.35;
  display: flex; flex-wrap: wrap; align-items: center; gap: .35rem .45rem;
}}
.yd-resource .title .yd-chip {{ margin: 0; font-weight: 600; }}
.yd-resource .desc {{ color: #4A6178; font-size: .95rem; line-height: 1.5; margin-top: .3rem; }}

.yd-quote {{ font-size: 1.08rem; line-height: 1.6; color: #0B5E59; font-style: italic; }}
.yd-muted {{ color: #5B7288; font-size: .88rem; }}
.yd-small {{ font-size: .85rem; }}

.yd-sidebar-brand {{ font-weight: 800; color: {DEEP_BLUE}; font-size: 1.15rem; line-height: 1.25; }}
.yd-sidebar-brand span {{ color: {TEAL}; }}
.yd-mode {{
  border-radius: 12px; padding: .55rem .7rem; font-size: .86rem; font-weight: 600; line-height: 1.35; margin: .2rem 0 .6rem;
}}
.yd-mode-off {{ background: #FFF6E0; color: #7A5200; border: 1px solid #F1D48A; }}
.yd-mode-on {{ background: {SOFT_TEAL}; color: #0B756F; border: 1px solid #BFE6E2; }}

.yd-crisis-number {{
  font-size: 2.4rem; font-weight: 800; letter-spacing: .04em; color: #A8432B; margin: .15rem 0 .2rem; line-height: 1;
}}
.yd-crisis-intro {{ font-size: 1.12rem; line-height: 1.6; }}

div[data-testid="stAlert"] {{
  border-radius: 14px; border-left: 6px solid {TEAL} !important; background: {SOFT_TEAL};
}}
div.stButton > button, div[data-testid="stFormSubmitButton"] > button {{
  border-radius: 12px; font-weight: 600; padding: .6rem 1.2rem;
}}

/* Default Streamlit sidebar is 256px, which wraps "My Recommendations". */
section[data-testid="stSidebar"] {{
  border-right: 1px solid #D9E8EE;
  width: 23rem !important;
  min-width: 23rem !important;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
  white-space: nowrap;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label p {{
  white-space: nowrap;
  font-size: .98rem;
}}

@media (max-width: 800px) {{
  section[data-testid="stSidebar"] {{ width: min(23rem, 88vw) !important; min-width: 0 !important; }}
  .yd-hero {{ padding: 1.4rem 1.2rem; border-radius: 16px; }}
  .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
  .yd-card h3 {{ font-size: 1.2rem; }}
  .yd-crisis-number {{ font-size: 2rem; }}
  div[data-testid="stHorizontalBlock"] {{ flex-wrap: wrap; gap: .6rem; }}
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
    width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
  }}
}}
</style>
"""


def inject_css() -> None:
    st.markdown(_compact(_CSS), unsafe_allow_html=True)


def _compact(markup: str) -> str:
    """Strip indentation so Markdown never treats HTML as a code block."""
    return " ".join(line.strip() for line in markup.splitlines() if line.strip())


def esc(value: object) -> str:
    """HTML-escape any text (including AI-generated text) before rendering as HTML."""
    return _html.escape(str(value), quote=True)


def render_html(markup: str) -> None:
    st.markdown(_compact(markup), unsafe_allow_html=True)


def card(inner_html: str, variant: str = "") -> str:
    return f'<div class="yd-card {variant}">{inner_html}</div>'


def chip(text: str, variant: str = "") -> str:
    return f'<span class="yd-chip {variant}">{esc(text)}</span>'


def numbered_steps(steps: list[str]) -> str:
    return "".join(
        f'<div class="yd-step"><div class="num">{i}</div><div class="txt">{esc(s)}</div></div>'
        for i, s in enumerate(steps, start=1)
    )


def render_emergency_box(heading: str = "If you or someone else may be in immediate danger") -> None:
    """Always-available emergency information for India."""
    lines = "".join(
        f"<p><b>{esc(number)}</b> &nbsp;{esc(name)}</p>" for name, number in HELPLINES_INDIA
    )
    render_html(
        card(
            f'<p class="yd-kicker">Immediate help</p>'
            f"<h4>🚨 {esc(heading)}</h4>"
            f'<p class="yd-crisis-number">{esc(EMERGENCY_NUMBER_INDIA)}</p>'
            f"<p>Please call <b>{esc(EMERGENCY_NUMBER_INDIA)}</b> (India emergency number) or "
            "go to the nearest hospital, and reach out to a trusted person nearby.</p>"
            f"{lines}",
            "crisis",
        )
    )


# ---------------------------------------------------------------------------
# Navigation & session state
# ---------------------------------------------------------------------------
def radio_value_from_ui(options: list, ui_value: str):
    """Map a radio label or index string back to the option.

    Streamlit 1.51 deserializes radios with ``options[ui_value]`` and expects an
    int. A newer frontend, or a saved selection, can send the label instead
    (``\"Stressed\"`` or ``\"😣 Stressed\"``). Resolving that label avoids
    ``TypeError: list indices must be integers or slices, not str``.
    """
    if ui_value in options:
        return ui_value
    for option in options:
        text = str(option)
        if ui_value == text or ui_value.endswith(" " + text):
            return option
    try:
        index = int(ui_value)
    except ValueError:
        return None
    if 0 <= index < len(options):
        return options[index]
    return None


def install_legacy_radio_fix() -> None:
    """Teach older Streamlit radios to accept a label string as well as an index."""
    from streamlit.elements.widgets.radio import RadioSerde

    if "formatted_options" in getattr(RadioSerde, "__annotations__", {}):
        return
    if getattr(RadioSerde, "_yd_radio_fix", False):
        return

    original = RadioSerde.deserialize

    def deserialize(self, ui_value):
        if isinstance(ui_value, str):
            return radio_value_from_ui(list(self.options), ui_value)
        return original(self, ui_value)

    RadioSerde.deserialize = deserialize
    RadioSerde._yd_radio_fix = True


def init_state() -> None:
    defaults = {
        "nav": PAGE_HOME,
        "pending_nav": None,
        "analysis": None,
        "form_version": 0,
        "booking": None,
        "analysing": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def apply_pending_navigation() -> None:
    """Apply a requested page change BEFORE the sidebar radio is created."""
    target = st.session_state.get("pending_nav")
    if target in PAGES:
        st.session_state["nav"] = target
    st.session_state["pending_nav"] = None


def go_to(page: str) -> None:
    """Button callback: request navigation to ``page`` on the next run."""
    st.session_state["pending_nav"] = page


def clear_form_state() -> None:
    """Start a fresh check-in form on the next script run.

    Must run from a widget callback, before any radio is created. Bumping
    ``form_version`` gives the next form new widget keys, so this does not
    write or delete radio widget state. The previous free-text description is
    removed so it is not kept in the session.
    """
    version = int(st.session_state.get("form_version", 0))
    description_key = f"description_{version}"
    if description_key in st.session_state:
        del st.session_state[description_key]
    st.session_state["form_version"] = version + 1


def stage_checkin_values(values: dict) -> None:
    """Fill the next check-in form. Call only from a widget callback.

    Values are written to keys the current run has not created yet, so an
    existing radio is never assigned a new session value.
    """
    clear_form_state()
    version = st.session_state["form_version"]
    for name in ("mood", "concern", "duration", "impact", "description", "sample_choice"):
        if name in values:
            st.session_state[f"{name}_{version}"] = values[name]


def reset_checkin(navigate: bool = True) -> None:
    """Clear all check-in data and results (nothing is stored beyond this session)."""
    st.session_state["analysis"] = None
    st.session_state["booking"] = None
    st.session_state["counselling_view"] = "explore"
    clear_form_state()
    if navigate:
        st.session_state["pending_nav"] = PAGE_CHECKIN
