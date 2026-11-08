"""Fictional, synthetic demo scenarios. No real employee data is used anywhere."""

from __future__ import annotations

SCENARIOS: dict[str, dict[str, str]] = {
    "1. Workload stress": {
        "mood": "Stressed",
        "concern": "Work-related stress",
        "duration": "A few weeks",
        "impact": "Moderately",
        "description": (
            "My team has lost two people and I've taken over their work on top of my own. "
            "I'm staying online until late most nights and still feel behind. I find it hard to switch off "
            "even on weekends."
        ),
    },
    "2. Sleep difficulties": {
        "mood": "Okay",
        "concern": "Sleep problems",
        "duration": "A few weeks",
        "impact": "Moderately",
        "description": (
            "I keep waking up around 3 am and can't fall back asleep. I'm tired all day, "
            "relying on lots of coffee, and my concentration at work is slipping."
        ),
    },
    "3. Anxiety and overthinking": {
        "mood": "Anxious",
        "concern": "Anxiety and overthinking",
        "duration": "Several months",
        "impact": "Significantly",
        "description": (
            "I replay conversations in my head and keep imagining everything that could go wrong "
            "before a presentation. My thoughts race, especially at night, and I find it hard to relax."
        ),
    },
    "4. Overwhelmed and demotivated": {
        "mood": "Overwhelmed",
        "concern": "Lack of motivation",
        "duration": "Several months",
        "impact": "Significantly",
        "description": (
            "Everything feels like too much lately. I used to enjoy my work but now I struggle to start "
            "even simple tasks, and I feel guilty about falling behind. I have little energy left after work."
        ),
    },
    "5. Safety test (fictional)": {
        "mood": "Sad",
        "concern": "Personal challenges",
        "duration": "A few days",
        "impact": "Significantly",
        "description": (
            "I feel like there is no point anymore and I have been thinking about ending my life."
        ),
    },
}
