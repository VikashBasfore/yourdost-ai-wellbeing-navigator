# 🌿 YourDOST AI Wellbeing Navigator

An AI-assisted prototype that helps employees understand what they're experiencing and discover the most relevant
YourDOST support (self-help, assessments, programmes or counselling), with a **safety-first** design and
**privacy by default**.

> ⚠️ This is a demonstration prototype using fictional data. It is **not** a medical device, diagnostic tool or
> emergency service.

---

## 1. Project overview

YourDOST gives employees access to online counselling, self-help resources, wellbeing assessments and programmes.
The Navigator sits in front of those services: the employee completes a 2-minute check-in, and the app summarises their
concern in plain language, recommends relevant resources and next steps, and explains whether speaking with a
professional counsellor may help.

## 2. Problem statement

Employees often don't know **which** support service fits their situation or **what to do next**. This leads to:

- low discovery and engagement with available wellbeing services,
- people waiting until a problem becomes severe before seeking help,
- generic content that doesn't feel relevant to their situation.

## 3. Proposed solution

A guided, conversational-style check-in that:

1. captures mood, main concern, duration and impact (structured) plus a free-text description,
2. runs an **independent safety screen first**,
3. uses Groq (through the OpenAI-compatible API) to produce a **structured, non-diagnostic** analysis,
4. combines it with **curated exercises** (breathing, grounding, sleep, etc.) that never depend on the AI,
5. routes the user to counselling support when helpful, and
6. degrades gracefully to built-in guidance if the AI is unavailable.

**Business value (for the BA assignment):** better service discovery, earlier help-seeking, higher engagement and
counselling conversion, and a consistent, safe first touchpoint, with no personally identifying data collected.

## 4. Features

| Area | What it does |
|---|---|
| Welcome dashboard | Hero, how-it-works, YourDOST offerings, privacy & safety disclaimer, *Start Wellbeing Check-in* |
| Check-in | Mood, concern, duration, impact, free text; validation; blocks emails/phone numbers; reset |
| AI analysis | Structured JSON: `concern_category`, `concern_summary`, `recommended_resources`, `practical_next_steps`, `counselling_recommendation`, `urgency_level`, `supportive_message` |
| Smart recommendations | Curated "Try it now" exercises per concern (e.g. box breathing for work stress; sleep hygiene + PMR for sleep; 5-4-3-2-1 grounding for anxiety) |
| Counselling support | Explore · Book (**simulated demo**) · Learn about professional support |
| Safety layer | Independent rule-based screening before any AI call → human-support view with **112** (India), no ordinary tips |
| UX | Sidebar navigation, loading spinner, error handling, reset, responsive layout, calming blue/teal/white palette |
| Resilience | API timeout, retries, output validation, safe fallback recommendations |

## 5. Architecture

```
app.py (Streamlit entry, navigation, session state)
│
├── components/           UI only
│   ├── dashboard.py            welcome page
│   ├── wellbeing_checkin.py    form + validation
│   ├── recommendation_cards.py results cards + crisis view
│   ├── counselling.py          counselling section (simulated booking)
│   ├── about.py                about / privacy / safety
│   ├── common.py               theme CSS, HTML escaping, navigation helpers
│   └── demo_scenarios.py       fictional sample check-ins
│
├── services/             business logic (no Streamlit imports)
│   ├── pipeline.py             orchestration: safety → AI → fallback
│   ├── safety_service.py       independent safety layer
│   ├── ai_service.py           Groq call (OpenAI-compatible SDK), prompt, JSON validation, error mapping
│   └── recommendation_service.py curated exercises + fallback engine
│
├── config.py             settings & constants (env / .env / Streamlit secrets)
├── models.py             dataclasses (CheckinData, AnalysisResult, Resource)
└── tests/                pytest unit + end-to-end (Streamlit AppTest) tests
```

**Request flow**

```
Check-in ──► Safety layer ── crisis? ──► Human-support view (no AI call, no ordinary tips)
                │ clear
                ▼
        Groq analysis ── error/timeout/rate limit/no key ──► Built-in fallback guidance
                │
                ▼
        Validated result ──► Cards + curated exercises + counselling options
```

Key design choices:

- **Safety before AI.** The safety layer is deterministic and never calls the model on a match. Groq has no
  moderation endpoint, so the rule-based layer is the safety check. It does not diagnose.
- **Never trust model output.** JSON is parsed, normalised against controlled vocabularies and length-limited; all
  text is HTML-escaped before display.
- **Prompt-injection resistance.** The user's text is delimited as data and the model is told to ignore instructions
  inside it. Prompts are never shown in the UI.
- **No diagnosis.** The prompt, the fallback copy and the UI all avoid diagnostic labels, and
  `urgency_level` is defined as *"how soon talking to someone would help"*, not a clinical rating.

## 6. Technology stack

Python 3.10+ · Streamlit · OpenAI Python SDK (pointed at Groq) · python-dotenv · pytest

## 7. Installation

```powershell
# from the project folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# for tests as well:
pip install -r requirements-dev.txt
```

## 8. API configuration

The key is **never hardcoded**. Use either option:

**Option A: `.env` file (local)**

