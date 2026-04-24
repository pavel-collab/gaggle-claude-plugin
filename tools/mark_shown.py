#!/usr/bin/env python3
"""
Mark a competition as shown after Telegram notification.

Usage:
    python tools/mark_shown.py --title "Competition Title"
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import db


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="Exact competition title")
    args = parser.parse_args()

    db.init_db()

    try:
        db.mark_shown(args.title)
        print(json.dumps({"ok": True, "title": args.title}))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
