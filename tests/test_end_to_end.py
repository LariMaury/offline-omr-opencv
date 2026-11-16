"""Read-only integration tests for the committed synthetic fixture and artifacts."""
import json
from pathlib import Path

import cv2
import numpy as np

from generate_synthetic_cards import ANSWER_KEY, STRONG, TOTAL_QUESTIONS, WEAK
from omr_demo_core import (
    classify_bubbles,
    correct_perspective_by_marks,
    grade_responses,
)


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"
FIXTURE_PATH = ROOT / "examples" / "visual_demo" / "synthetic-fixture.json"


def _read_bgr(path):
    image = cv2.imdecode(np.frombuffer(path.read_bytes(), np.uint8), cv2.IMREAD_COLOR)
    assert image is not None
    return image


def test_committed_fixture_matches_the_public_constants():
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert fixture["synthetic"] is True
    assert fixture["questions"] == TOTAL_QUESTIONS
    assert fixture["answer_key"] == {str(key): value for key, value in ANSWER_KEY.items()}
    assert fixture["strong_marks"] == {str(key): value for key, value in STRONG.items()}
    assert fixture["weak_marks"] == {str(key): value for key, value in WEAK.items()}


def test_committed_result_is_reproducible_without_the_private_project():
    source = _read_bgr(MEDIA / "synthetic-card-perspective.png")
    corrected, points = correct_perspective_by_marks(source)
    assert corrected is not None
    assert points is not None

    recognition = classify_bubbles(corrected, TOTAL_QUESTIONS)
    grade = grade_responses(recognition.strong, ANSWER_KEY)
    committed = json.loads((MEDIA / "omr-demo-results.json").read_text(encoding="utf-8"))

    assert committed["strong_marks"] == {
        str(question): values
        for question, values in recognition.strong.items()
        if values
    }
    assert committed["weak_marks"] == {
        str(question): values
        for question, values in recognition.weak.items()
        if values
    }
    assert committed["grade"] == {
        "correct": grade.correct,
        "incorrect": grade.incorrect,
        "blank": grade.blank,
        "multiple": grade.multiple,
    }
    assert committed["accuracy_claim"] is None