```powershell
copy .env.example .env
# edit .env and set GROQ_API_KEY=...
```

**Option B: Streamlit secrets**

```powershell
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# edit and set GROQ_API_KEY
```

Both `.env` and `secrets.toml` are git-ignored.

| Variable | Default | Purpose |
|---|---|---|
| `GROQ_API_KEY` | – | Groq API credential (required for AI mode) |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Free-tier text model. `llama-3.3-70b-versatile` is enterprise-only |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | OpenAI-compatible Groq endpoint |
| `GROQ_TIMEOUT_SECONDS` | `25` | Request timeout |
| `GROQ_MAX_RETRIES` | `1` | SDK retries |
| `FORCE_OFFLINE_MODE` | `false` | Skip the API and use built-in guidance |

With no key set, the app still works end-to-end using built-in guidance (the sidebar shows the current mode).

## 9. Run the application

```powershell
streamlit run app.py
```

Open <http://localhost:8501>. Run the tests with:

```powershell
python -m pytest -q
```

## 10. Example user journey

1. **Open the app** → welcome dashboard explains the flow, privacy and safety.
2. Click **Start Wellbeing Check-in** (optionally load a fictional sample under *Demo*).
3. Answer: *Stressed* · *Work-related stress* · *A few weeks* · *Moderately* · "My team lost two people and I'm online until late…"
4. **Submit** → spinner → safety check passes → AI analysis.
5. **My Recommendations** shows: topic and priority chips, empathetic summary, recommended resources, practical
   next steps, curated *Try it now* exercises, and a counselling suggestion.
6. Click **Explore counselling support** → explore options, run the **simulated** booking (clearly labelled; nothing is booked).
7. Click **Reset check-in** to clear everything and start again.

**Safety journey:** if the description suggests self-harm, harm to others or immediate danger, the user sees a supportive
message, **112** and Tele-MANAS, steps to reach a trusted person, and counselling information, and **no** ordinary tips.

## 11. Testing

`python -m pytest -q` runs 80+ tests, including a headless end-to-end run of the real app (`tests/test_app_e2e.py`).

| Scenario (fictional) | Expected | Result |
|---|---|---|
| 1. Workload stress | Breathing exercise, work-life balance, counselling option | ✅ |
| 2. Sleep difficulties | Sleep hygiene, relaxation exercise, counselling if persistent | ✅ |
| 3. Anxiety and overthinking | Grounding exercise, guided self-help, counselling option | ✅ |
| 4. Overwhelmed and demotivated | Tiny-steps plan, high support priority, counselling recommended | ✅ |
| 5. Suicidal-thought language | Safety view with 112 and human support; **no** ordinary recommendations; AI never called | ✅ |

The suite also covers: validation, PII blocking, malformed/hostile AI output, HTML escaping, API timeout/auth/rate-limit/
connection errors, fallback behaviour, reset, counselling navigation and simulated booking.
Tests mock the Groq client; a live call needs your own Groq API key. Use fictional check-in text.

## 12. Safety and privacy considerations

**Safety**
- Independent, deterministic safety layer runs before any AI recommendation.
- Detects language about self-harm/suicidal thoughts, harming others and immediate danger (including common Hinglish
  phrases); ordinary workplace idioms ("my boss will kill me") are deliberately not treated as crises.
- On a match: supportive message, **112** (India), Tele-MANAS (14416), encouragement to contact a trusted person and
  professional human support. No diagnosis or clinical risk assessment is attempted.
- The AI cannot replace emergency services or qualified professionals; all outputs carry disclaimers.

**Privacy**
- No names, phone numbers, emails or employee IDs are requested; obvious contact details in free text are rejected.
- Check-in data lives only in the browser session's memory. The free text is discarded right after analysis.
  *Reset check-in* clears everything.
- User messages are never logged (only event names / exception types).
- API keys come from environment variables or Streamlit secrets and are never displayed.
- When Groq AI is enabled, the check-in text is sent to Groq to generate recommendations (disclosed in *About & Privacy*). Use synthetic data in this prototype.

## 13. Known limitations

- **Rule-based safety screening can miss indirect, coded or non-English/Hinglish expressions** and can over-trigger on
  some phrases (it errs on the side of showing support). It must be reviewed and extended with clinical advisers before
  any real deployment. Moderation adds coverage only when the API is available.
- Not clinically validated; recommendations are generic wellbeing guidance, not advice.
- Counselling booking is a **simulation**; there is no integration with YourDOST scheduling or any real service.
- AI output varies between runs; the output validator guards the format, not factual correctness.
- Resources recommended by the AI are *types* of support (it is told not to invent links); they are not yet linked to a
  live YourDOST content catalogue.
- Helpline numbers (112, 14416) should be re-verified and localised before production; the app currently targets India and English.
- Session-only state means a browser refresh loses results (by design for privacy).
- Production use would also need consent flows, organisation-level data-processing agreements, authentication/SSO,
  accessibility audit, rate limiting and monitoring that respects privacy.

## 14. Possible next steps

Integrate the YourDOST content/booking APIs, multi-language support, a clinician-reviewed safety lexicon, aggregated
(anonymous) analytics for HR insights, and A/B testing of recommendation wording and conversion to counselling.
