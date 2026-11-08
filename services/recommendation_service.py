"""Curated, non-diagnostic recommendations and the safe fallback engine.

Two responsibilities:
  1. ``get_exercises`` - deterministic "try it now" self-help exercises per concern
     (the "smart recommendations"). These never depend on the AI, so they are always
     shown, and they are reviewed content rather than model-generated advice.
  2. ``build_fallback_analysis`` - a complete analysis used when the Groq API is
     unavailable, so the user journey never dead-ends.

All content is general, informational wellbeing guidance. It is not medical advice.
"""

from __future__ import annotations

from dataclasses import dataclass

from models import AnalysisResult, CheckinData, Resource


@dataclass(frozen=True)
class Exercise:
    id: str
    title: str
    duration: str
    why: str
    steps: tuple[str, ...]


EXERCISES: dict[str, Exercise] = {
    "box_breathing": Exercise(
        id="box_breathing",
        title="Box breathing (1-2 minutes)",
        duration="2 min",
        why="Slow, even breathing helps your body settle when you feel tense or rushed.",
        steps=(
            "Sit comfortably and relax your shoulders.",
            "Breathe in slowly through your nose for 4 seconds.",
            "Hold gently for 4 seconds.",
            "Breathe out slowly through your mouth for 4 seconds.",
            "Hold for 4 seconds, then repeat 4-6 rounds.",
        ),
    ),
    "worklife_boundaries": Exercise(
        id="worklife_boundaries",
        title="Work-life balance reset",
        duration="10 min",
        why="Small boundaries and clear priorities make workload feel more manageable.",
        steps=(
            "Write down everything on your plate, then mark the top 3 that truly matter this week.",
            "Identify one task you can delay, delegate or ask to re-scope, and note who to talk to.",
            "Set a 'shutdown ritual': a fixed time and a 2-minute routine that signals the workday is over.",
            "Protect one short break today (walk, water, stretch) and put it in your calendar.",
            "Consider sharing your workload honestly with your manager or HR using specific examples.",
        ),
    ),
    "grounding_54321": Exercise(
        id="grounding_54321",
        title="5-4-3-2-1 grounding exercise",
        duration="3 min",
        why="Bringing attention to your senses can ease racing thoughts and bring you back to the present.",
        steps=(
            "Pause and take one slow breath.",
            "Notice 5 things you can see around you.",
            "Notice 4 things you can feel (feet on floor, fabric, chair).",
            "Notice 3 things you can hear.",
            "Notice 2 things you can smell, and 1 thing you can taste. Breathe slowly.",
        ),
    ),
    "worry_time": Exercise(
        id="worry_time",
        title="Scheduled 'worry time' journal",
        duration="10 min",
        why="Giving worries a time and place can stop them from following you all day.",
        steps=(
            "Pick a 10-minute window (not close to bedtime) as your daily worry time.",
            "When a worry appears earlier, jot a few words down and tell yourself 'I'll come back to this'.",
            "In worry time, write each worry and ask: can I do something about it today?",
            "For things you can act on, write one small next step. For the rest, practise letting them go.",
        ),
    ),
    "sleep_hygiene": Exercise(
        id="sleep_hygiene",
        title="Sleep hygiene basics",
        duration="Ongoing",
        why="Consistent habits help your body learn when it is time to sleep.",
        steps=(
            "Keep a regular wake-up time, even on weekends.",
            "Avoid screens and bright light for 30-60 minutes before bed.",
            "Limit caffeine after midday and heavy meals close to bedtime.",
            "Keep your room cool, dark and quiet; use the bed mainly for sleep.",
            "If you can't sleep after ~20 minutes, get up, do something calm in dim light, then return when sleepy.",
        ),
    ),
    "pmr": Exercise(
        id="pmr",
        title="Progressive muscle relaxation",
        duration="8 min",
        why="Tensing then releasing muscles can help your body unwind before sleep.",
        steps=(
            "Lie down or sit comfortably and take three slow breaths.",
            "Tense your feet and calves for 5 seconds, then release for 10 seconds.",
            "Move upward: thighs, stomach, hands, arms, shoulders, face.",
            "Notice the contrast between tension and relaxation as you go.",
            "Finish with three slow breaths and let your body feel heavy.",
        ),
    ),
    "small_steps": Exercise(
        id="small_steps",
        title="Tiny-steps momentum plan",
        duration="5 min",
        why="When motivation is low, starting very small is easier than waiting to feel ready.",
        steps=(
            "Choose one task that matters to you and shrink it to something doable in 5 minutes.",
            "Do just that, with a timer. You are allowed to stop afterwards.",
            "Pair it with something pleasant (music, a favourite drink).",
            "Note one thing you completed today, however small.",
            "Add one more small step tomorrow rather than a big change.",
        ),
    ),
    "money_snapshot": Exercise(
        id="money_snapshot",
        title="Money worries: calm snapshot",
        duration="15 min",
        why="Seeing the full picture on paper is usually less scary than the picture in your head.",
        steps=(
            "Write down fixed monthly expenses and income (estimates are fine).",
            "Mark the one or two items causing the most pressure.",
            "Pick one small step this week (e.g., review a subscription, ask about a payment plan).",
            "Consider talking to a trusted person or a qualified financial advisor about bigger decisions.",
        ),
    ),
    "i_statements": Exercise(
        id="i_statements",
        title="Preparing a calm conversation",
        duration="10 min",
        why="Clear, kind wording makes difficult conversations less likely to escalate.",
        steps=(
            "Write the one thing you most want the other person to understand.",
            "Use 'I' statements: 'I feel ___ when ___ because ___. What I need is ___.'",
            "Choose a calm time and place; agree on a short time-box if it helps.",
            "Plan to listen first for a couple of minutes without interrupting.",
            "If it is too hard to do alone, a counsellor can help you rehearse or mediate.",
        ),
    ),
    "self_compassion": Exercise(
        id="self_compassion",
        title="Self-compassion pause",
        duration="3 min",
        why="Treating yourself as you would a good friend can soften self-criticism.",
        steps=(
            "Notice the hard feeling and name it: 'This is a moment of stress.'",
            "Remind yourself: 'Many people struggle with this at times.'",
            "Place a hand on your chest or arm and take three slow breaths.",
            "Ask: 'What would I say to a friend in this situation?' and say it to yourself.",
        ),
    ),
    "three_good_things": Exercise(
        id="three_good_things",
        title="Three small good things",
        duration="3 min",
        why="Noticing small positives helps counter the pull of low mood and low energy.",
        steps=(
            "At the end of the day, write down three things that went okay, however small.",
            "Next to each, note what role you or someone else played.",
            "Do this for a week and see if anything shifts.",
        ),
    ),
}

