#!/usr/bin/env python3
"""Command-line entry point. The implementation lives in luxembourgish_lod/verify.py;
this shim lets the skill layout call scripts/verify.py without installing the package."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from luxembourgish_lod.verify import main  # noqa: E402

if __name__ == "__main__":
    main()
