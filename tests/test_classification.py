"""Bubble-density classification tests for the synthetic fixture."""
import numpy as np

from generate_synthetic_cards import STRONG, TOTAL_QUESTIONS, WEAK, draw_card
from omr_demo_core import classify_bubbles


def _non_empty(mapping):
    return {question: values for question, values in mapping.items() if values}


def test_classification_matches_the_generated_fixture():
    recognition = classify_bubbles(draw_card(), TOTAL_QUESTIONS)

    assert _non_empty(recognition.strong) == STRONG
    assert _non_empty(recognition.weak) == WEAK
    assert recognition.strong[3] == []
    assert recognition.strong[12] == []
    assert recognition.strong[4] == ["C", "E"]


def test_weak_mark_is_between_the_documented_thresholds():
    recognition = classify_bubbles(draw_card(), TOTAL_QUESTIONS)
    ratio = recognition.ratios[5]["D"]

    assert 0.22 < ratio <= 0.40
    assert recognition.strong[5] == []
    assert recognition.weak[5] == ["D"]


def test_threshold_comparisons_are_strict_at_the_boundary():
    card = draw_card()
    baseline = classify_bubbles(card, TOTAL_QUESTIONS)
    ratio = baseline.ratios[5]["D"]

    at_boundary = classify_bubbles(
        card, TOTAL_QUESTIONS, mark_threshold=1.0, weak_threshold=ratio
    )
    just_below = classify_bubbles(
        card,
        TOTAL_QUESTIONS,
        mark_threshold=1.0,
        weak_threshold=np.nextafter(ratio, -np.inf),
    )

    assert "D" not in at_boundary.weak[5]
    assert "D" in just_below.weak[5]