# Exercise IDs shown per concern category (smart recommendations)
EXERCISES_BY_CATEGORY: dict[str, list[str]] = {
    "Work-related stress": ["box_breathing", "worklife_boundaries", "self_compassion"],
    "Anxiety and overthinking": ["grounding_54321", "box_breathing", "worry_time"],
    "Sleep problems": ["sleep_hygiene", "pmr", "box_breathing"],
    "Relationship difficulties": ["i_statements", "box_breathing", "self_compassion"],
    "Family problems": ["i_statements", "box_breathing", "self_compassion"],
    "Financial stress": ["money_snapshot", "box_breathing", "worry_time"],
    "Lack of motivation": ["small_steps", "three_good_things", "self_compassion"],
    "Personal challenges": ["self_compassion", "grounding_54321", "three_good_things"],
    "Other": ["box_breathing", "grounding_54321", "self_compassion"],
}

# Fallback content per category: (summary stem, resources, next steps)
_CATEGORY_CONTENT: dict[str, dict] = {
    "Work-related stress": {
        "topic": "work-related stress",
        "resources": [
            Resource("Short breathing exercise", "Exercise", "A quick technique to reset between meetings or tasks."),
            Resource("Work-life balance guidance", "Self-help", "Practical ideas for boundaries, priorities and workload conversations."),
            Resource("Stress and workload self-assessment", "Assessment", "A brief wellbeing assessment to understand your stress patterns."),
            Resource("Talk to a professional counsellor", "Counselling", "A confidential space to explore workload pressure and coping strategies."),
        ],
        "steps": [
            "Pick your top 3 priorities for this week and let the rest wait.",
            "Take a 2-minute breathing break between demanding tasks today.",
            "Prepare 1-2 specific examples to discuss workload with your manager.",
            "Set a clear end-of-day shutdown routine and keep one real break.",
        ],
    },
    "Anxiety and overthinking": {
        "topic": "anxious or racing thoughts",
        "resources": [
            Resource("Grounding exercise (5-4-3-2-1)", "Exercise", "Brings your attention back to the present when thoughts spiral."),
            Resource("Guided self-help: managing worry", "Self-help", "Step-by-step guidance on noticing and loosening worry loops."),
            Resource("Wellbeing check assessment", "Assessment", "A short self-reflection tool to understand how worry affects you."),
            Resource("Talk to a professional counsellor", "Counselling", "A counsellor can help you build tools for overthinking in a safe space."),
        ],
        "steps": [
            "Try the 5-4-3-2-1 grounding exercise next time thoughts speed up.",
            "Write your worries down and note one small action for those you can influence.",
            "Limit late-night scrolling and news that feeds worry.",
            "Share how you feel with someone you trust.",
        ],
    },
    "Sleep problems": {
        "topic": "difficulty with sleep",
        "resources": [
            Resource("Sleep hygiene guidance", "Self-help", "Evidence-informed habits that support more restful sleep."),
            Resource("Relaxation exercise before bed", "Exercise", "Progressive muscle relaxation and slow breathing for winding down."),
            Resource("Sleep and energy self-reflection", "Assessment", "Track patterns in your sleep, mood and energy."),
            Resource("Counselling if sleep difficulties persist", "Counselling", "Talk with a professional if poor sleep continues or affects daily life."),
        ],
        "steps": [
            "Keep a consistent wake-up time for the next week.",
            "Start a 30-minute screen-free wind-down before bed tonight.",
            "Try progressive muscle relaxation when you lie down.",
            "If poor sleep continues for several weeks, speak with a counsellor or your doctor.",
        ],
    },
    "Relationship difficulties": {
        "topic": "difficulties in a relationship",
        "resources": [
            Resource("Healthy communication guide", "Self-help", "Ways to express needs and listen without escalating conflict."),
            Resource("Calm conversation preparation", "Exercise", "A short exercise to plan a difficult conversation with 'I' statements."),
            Resource("Relationships and wellbeing programme", "Programme", "Group or guided programmes on connection and boundaries."),
            Resource("Talk to a professional counsellor", "Counselling", "A neutral, confidential space to work through relationship concerns."),
        ],
        "steps": [
            "Write down what you most want the other person to understand.",
            "Choose a calm moment for the conversation instead of the heat of the moment.",
            "Take care of basics (sleep, food, movement) while this is on your mind.",
            "Consider counselling if the same issue keeps recurring.",
        ],
    },
    "Family problems": {
        "topic": "challenges within your family",
        "resources": [
            Resource("Navigating family expectations", "Self-help", "Guidance on boundaries, expectations and communication at home."),
            Resource("Calm conversation preparation", "Exercise", "Plan a hard conversation with kindness and clarity."),
            Resource("Family and wellbeing programme", "Programme", "Programmes supporting wellbeing across work and home."),
            Resource("Talk to a professional counsellor", "Counselling", "Confidential support to think through family dynamics."),
        ],
        "steps": [
            "Identify one specific thing you would like to change or feel heard about.",
            "Take short breaks from tense situations when you need to settle.",
            "Lean on one supportive person (a friend, relative or colleague).",
            "Consider speaking with a counsellor for a neutral perspective.",
        ],
    },
    "Financial stress": {
        "topic": "financial pressure",
        "resources": [
            Resource("Money worries: calm snapshot", "Exercise", "A simple way to see your finances clearly and pick one next step."),
            Resource("Managing stress about money", "Self-help", "How financial worries affect wellbeing and ways to cope."),
            Resource("Wellbeing check assessment", "Assessment", "A brief tool to understand how stress is affecting you overall."),
            Resource("Talk to a professional counsellor", "Counselling", "Support with the emotional load of financial pressure."),
        ],
        "steps": [
            "Write a rough list of income and key expenses to see the real picture.",
            "Choose one small action this week (e.g., review a subscription).",
            "Consider a qualified financial advisor for larger decisions.",
            "Notice how this is affecting sleep and mood; talk to someone you trust.",
        ],
    },
    "Lack of motivation": {
        "topic": "low motivation and energy",
        "resources": [
            Resource("Tiny-steps momentum plan", "Exercise", "Build momentum with very small, doable actions."),
            Resource("Guided self-help: low energy and motivation", "Self-help", "Understanding what drains motivation and how to rebuild it."),
            Resource("Energy and mood self-reflection", "Assessment", "A brief reflection to notice patterns in your energy and mood."),
            Resource("Talk to a professional counsellor", "Counselling", "Explore what is behind low motivation with a professional."),
        ],
        "steps": [
            "Choose one 5-minute task and do it with a timer.",
            "Get some daylight and gentle movement today, even a short walk.",
            "Note three small things that went okay today.",
            "If low motivation continues for weeks, consider speaking to a counsellor.",
        ],
    },
    "Personal challenges": {
        "topic": "personal challenges",
        "resources": [
            Resource("Self-compassion pause", "Exercise", "A short practice to ease self-criticism."),
            Resource("Guided self-help library", "Self-help", "Browse self-help guidance for coping with life changes."),
            Resource("Wellbeing check assessment", "Assessment", "A brief assessment to reflect on your overall wellbeing."),
            Resource("Talk to a professional counsellor", "Counselling", "A confidential space to talk through what is on your mind."),
        ],
        "steps": [
            "Write down what's weighing on you in a few sentences.",
            "Pick one small thing that would make today 5% easier.",
            "Talk with someone you trust about how you feel.",
            "Consider counselling if you feel stuck.",
        ],
    },
    "Other": {
        "topic": "what you are going through",
        "resources": [
            Resource("Breathing and grounding exercises", "Exercise", "Quick techniques to settle your mind and body."),
            Resource("Guided self-help library", "Self-help", "Browse general guidance on coping and wellbeing."),
            Resource("Wellbeing check assessment", "Assessment", "A brief assessment to reflect on your overall wellbeing."),
            Resource("Talk to a professional counsellor", "Counselling", "A confidential space to talk, whatever the concern."),
        ],
        "steps": [
            "Take a few minutes to breathe slowly and settle.",
            "Name what's bothering you most in one sentence.",
            "Reach out to someone you trust.",
            "Consider counselling to talk it through with a professional.",
        ],
    },
}

