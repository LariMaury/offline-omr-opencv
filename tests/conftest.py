"""Test configuration for the standalone synthetic OMR demonstration."""
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "examples" / "visual_demo"

if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))
