#!/usr/bin/env python3
"""Run the local checkout without installing a package."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "skills/product-lab/scripts"))

from product_lab.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