_IMPACT_SCORE = {"Slightly": 0, "Moderately": 1, "Significantly": 2}
_DURATION_SCORE = {"Today": 0, "A few days": 0, "A few weeks": 1, "Several months": 2}

_URGENCY_TO_COUNSELLING = {"low": "optional", "moderate": "consider", "high": "recommended"}

_COUNSELLING_REASON = {
    "optional": (
        "Self-help may be enough for now. Counselling is still available whenever you "
        "would like to talk things through with a professional."
    ),
    "consider": (
        "Because this is affecting your daily life, speaking with a professional counsellor "
        "could be a helpful next step alongside self-help."
    ),
    "recommended": (
        "Given how long and how much this has been affecting you, we'd encourage you to speak "
        "with a professional counsellor soon. You don't have to handle this alone."
    ),
}


def get_exercises(category: str) -> list[Exercise]:
    """Curated 'try it now' exercises for a concern category."""
    ids = EXERCISES_BY_CATEGORY.get(category, EXERCISES_BY_CATEGORY["Other"])
    return [EXERCISES[i] for i in ids]


def derive_support_priority(duration: str, impact: str) -> str:
    """Map duration + impact to a support priority ('low' | 'moderate' | 'high').

    This describes how useful it would be to talk to a human soon. It is NOT a
    clinical risk rating.
    """
    score = _IMPACT_SCORE.get(impact, 1) + _DURATION_SCORE.get(duration, 0)
    if score >= 4:
        return "high"
    if score >= 2:
        return "moderate"
    return "low"


