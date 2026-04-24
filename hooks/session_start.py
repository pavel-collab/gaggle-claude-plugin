#!/usr/bin/env python3
"""
SessionStart hook: inject import reminder if >24h since last import.

Outputs hookSpecificOutput JSON for Claude Code to inject into context.
Outputs nothing if import is not yet due.
"""

import json
import subprocess
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent.parent
TOOLS_DIR = PLUGIN_DIR / "tools"
PYTHON = sys.executable


def main() -> None:
    try:
        result = subprocess.run(
            [PYTHON, str(TOOLS_DIR / "check_schedule.py")],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return

        data = json.loads(result.stdout)
        if not data.get("should_import"):
            return

        hours = data.get("hours_since_last")
        if hours is None:
            time_msg = "Импорт ещё не выполнялся"
        else:
            time_msg = f"Последний импорт был {hours:.1f} ч. назад"

        pending_result = subprocess.run(
            [PYTHON, str(TOOLS_DIR / "status.py")],
            capture_output=True,
            text=True,
            timeout=10,
        )
        pending_info = ""
        if pending_result.returncode == 0:
            stats = json.loads(pending_result.stdout)
            pending_info = f" В базе {stats.get('pending_notify', 0)} ожидают отправки."

        context = (
            f"[kaggle-assistant] {time_msg}.{pending_info} "
            f"Рекомендую выполнить /kaggle-import для обновления списка соревнований."
        )

        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }))

    except Exception:
        pass


if __name__ == "__main__":
    main()
