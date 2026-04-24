#!/usr/bin/env python3
"""
Fetch active Kaggle competitions and print JSON to stdout.

Reads credentials from tools/.credentials (KAGGLE_USERNAME, KAGGLE_KEY).
Outputs JSON array to stdout. Errors go to stderr.

Usage:
    python tools/fetch_competitions.py
    python tools/fetch_competitions.py --limit 50
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".credentials")

MAX_PAGE_NUMBER = 10
PAGE_SIZE = 100
MIN_DAYS_UNTIL_DEADLINE = 7


def fetch() -> list[dict]:
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()

    competitions = []
    page = 1
    today = datetime.now()

    while True:
        batch = api.competitions_list(
            page=page,
            page_size=PAGE_SIZE,
            search="",
            category="all",
            sort_by="latestDeadline",
        )

        if not batch or not batch.competitions:
            break

        for c in batch.competitions:
            deadline_dt = c.deadline
            if deadline_dt < today:
                continue
            if deadline_dt - today < timedelta(days=MIN_DAYS_UNTIL_DEADLINE):
                continue
            competitions.append(c)

        page += 1
        if page >= MAX_PAGE_NUMBER:
            break

    result = []
    for c in competitions:
        description = c.description or ""
        tag_descs = [t.description for t in (c.tags or []) if t.description]
        if tag_descs:
            description += "\n\n" + "\n\n".join(tag_descs)

        tags = ", ".join(t.ref for t in (c.tags or []) if t.ref)
        link = c.ref if c.ref.startswith("http") else f"https://www.kaggle.com/{c.ref.lstrip('/')}"

        result.append({
            "title": c.title,
            "link": link,
            "date_start": c.enabled_date.strftime("%Y-%m-%d") if c.enabled_date else "",
            "deadline": c.deadline.strftime("%Y-%m-%d"),
            "description": description,
            "tags": tags,
        })

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50, help="Max competitions to return")
    args = parser.parse_args()

    try:
        competitions = fetch()
        competitions = competitions[: args.limit]
        print(json.dumps(competitions, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
