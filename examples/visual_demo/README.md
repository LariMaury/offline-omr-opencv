# Reproducible synthetic OMR demonstration

This directory contains a narrow, approved isolation of the original OMR logic and new presentation tooling. It is not a copy of the desktop application.

## Files

- `omr_demo_core.py`: alignment-mark detection, homography, answer-grid calibration, circular ink-density measurement, response classification, and grading.
- `generate_synthetic_cards.py`: creates an entirely fictional 20-question card plus tilted and perspective-distorted variants.
- `render_real_demo.py`: runs the isolated algorithms and renders the comparison, overlay, flow image, GIF, and JSON result.
- `synthetic-fixture.json`: generated fixture metadata and expected synthetic marks.

## Provenance

The isolated core is adapted from the private project's `leitor.py`:

- `corrigir_perspectiva_por_marcas`;
- `calibrar_grade`;
- the ink-density loop inside `_corrigir_folha_interna`;
- `avaliar_respostas`;
- card geometry from `gerar_folha_respostas`.

The extraction deliberately excludes OCR, student identity, roster matching, databases, online configuration, licensing, UI code, original paths, and debug-file writes. `detectar_tipo` was consulted but not needed because the fixture declares test type A.

## Installation

Python 3.14 was used for the validated clean-environment run. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The pinned environment uses NumPy 2.5.1, opencv-python 5.0.0.93, Pillow 12.3.0, and pytest 9.2.0.

## Reproduction

Run the two commands in this order:

```powershell
python -B examples/visual_demo/generate_synthetic_cards.py
python -B examples/visual_demo/render_real_demo.py
```

The scripts write only to `media/` and `examples/visual_demo/synthetic-fixture.json`.

Regenerate the conceptual architecture diagram separately:

```powershell
python -B examples/create_conceptual_flow.py
```

## Tests

```powershell
python -m pytest -q
```

The tests generate cards in memory, exercise failure and boundary cases, and reproduce the committed JSON without accessing the private project. They are synthetic regression tests, not a recognition-accuracy benchmark.

## Controlled result

The current fixture produces:

```json
{
  "correct": 13,
  "incorrect": 3,
  "blank": 3,
  "multiple": 1
}
```

It also produces one weak-mark alert that is not counted as an answer. These values demonstrate deterministic execution on one synthetic image; they are not an OMR accuracy benchmark.

## Portability note

The presentation scripts use byte-based OpenCV image encoding and decoding so Windows paths containing non-ASCII characters are handled reliably. This change belongs to the demo tooling and does not alter the OMR algorithm.
