#!/usr/bin/env python3
"""
Aggregate plugin stats for /kaggle-status.

Outputs JSON with counts by status and type, plus last import info.

Usage:
    python tools/status.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import db


def main() -> None:
    db.init_db()

    try:
        stats = db.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
