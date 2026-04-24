#!/usr/bin/env python3
"""
Save Claude's classified competitions to SQLite.

Reads JSON from stdin. Expected format:
[
  {
    "title": "Competition Title",
    "link": "https://www.kaggle.com/competitions/...",
    "date_start": "2026-01-01",
    "deadline": "2026-06-01",
    "description": "...",
    "tags": "nlp, text",
    "competition_type": "LLM/NLP"
  },
  ...
]

Only saves competitions with competition_type in: CLASSIC ML, LLM/NLP, CV.
Other is silently skipped (as per plugin convention).

Usage:
    echo '[...]' | python tools/save_classifications.py
    python tools/save_classifications.py < classified.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import db

VALID_TYPES = {"CLASSIC ML", "LLM/NLP", "CV"}


def main() -> None:
    db.init_db()

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}), file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print(json.dumps({"error": "Expected JSON array"}), file=sys.stderr)
        sys.exit(1)

    fetched_count = len(data)
    saved_count = 0
    skipped_other = 0
    updated_count = 0

    for item in data:
        comp_type = item.get("competition_type", "Other")
        if comp_type not in VALID_TYPES:
            skipped_other += 1
            continue

        is_new = db.upsert_competition(
            title=item.get("title", ""),
            link=item.get("link", ""),
            date_start=item.get("date_start", ""),
            deadline=item.get("deadline", ""),
            description=item.get("description", ""),
            tags=item.get("tags", ""),
            competition_type=comp_type,
        )
        if is_new:
            saved_count += 1
        else:
            updated_count += 1

    db.log_import(fetched_count=fetched_count, saved_count=saved_count)

    result = {
        "fetched": fetched_count,
        "saved_new": saved_count,
        "updated": updated_count,
        "skipped_other": skipped_other,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
