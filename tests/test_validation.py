from components.common import radio_value_from_ui
from components.wellbeing_checkin import validate_checkin

OK = dict(
    mood="Stressed",
    concern="Work-related stress",
    duration="A few days",
    impact="Moderately",
    description="I have too much work and feel stretched thin.",
)


def test_valid_input_has_no_errors():
    assert validate_checkin(**OK) == []


def test_missing_selections_are_reported():
    errors = validate_checkin(None, None, None, None, "short")
    assert len(errors) == 5


def test_description_length_limits():
    assert validate_checkin(**{**OK, "description": "   too short   "})
    assert validate_checkin(**{**OK, "description": "x" * 1501})


def test_radio_label_is_not_used_as_an_index():
    options = ["Happy", "Stressed", "Sad"]
    assert radio_value_from_ui(options, "Stressed") == "Stressed"
    assert radio_value_from_ui(options, "😣 Stressed") == "Stressed"
    assert radio_value_from_ui(options, "1") == "Stressed"
    assert radio_value_from_ui(["📝 Wellbeing Check-in"], "📝 Wellbeing Check-in") == "📝 Wellbeing Check-in"
    assert radio_value_from_ui(options, "not-a-mood") is None


def test_contact_details_are_rejected():
    assert validate_checkin(**{**OK, "description": "Call me on 98765 43210 about my workload please"})
    assert validate_checkin(**{**OK, "description": "Email me at someone@example.com about my workload"})
    assert validate_checkin(**{**OK, "description": "I have worked 12 hours a day for 3 weeks now."}) == []
