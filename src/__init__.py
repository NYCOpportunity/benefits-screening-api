"""
Initialize the `src` package and ensure the project root is on `sys.path` so
that absolute imports like `src.models` work regardless of where the program
is launched from (e.g., running `python src/main.py`).
"""

import sys
from pathlib import Path

# Compute the project root (one directory above this `__init__.py`).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add the project root to `sys.path` if it's not already present.
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.append(str(_PROJECT_ROOT))
