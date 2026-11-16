"""Generate fictitious answer sheets compatible with the isolated OMR core."""
import json
from pathlib import Path

import cv2
import numpy as np

from omr_demo_core import ALIGNMENT_CENTERS, ALIGNMENT_SIDE_PT, TARGET_HEIGHT, TARGET_WIDTH


ROOT = Path(__file__).resolve().parents[2]
MEDIA = ROOT / "media"
W, H = TARGET_WIDTH, TARGET_HEIGHT
TOTAL_QUESTIONS = 20
ANSWER_KEY = {q: "ABCDE"[(q - 1) % 5] for q in range(1, TOTAL_QUESTIONS + 1)}

# Purposefully includes correct, incorrect, blank, multiple and weak answers.
STRONG = {
    1: ["A"], 2: ["B"], 4: ["C", "E"], 6: ["A"], 7: ["C"],
    8: ["C"], 9: ["D"], 10: ["A"], 11: ["A"], 13: ["C"],
    14: ["D"], 15: ["E"], 16: ["A"], 17: ["B"], 18: ["D"],
    19: ["D"], 20: ["E"],
}
WEAK = {5: ["D"]}


def put(canvas, text, position, scale, color=(35, 45, 63), thickness=2):
    cv2.putText(canvas, text, position, cv2.FONT_HERSHEY_SIMPLEX, scale, color,
                thickness, cv2.LINE_AA)


def bubble_centers():
    x_scale, y_scale = W / 595.0, H / 842.0
    x_offsets = [value * x_scale for value in (51.1, 75.3, 99.5, 123.7, 147.9)]
    column_width = W / 3.0
    y_start, y_step = 220.3 * y_scale, 37.92 * y_scale
    centers = {}
    for question in range(1, TOTAL_QUESTIONS + 1):
        column, row = (question - 1) // 15, (question - 1) % 15
        centers[question] = {
            letter: (int(round(column * column_width + x_offsets[index])),
                     int(round(y_start + row * y_step)))
            for index, letter in enumerate("ABCDE")
        }
    return centers


def draw_card():
    canvas = np.full((H, W, 3), 255, dtype=np.uint8)
    navy, muted, green = (45, 41, 32), (135, 132, 126), (107, 119, 42)
    put(canvas, "SYNTHETIC OMR DEMO", (105, 100), 1.25, navy, 3)
    put(canvas, "FICTITIOUS DATA ONLY", (107, 140), 0.62, green, 2)
    put(canvas, "20 QUESTIONS  |  TEST TYPE A", (690, 112), 0.58, muted, 2)
    cv2.line(canvas, (105, 165), (1135, 165), (205, 207, 210), 2)
    put(canvas, "STUDENT: SYNTHETIC SAMPLE", (105, 235), 0.62, navy, 2)
    put(canvas, "ROSTER NO.: 00", (840, 235), 0.62, navy, 2)
    put(canvas, "DEMONSTRATION CARD - NO REAL PERSON OR INSTITUTION", (105, 305), 0.52, muted, 1)

    divider_y = int(round(H * 192.5 / 842.0))
    cv2.rectangle(canvas, (0, divider_y - 5), (W - 1, divider_y + 3), navy, -1)

    radius = int(round(W * 10.1 / 595.0))
    centers = bubble_centers()
    for question, by_letter in centers.items():
        first_x, y = by_letter["A"]
        number_x = first_x - int(round(W * 32 / 595.0))
        put(canvas, f"{question:02d}", (number_x, y + 7), 0.48, navy, 1)
        for letter, (x, cy) in by_letter.items():
            if letter in STRONG.get(question, []):
                cv2.circle(canvas, (x, cy), radius - 3, (25, 25, 25), -1, cv2.LINE_AA)
            elif letter in WEAK.get(question, []):
                cv2.circle(canvas, (x, cy), 9, (35, 35, 35), -1, cv2.LINE_AA)
            cv2.circle(canvas, (x, cy), radius, (115, 115, 115), 2, cv2.LINE_AA)
            if letter not in STRONG.get(question, []):
                size = cv2.getTextSize(letter, cv2.FONT_HERSHEY_SIMPLEX, 0.34, 1)[0]
                cv2.putText(canvas, letter, (x - size[0] // 2, cy + size[1] // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.34, (205, 205, 205), 1, cv2.LINE_AA)

    put(canvas, "Fill one bubble per question. This sheet is synthetic.", (105, 1690),
        0.5, muted, 1)

    side = int(round(W * (ALIGNMENT_SIDE_PT / 595.0)))
    for fx, fy in ALIGNMENT_CENTERS:
        cx, cy = int(round(W * fx)), int(round(H * fy))
        cv2.rectangle(canvas, (cx - side // 2, cy - side // 2),
                      (cx + side // 2, cy + side // 2), (0, 0, 0), -1)
    return canvas


def rotate_expanded(image, degrees=6.5):
    height, width = image.shape[:2]
    center = (width / 2.0, height / 2.0)
    matrix = cv2.getRotationMatrix2D(center, degrees, 1.0)
    cosine, sine = abs(matrix[0, 0]), abs(matrix[0, 1])
    new_width = int(height * sine + width * cosine)
    new_height = int(height * cosine + width * sine)
    matrix[0, 2] += new_width / 2.0 - center[0]
    matrix[1, 2] += new_height / 2.0 - center[1]
    return cv2.warpAffine(image, matrix, (new_width, new_height),
                          borderValue=(242, 244, 248))


def perspective_photo(image):
    source = np.float32([(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)])
    destination = np.float32([(105, 70), (1345, 135), (65, 1830), (1390, 1885)])
    matrix = cv2.getPerspectiveTransform(source, destination)
    return cv2.warpPerspective(image, matrix, (1460, 1960), borderValue=(242, 244, 248))


def save_png(path, image):
    """Write through memory so Windows paths with non-ASCII text are safe."""
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError(f"could not encode {path.name}")
    path.write_bytes(encoded.tobytes())


def main():
    MEDIA.mkdir(parents=True, exist_ok=True)
    aligned = draw_card()
    tilted = rotate_expanded(aligned)
    perspective = perspective_photo(aligned)
    save_png(MEDIA / "synthetic-card-aligned.png", aligned)
    save_png(MEDIA / "synthetic-card-tilted.png", tilted)
    save_png(MEDIA / "synthetic-card-perspective.png", perspective)
    fixture = {
        "synthetic": True,
        "questions": TOTAL_QUESTIONS,
        "answer_key": ANSWER_KEY,
        "strong_marks": STRONG,
        "weak_marks": WEAK,
        "expected_blank_questions": [3, 5, 12],
        "expected_multiple_questions": [4],
    }
    with (Path(__file__).parent / "synthetic-fixture.json").open("w", encoding="utf-8") as stream:
        json.dump(fixture, stream, indent=2)
    print("Synthetic cards created in", MEDIA)


if __name__ == "__main__":
    main()
