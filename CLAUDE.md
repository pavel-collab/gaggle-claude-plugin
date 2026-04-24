# kaggle-claude-plugin

Claude Code plugin for automated Kaggle competition monitoring, classification, and Telegram notifications.

## What This Is

A Claude Code plugin — not a skill (prompt-only) and not an MCP server (tool-only).
A plugin bundles **skills** (slash commands), **hooks** (lifecycle automation), and **tools** (credential-isolated shell scripts) into one installable package.

Claude handles all ML logic: competition analysis, classification, translation.
Credentials (Kaggle API, Telegram) are stored in `.credentials` and never exposed to Claude's context.

## Plugin Structure

```
kaggle-claude-plugin/
├── manifest.json               # Plugin metadata and entry point
├── CLAUDE.md                   # This file
├── skills/
│   ├── kaggle-import/
│   │   └── SKILL.md            # /kaggle-import — fetch + classify competitions
│   ├── kaggle-classify/
│   │   └── SKILL.md            # /kaggle-classify [id] — reclassify a competition
│   ├── kaggle-notify/
│   │   └── SKILL.md            # /kaggle-notify — translate + send to Telegram
│   ├── kaggle-status/
│   │   └── SKILL.md            # /kaggle-status — pipeline stats
│   └── kaggle-review/
│       └── SKILL.md            # /kaggle-review — interactive top competitions review
├── hooks/
│   └── hooks.json              # SessionStart: check schedule, suggest /kaggle-import
├── tools/
│   ├── fetch_competitions.py   # Kaggle API → JSON stdout (reads credentials internally)
│   ├── save_classifications.py # Write Claude's classifications to local DB (SQLite)
│   ├── get_pending.py          # Read competitions pending notification
│   ├── mark_shown.py           # Mark competition as shown after Telegram send
│   ├── send_telegram.py        # Send formatted HTML message to Telegram
│   ├── check_schedule.py       # Check if 24h passed since last import
│   ├── status.py               # Aggregate stats for /kaggle-status
│   └── db.py                   # SQLite schema and helpers
├── .credentials.example        # Template — copy to .credentials and fill in
└── requirements.txt            # Python deps for tools/
```

## Data Flow

```
/kaggle-import:
  fetch_competitions.py (Kaggle API) → JSON → Claude classifies → save_classifications.py → SQLite

/kaggle-notify:
  get_pending.py (SQLite) → JSON → Claude translates + formats → send_telegram.py (Telegram API)

/kaggle-status:
  status.py → stats JSON → Claude renders summary table

SessionStart hook:
  check_schedule.py → if >24h since last import → inject reminder into Claude context
```

## Credential Isolation

Credentials live in `tools/.credentials` (gitignored). Claude **cannot** read this file — a `PreToolUse` hook blocks any Read/Bash access to `.credentials`. Scripts load credentials via `python-dotenv` internally and only print structured JSON to stdout.

```
tools/.credentials
  KAGGLE_USERNAME=...
  KAGGLE_KEY=...
  TELEGRAM_BOT_TOKEN=...
  TELEGRAM_CHAT_ID=...
```

## Competition Status Flow

```
fetched → classified → pending_notify → shown
```

Stored in SQLite (`tools/kaggle.db`, gitignored). Schema mirrors the main project's PostgreSQL model but simplified for local plugin use.

## Classification Labels

- `CLASSIC ML` — tabular data, gradient boosting, feature engineering
- `LLM/NLP` — language models, text tasks, RAG
- `CV` — image/video, object detection, segmentation
- `Other` — filtered out, not stored

## Running the Plugin (Development)

```bash
# Install Python deps
pip install -r requirements.txt

# Configure credentials
cp tools/.credentials.example tools/.credentials
# fill in your keys

# Install plugin into Claude Code
claude plugin install .

# Then use slash commands inside any Claude Code session:
# /kaggle-import
# /kaggle-status
# /kaggle-notify
```

## Knowledge Base

Project knowledge is maintained in an Obsidian vault at:
`/Users/pavelfilippenko/Projects/ProjectsRootVault`

Relevant sections to check at session start:
- `wiki/concepts/` — architectural concepts (RAG, LLM agents, eval strategies)
- `wiki/src-dive-into-claude-code.md` — Claude Code internals (plugin architecture, hooks, compaction)
- `wiki/entities/claude-code.md` — Claude Code component reference

## Development Notes

- All `tools/*.py` scripts are designed to be run standalone (testable without Claude).
- Scripts output JSON to stdout, errors to stderr. Exit code 0 = success, 1 = error.
- Claude receives only stdout. Credentials, stack traces, and debug logs go to stderr.
- SQLite DB path defaults to `tools/kaggle.db`. Override with `KAGGLE_PLUGIN_DB` env var.
- Scheduled import uses `check_schedule.py` via SessionStart hook — no external cron needed.
