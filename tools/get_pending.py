#!/usr/bin/env python3
"""
Get competitions pending Telegram notification.

Outputs JSON array sorted by deadline (soonest first).

Usage:
    python tools/get_pending.py
    python tools/get_pending.py --limit 5
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import db


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    db.init_db()

    try:
        competitions = db.get_pending(limit=args.limit)
        print(json.dumps(competitions, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
