import pytest

from components.demo_scenarios import SCENARIOS
from services import safety_service
from services.safety_service import (
    HARM_TO_OTHERS,
    IMMEDIATE_DANGER,
    SELF_HARM,
    check_safety,
    check_text_rules,
)

CRISIS_TEXTS = [
    ("I want to kill myself", SELF_HARM),
    ("I've been thinking about suicide lately", SELF_HARM),
    ("I just want to die.", SELF_HARM),
    ("I don't want to live anymore", SELF_HARM),
    ("everyone would be better off without me", SELF_HARM),
    ("I have been cutting myself again", SELF_HARM),
    ("I plan to end my life tonight", SELF_HARM),
    ("There is no point in living", SELF_HARM),
    ("I WANT TO END MY LIFE", SELF_HARM),
    ("main marna chahta hoon", SELF_HARM),
    ("I feel like there is no point anymore and I have been thinking about ending my life.", SELF_HARM),
    ("I want to hurt my manager badly", HARM_TO_OTHERS),
    ("I'm going to kill him", HARM_TO_OTHERS),
    ("thinking of hurting people at the office", HARM_TO_OTHERS),
    ("I am in danger right now", IMMEDIATE_DANGER),
    ("I'm not safe at home", IMMEDIATE_DANGER),
    ("he keeps hitting me and I'm scared", IMMEDIATE_DANGER),
]

# Ordinary stress language that must NOT be routed to the crisis flow.
ORDINARY_TEXTS = [
    "My workload is killing me and my boss will kill me if I miss the deadline",
    "I can't sleep and I'm exhausted every day",
    "I don't want to hurt my parents by telling them about my job change",
    "I am ready to kill it at my presentation but I'm so anxious",
    "I overthink everything and my thoughts race at night",
    "I'm going to shoot him an email about the delay",
    "I feel unmotivated and don't want to wake up for meetings",
    "Life is worth living but work has been exhausting",
    "",
]


@pytest.mark.parametrize("text,category", CRISIS_TEXTS)
def test_crisis_language_is_detected(text, category):
    result = check_text_rules(text)
    assert result.is_crisis, text
    assert result.category == category


@pytest.mark.parametrize("text", ORDINARY_TEXTS)
def test_ordinary_language_is_not_flagged(text):
    assert not check_text_rules(text).is_crisis, text


def test_demo_scenarios_1_to_4_are_not_crisis_and_5_is():
    for name, sample in SCENARIOS.items():
        expected = name.startswith("5.")
        assert check_text_rules(sample["description"]).is_crisis is expected, name


def test_unicode_and_spacing_tricks_do_not_bypass():
    assert check_text_rules("I want   to   k\u200bill  my\u00a0self").is_crisis
    assert check_text_rules("i want to end my life").is_crisis
    assert check_text_rules("I don\u2019t want to live anymore").is_crisis


def test_result_contains_no_user_text():
    result = check_text_rules("I want to kill myself")
    assert set(vars(result)) == {"is_crisis", "category", "source"}


def test_moderation_fails_open(ai_settings, monkeypatch):
    from dataclasses import replace

    settings = replace(ai_settings, use_moderation=True)

    class Boom:
        def __init__(self, *a, **k):
            raise RuntimeError("network down")

    monkeypatch.setattr("openai.OpenAI", Boom)
    assert not check_safety("I feel a bit tired today", settings).is_crisis


def test_moderation_flag_triggers_crisis(ai_settings, monkeypatch):
    from dataclasses import replace
    from types import SimpleNamespace

    settings = replace(ai_settings, use_moderation=True)

    class FakeClient:
        def __init__(self, *a, **k):
            self.moderations = SimpleNamespace(
                create=lambda **kw: SimpleNamespace(
                    results=[SimpleNamespace(categories=SimpleNamespace(self_harm=False, self_harm_intent=True))]
                )
            )

    monkeypatch.setattr("openai.OpenAI", FakeClient)
    result = check_safety("something the rules don't know", settings)
    assert result.is_crisis and result.source == "moderation"


def test_rules_run_even_when_moderation_disabled(ai_settings):
    assert check_safety("I want to die", ai_settings).is_crisis
    assert safety_service.check_text_rules("hello").is_crisis is False
