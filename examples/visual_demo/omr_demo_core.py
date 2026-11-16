"""Sanitized OMR core adapted from the private desktop application.

Provenance:
- grid calibration: ``calibrar_grade``;
- alignment correction: ``corrigir_perspectiva_por_marcas``;
- bubble measurement: selected loop from ``_corrigir_folha_interna``;
- grading: ``avaliar_respostas``.

Only geometry, mark classification and grading are retained. OCR, student data,
configuration files, logging, licensing and filesystem side effects are absent.
"""
from dataclasses import dataclass

import cv2
import numpy as np


TARGET_WIDTH, TARGET_HEIGHT = 1241, 1754
ALIGNMENT_SIDE_PT = 12.0
ALIGNMENT_CENTERS = ((0.030, 0.024), (0.970, 0.024),
                     (0.030, 0.976), (0.970, 0.976))
LETTERS = "ABCDE"


@dataclass(frozen=True)
class GridGeometry:
    rows_y: list[float]
    positions_x: dict[int, list[float]]
    radius: float
    y_cut: int


@dataclass(frozen=True)
class RecognitionResult:
    geometry: GridGeometry
    strong: dict[int, list[str]]
    weak: dict[int, list[str]]
    ratios: dict[int, dict[str, float]]
    centers: dict[int, dict[str, tuple[int, int]]]


@dataclass(frozen=True)
class GradeResult:
    correct: int
    incorrect: int
    blank: int
    multiple: int
    details: dict[int, str]


