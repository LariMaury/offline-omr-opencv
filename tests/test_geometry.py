"""Geometry and grid-calibration tests using generated synthetic images."""
import cv2
import numpy as np
import pytest

from generate_synthetic_cards import (
    ALIGNMENT_CENTERS,
    TOTAL_QUESTIONS,
    draw_card,
    perspective_photo,
)
from omr_demo_core import (
    TARGET_HEIGHT,
    TARGET_WIDTH,
    calibrate_grid,
    correct_perspective_by_marks,
    find_grid_cut,
)


def test_perspective_correction_detects_four_marks_and_normalizes_shape():
    distorted = perspective_photo(draw_card())

    corrected, points = correct_perspective_by_marks(distorted)

    assert corrected is not None
    assert points is not None
    assert points.shape == (4, 2)
    assert corrected.shape == (TARGET_HEIGHT, TARGET_WIDTH, 3)


def test_perspective_correction_returns_none_when_one_mark_is_missing():
    card = draw_card()
    fx, fy = ALIGNMENT_CENTERS[0]
    cx, cy = int(TARGET_WIDTH * fx), int(TARGET_HEIGHT * fy)
    cv2.rectangle(card, (cx - 45, cy - 45), (cx + 45, cy + 45),
                  (255, 255, 255), -1)

    corrected, points = correct_perspective_by_marks(card)

    assert corrected is None
    assert points is None


def test_grid_cut_ignores_a_late_horizontal_line():
    gray = np.full((1000, 800), 255, dtype=np.uint8)
    cv2.line(gray, (0, 900), (799, 900), 0, 5)

    assert find_grid_cut(gray) == 250


def test_grid_calibration_rejects_an_image_without_bubbles():
    gray = np.full((TARGET_HEIGHT, TARGET_WIDTH), 255, dtype=np.uint8)

    with pytest.raises(ValueError, match="bubble contours detected"):
        calibrate_grid(gray, 400, int(TARGET_HEIGHT * 0.95))


def test_grid_calibration_recovers_the_synthetic_layout():
    card = draw_card()
    gray = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY)
    y_cut = find_grid_cut(gray)

    geometry = calibrate_grid(gray, y_cut, int(TARGET_HEIGHT * 0.95))

    assert len(geometry.rows_y) == 15
    assert len(geometry.positions_x) == 3
    assert all(len(positions) == 5 for positions in geometry.positions_x.values())
    assert geometry.radius > 0
    assert TOTAL_QUESTIONS <= len(geometry.rows_y) * len(geometry.positions_x)
