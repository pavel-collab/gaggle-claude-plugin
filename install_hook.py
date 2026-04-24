#!/usr/bin/env python3
"""
Add kaggle-claude-plugin SessionStart hook to ~/.claude/settings.json.
Safe: appends to existing hooks array, never overwrites other entries.
"""

import json
import os
import sys
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
PLUGIN_DIR = Path(__file__).parent.resolve()
HOOK_COMMAND = f"{sys.executable} {PLUGIN_DIR}/hooks/session_start.py"


def main() -> None:
    # Read existing settings
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH) as f:
            settings = json.load(f)
    else:
        settings = {}

    hooks = settings.setdefault("hooks", {})
    session_start = hooks.setdefault("SessionStart", [])

    # Check if our hook is already registered
    for entry in session_start:
        for h in entry.get("hooks", []):
            if "session_start.py" in h.get("command", "") and str(PLUGIN_DIR) in h.get("command", ""):
                print("Hook already registered — skipping.")
                return

    # Append our hook entry
    session_start.append({
        "matcher": "",
        "hooks": [{
            "type": "command",
            "command": HOOK_COMMAND,
            "timeout": 15,
        }]
    })

    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Hook registered: {HOOK_COMMAND}")


if __name__ == "__main__":
    main()
