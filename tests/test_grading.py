"""Tests for the deliberately simplified public grading result."""
from omr_demo_core import grade_responses


def test_grading_distinguishes_all_response_states():
    answer_key = {1: "A", 2: "B", 3: "C", 4: "D"}
    responses = {1: ["A"], 2: ["C"], 3: [], 4: ["A", "D"]}

    grade = grade_responses(responses, answer_key)

    assert grade.correct == 1
    assert grade.incorrect == 1
    assert grade.blank == 1
    assert grade.multiple == 1
    assert grade.details[3] == "BLANK"
    assert grade.details[4] == "MULTIPLE"


def test_missing_questions_are_treated_as_blank():
    grade = grade_responses({}, {1: "A", 2: "B"})

    assert grade.correct == 0
    assert grade.incorrect == 0
    assert grade.blank == 2
    assert grade.multiple == 0


def test_empty_answer_key_returns_zero_counts():
    grade = grade_responses({1: ["A"]}, {})

    assert (grade.correct, grade.incorrect, grade.blank, grade.multiple) == (0, 0, 0, 0)
    assert grade.details == {}