def counselling_reason_for(level: str) -> str:
    return _COUNSELLING_REASON.get(level, _COUNSELLING_REASON["optional"])


def build_fallback_analysis(checkin: CheckinData, reason: str = "") -> AnalysisResult:
    """Safe, rule-based recommendations used when the AI service is unavailable."""
    category = checkin.concern_category if checkin.concern_category in _CATEGORY_CONTENT else "Other"
    content = _CATEGORY_CONTENT[category]
    urgency = derive_support_priority(checkin.duration, checkin.impact)
    level = _URGENCY_TO_COUNSELLING[urgency]

    mood_text = checkin.mood.lower()
    duration_text = checkin.duration.lower()
    summary = (
        f"You told us you are feeling {mood_text} and dealing with {content['topic']}. "
        f"This has been going on for {duration_text} and is affecting your daily life "
        f"{checkin.impact.lower()}. It makes sense to want some support with this."
    )
    message = (
        "Thank you for taking a moment to check in. "
        "What you're feeling is valid, and reaching out for support is a strong first step. "
        "Small, steady steps can make a real difference."
    )

    return AnalysisResult(
        mode="fallback",
        concern_category=category,
        concern_summary=summary,
        recommended_resources=list(content["resources"]),
        practical_next_steps=list(content["steps"]),
        counselling_level=level,
        counselling_reason=counselling_reason_for(level),
        urgency_level=urgency,
        supportive_message=message,
        mood=checkin.mood,
        duration=checkin.duration,
        impact=checkin.impact,
        fallback_reason=reason,
    )
