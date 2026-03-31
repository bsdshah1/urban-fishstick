"""Vercel serverless entry point.

Vercel looks for an `app` variable (ASGI) in this file.
All HTTP requests are rewritten here by vercel.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on the Python path so that
# `interface`, `api`, `services`, and `app` packages are importable.
sys.path.insert(0, str(Path(__file__).parent.parent))

from interface.main import app  # noqa: F401, E402 — re-exported for Vercel
