#!/usr/bin/env python3
"""
Check whether a new import should be triggered (>24h since last import).

Outputs JSON:
{
  "should_import": true,
  "hours_since_last": 26.3,
  "last_imported_at": "2026-04-23 14:00:00"
}

If no import has ever been done:
  {"should_import": true, "hours_since_last": null, "last_imported_at": null}

Usage:
    python tools/check_schedule.py
    python tools/check_schedule.py --threshold-hours 12
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import db

DEFAULT_THRESHOLD_HOURS = 24


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold-hours", type=float, default=DEFAULT_THRESHOLD_HOURS)
    args = parser.parse_args()

    db.init_db()

    last = db.get_last_import()

    if last is None:
        print(json.dumps({
            "should_import": True,
            "hours_since_last": None,
            "last_imported_at": None,
        }))
        return

    last_dt = datetime.fromisoformat(last["imported_at"])
    now = datetime.now()
    hours_since = (now - last_dt).total_seconds() / 3600

    print(json.dumps({
        "should_import": hours_since >= args.threshold_hours,
        "hours_since_last": round(hours_since, 1),
        "last_imported_at": last["imported_at"],
    }))


if __name__ == "__main__":
    main()
