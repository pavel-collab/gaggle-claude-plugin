#!/usr/bin/env python3
"""
Send a Kaggle competition notification to Telegram.

Reads competition data from stdin as JSON:
{
  "title": "...",
  "link": "https://...",
  "deadline": "2026-06-01",
  "competition_type": "LLM/NLP",
  "description_ru": "Русское описание..."
}

Reads credentials from tools/.credentials (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID).

Usage:
    echo '{...}' | python tools/send_telegram.py
    python tools/send_telegram.py < competition.json
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".credentials")

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_message(token: str, chat_id: str, text: str) -> dict:
    url = TELEGRAM_API.format(token=token)
    resp = requests.post(
        url,
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def format_message(data: dict) -> str:
    title = data.get("title", "")
    link = data.get("link", "")
    deadline = data.get("deadline", "")
    comp_type = data.get("competition_type", "")
    description_ru = data.get("description_ru", "")

    return (
        f"<b>Kaggle соревнование:</b>\n\n"
        f"<b>Title:</b> {title}\n"
        f"<b>Link:</b> {link}\n"
        f"<b>Deadline:</b> {deadline}\n"
        f"<b>Theme:</b> {comp_type}\n\n"
        f"<b>Описание:</b>\n{description_ru}"
    )


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print(json.dumps({"error": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set"}), file=sys.stderr)
        sys.exit(1)

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}), file=sys.stderr)
        sys.exit(1)

    try:
        text = format_message(data)
        result = send_message(token, chat_id, text)
        print(json.dumps({"ok": True, "message_id": result.get("result", {}).get("message_id")}))
    except requests.HTTPError as e:
        print(json.dumps({"error": f"Telegram API error: {e}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