def find_alignment_marks(image_bgr: np.ndarray):
    """Return alignment centers in TL, TR, BL, BR order, or ``None``."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    _, dark = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    expected_side = width * (ALIGNMENT_SIDE_PT / 595.0)
    contours, _ = cv2.findContours(dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if not (expected_side * 0.5 <= w <= expected_side * 2.2 and
                expected_side * 0.5 <= h <= expected_side * 2.2):
            continue
        if abs(w - h) > expected_side * 0.6:
            continue
        if cv2.contourArea(contour) < 0.6 * w * h:
            continue
        cx, cy = x + w / 2.0, y + h / 2.0
        outer = int(max(w, h) * 1.9)
        y0, y1 = max(int(cy) - outer, 0), min(int(cy) + outer, height)
        x0, x1 = max(int(cx) - outer, 0), min(int(cx) + outer, width)
        neighborhood = dark[y0:y1, x0:x1]
        total_ink = cv2.countNonZero(neighborhood)
        mark_ink = cv2.countNonZero(dark[y:y + h, x:x + w])
        if total_ink - mark_ink > 0.12 * neighborhood.size:
            continue
        candidates.append((cx, cy, (w + h) / 2.0))

    if len(candidates) < 4:
        return None

    corners = ((0, 0), (width, 0), (0, height), (width, height))
    points, sides = [], []
    for target_x, target_y in corners:
        eligible = []
        for cx, cy, side in candidates:
            if abs(cx - target_x) <= width * 0.15 and abs(cy - target_y) <= height * 0.15:
                distance = (cx - target_x) ** 2 + (cy - target_y) ** 2
                eligible.append((distance, (cx, cy), side))
        if not eligible:
            return None
        _, point, side = min(eligible, key=lambda item: item[0])
        points.append(point)
        sides.append(side)

    if max(sides) > 1.6 * min(sides):
        return None
    tl, tr, bl, br = points
    width_top = np.hypot(tr[0] - tl[0], tr[1] - tl[1])
    width_bottom = np.hypot(br[0] - bl[0], br[1] - bl[1])
    height_left = np.hypot(bl[0] - tl[0], bl[1] - tl[1])
    height_right = np.hypot(br[0] - tr[0], br[1] - tr[1])
    if not 0.85 <= width_top / max(width_bottom, 1) <= 1.18:
        return None
    if not 0.85 <= height_left / max(height_right, 1) <= 1.18:
        return None
    ratio = (width_top + width_bottom) / max(height_left + height_right, 1)
    expected_ratio = ((ALIGNMENT_CENTERS[1][0] - ALIGNMENT_CENTERS[0][0]) * 595) / \
                     ((ALIGNMENT_CENTERS[2][1] - ALIGNMENT_CENTERS[0][1]) * 842)
    if not 0.78 * expected_ratio <= ratio <= 1.25 * expected_ratio:
        return None
    return np.float32(points)


def correct_perspective_by_marks(image_bgr: np.ndarray):
    """Return ``(normalized_image, detected_points)`` or ``(None, None)``."""
    points = find_alignment_marks(image_bgr)
    if points is None:
        return None, None
    destination = np.float32([(TARGET_WIDTH * fx, TARGET_HEIGHT * fy)
                              for fx, fy in ALIGNMENT_CENTERS])
    matrix = cv2.getPerspectiveTransform(points, destination)
    normalized = cv2.warpPerspective(
        image_bgr, matrix, (TARGET_WIDTH, TARGET_HEIGHT), borderValue=(255, 255, 255)
    )
    return normalized, points


def find_grid_cut(gray: np.ndarray):
    """Find the horizontal divider immediately above the answer grid."""
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    height, width = gray.shape
    for contour in sorted(contours, key=lambda c: cv2.boundingRect(c)[1]):
        _, y, w, _ = cv2.boundingRect(contour)
        if w > width * 0.5 and height * 0.15 < y < height * 0.80:
            return y + 5
    return int(height * 0.25)


def calibrate_grid(gray: np.ndarray, y_cut: int, y_end: int):
    """Reconstruct row and A–E centers from detected bubble contours."""
    _, width = gray.shape
    region = gray[y_cut:y_end, :]
    smooth = cv2.GaussianBlur(region, (3, 3), 0)
    marks = cv2.adaptiveThreshold(
        smooth, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 41, 8
    )
    expected_diameter = width * 0.034
    min_diameter, max_diameter = expected_diameter * 0.5, expected_diameter * 1.6
    contours, _ = cv2.findContours(marks, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubbles = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if (min_diameter <= w <= max_diameter and min_diameter <= h <= max_diameter and
                abs(w - h) <= expected_diameter * 0.5):
            bubbles.append((x + w / 2.0, y + h / 2.0, (w + h) / 4.0))
    if len(bubbles) < 20:
        raise ValueError(f"only {len(bubbles)} bubble contours detected")

    bubbles.sort(key=lambda bubble: bubble[1])
    groups = [[bubbles[0]]]
    for bubble in bubbles[1:]:
        if bubble[1] - groups[-1][-1][1] > expected_diameter * 0.6:
            groups.append([bubble])
        else:
            groups[-1].append(bubble)
    groups = [group for group in groups if len(group) >= 4]
    if 8 <= len(groups) <= 15:
        column_count = 3
    elif len(groups) == 25:
        column_count = 4
    else:
        raise ValueError(f"unexpected grid row count: {len(groups)}")

    rows_y = [float(np.median([bubble[1] for bubble in group])) for group in groups]
    column_width = width / float(column_count)
    x_samples = {}
    for group in groups:
        by_column = {}
        for bubble in group:
            column = int(bubble[0] // column_width)
            if 0 <= column < column_count:
                by_column.setdefault(column, []).append(bubble)
        for column, cell in by_column.items():
            if len(cell) == 5:
                for index, bubble in enumerate(sorted(cell, key=lambda item: item[0])):
                    x_samples.setdefault((column, index), []).append(bubble[0])

    positions_x = {}
    for column in range(column_count):
        positions_x[column] = []
        for index in range(5):
            values = x_samples.get((column, index))
            if values:
                positions_x[column].append(float(np.median(values)))
            else:
                alternatives = [float(np.median(sample)) - (other - column) * column_width
                                for (other, letter), sample in x_samples.items() if letter == index]
                if not alternatives:
                    raise ValueError("letter positions could not be calibrated")
                positions_x[column].append(float(np.median(alternatives)))
    radius = float(np.median([bubble[2] for bubble in bubbles]))
    return GridGeometry(rows_y, positions_x, radius, y_cut)


def classify_bubbles(image_bgr: np.ndarray, total_questions: int,
                     mark_threshold=0.40, weak_threshold=0.22):
    """Measure ink density and classify every synthetic answer bubble."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    y_cut = find_grid_cut(gray)
    geometry = calibrate_grid(gray, y_cut, int(gray.shape[0] * 0.95))
    measure_radius = max(int(geometry.radius * 0.75), 2)
    strong = {q: [] for q in range(1, total_questions + 1)}
    weak = {q: [] for q in range(1, total_questions + 1)}
    ratios, centers = {}, {}
    row_count = len(geometry.rows_y)
    height, width = gray.shape

    for column, x_positions in geometry.positions_x.items():
        for row_index, relative_y in enumerate(geometry.rows_y):
            question = column * row_count + row_index + 1
            if question > total_questions:
                continue
            ratios[question], centers[question] = {}, {}
            for letter_index, x_position in enumerate(x_positions):
                letter = LETTERS[letter_index]
                cx, cy = int(round(x_position)), int(round(relative_y + y_cut))
                y0, y1 = max(cy-measure_radius,0), min(cy+measure_radius+1,height)
                x0, x1 = max(cx-measure_radius,0), min(cx+measure_radius+1,width)
                window = binary[y0:y1, x0:x1]
                mask = np.zeros(window.shape, dtype="uint8")
                cv2.circle(mask, (cx-x0, cy-y0), measure_radius, 255, -1)
                area = cv2.countNonZero(mask)
                ratio = cv2.countNonZero(cv2.bitwise_and(window, mask)) / float(max(area, 1))
                ratios[question][letter] = ratio
                centers[question][letter] = (cx, cy)
                if ratio > mark_threshold:
                    strong[question].append(letter)
                elif ratio > weak_threshold:
                    weak[question].append(letter)
    return RecognitionResult(geometry, strong, weak, ratios, centers)


def grade_responses(responses: dict[int, list[str]], answer_key: dict[int, str]):
    """Grade synthetic responses using the original rule structure."""
    details = {}; correct = incorrect = blank = multiple = 0
    for question in sorted(answer_key):
        marked = responses.get(question, [])
        if not marked:
            blank += 1; details[question] = "BLANK"
        elif len(marked) > 1:
            multiple += 1; details[question] = "MULTIPLE"
        elif marked[0] == answer_key[question]:
            correct += 1; details[question] = f"{marked[0]} · CORRECT"
        else:
            incorrect += 1; details[question] = f"{marked[0]} · INCORRECT"
    return GradeResult(correct, incorrect, blank, multiple, details)
