# 🌿 YourDOST AI Wellbeing Navigator

An AI-powered employee wellbeing support prototype that helps employees understand their wellbeing concerns and discover relevant self-help resources, practical next steps and counselling options.

<p align="center">

**[🚀 Live Application](https://yourdost-ai-wellbeing-navigator-i3hgfadxqes9mq4zgtty4s.streamlit.app/) | [💻 GitHub Repository](https://github.com/VikashBasfore/yourdost-ai-wellbeing-navigator)**

</p>

---

## 📌 Project Overview

Employees may have access to multiple wellbeing services but often struggle to identify which support is relevant to their current situation.

YourDOST AI Wellbeing Navigator addresses this problem through a conversational wellbeing check-in and AI-powered recommendations.

Users describe what they are experiencing in natural language. The application analyses the description and provides relevant resources, practical next steps and counselling suggestions.

**The goal:** Make employee wellbeing support easier to understand and access.

## 🎯 Key Features

- **Conversational Wellbeing Check-in:** Employees describe their concerns using natural language.
- **AI-powered Analysis:** Groq AI analyses wellbeing descriptions and generates personalised summaries.
- **Personalised Recommendations:** Suggests relevant self-help resources, exercises and assessments.
- **Practical Next Steps:** Provides actionable suggestions based on the identified concern.
- **Counselling Support:** Helps users explore professional counselling options.
- **Safety-first Architecture:** Rule-based safety checks identify crisis-related language and prioritise human support.
- **Fallback Guidance:** Built-in recommendations remain available when the AI service is unavailable.
- **Privacy-conscious Design:** The prototype avoids collecting names and personal identifiers.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend / UI | Streamlit |
| AI Integration | Groq API |
| AI Model | OpenAI GPT-OSS 120B (via Groq, configurable) |
| API Client | OpenAI Python SDK |
| Data Validation | Python |
| Testing | Pytest |
| Version Control | Git, GitHub |
| Deployment | Streamlit Community Cloud |

## 🏗️ Application Architecture

```text
Employee
   |
   v
Streamlit Wellbeing Check-in
   |
   v
Safety Detection Layer
   |
   +------ Crisis detected ------> Immediate Human Support
   |
   v
AI Analysis Service
   |
   v
Groq API
   |
   v
Structured JSON Response
   |
   v
Response Validation
   |
   +------ AI unavailable ------> Built-in Guidance
   |
   v
Recommendation Service
   |
   v
Personalised Results
   |
   +--> Wellbeing Summary
   +--> Recommended Resources
   +--> Practical Next Steps
   +--> Counselling Options
```

## 📁 Project Structure

```text
yourdost-ai-wellbeing-navigator/
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
│
├── components/
│   ├── about.py
│   ├── common.py
│   ├── counselling.py
│   ├── dashboard.py
│   ├── demo_scenarios.py
│   ├── recommendation_cards.py
│   └── wellbeing_checkin.py
│
├── services/
│   ├── ai_service.py
│   ├── pipeline.py
│   ├── recommendation_service.py
│   └── safety_service.py
│
├── tests/
│   ├── conftest.py
│   ├── test_ai_and_pipeline.py
│   ├── test_app_e2e.py
│   ├── test_safety_service.py
│   └── test_validation.py
│
├── app.py
├── config.py
├── models.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/VikashBasfore/yourdost-ai-wellbeing-navigator.git

cd yourdost-ai-wellbeing-navigator
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-groq-api-key"
GROQ_MODEL = "openai/gpt-oss-120b"
```

Use the model configured and available in your Groq account.

Never commit API keys or secrets to GitHub.

### 5. Run the application

```bash
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## 🧪 Testing and Validation

Automated testing was performed using Pytest.

**Automated test results: 82 passed.**

Manual AI validation covered six fictional wellbeing scenarios:

1. Work-related stress
2. Sleep difficulties
3. Low motivation
4. Work-life balance
5. Career uncertainty
6. Workplace relationships

The application was also tested with a fictional crisis-related scenario to verify that immediate human-support guidance takes priority over ordinary AI recommendations.

Run the test suite:

```bash
python -m pytest -v
```

## 🔐 Safety, Privacy and Limitations

- The application is a wellbeing support prototype, not a medical or clinical service.
- It does not diagnose mental health conditions or recommend medication.
- Crisis-related inputs are handled through a separate safety-first flow.
- Emergency and human-support information is prioritised when crisis indicators are detected.
- The application uses fictional scenarios for testing.
- Check-in descriptions are sent to Groq for AI analysis when AI mode is enabled. Users should avoid entering identifying or sensitive personal information.
- AI-generated recommendations may be inaccurate or incomplete and should not replace qualified professional support.
- Rule-based crisis detection may not identify every possible crisis expression.

## 🚀 Deployment

The application is deployed using Streamlit Community Cloud.

**Live Demo:**

https://yourdost-ai-wellbeing-navigator-i3hgfadxqes9mq4zgtty4s.streamlit.app/

## 📈 Future Improvements

- Expand the wellbeing recommendation library.
- Improve multilingual wellbeing support.
- Add more comprehensive safety evaluation scenarios.
- Improve recommendation quality through structured user feedback.
- Introduce analytics for anonymous product-level usage and success measurement.

## 👨‍💻 Author

**Vikash Basfore**

GitHub: https://github.com/VikashBasfore

---

*YourDOST AI Wellbeing Navigator — Helping employees discover the right wellbeing support, one check-in at a time.*