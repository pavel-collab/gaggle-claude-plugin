#!/usr/bin/env bash
# kaggle-claude-plugin installer
# Run once from the plugin directory: bash install.sh

set -e

PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DST="$HOME/.claude/skills"

echo "=== kaggle-claude-plugin installer ==="
echo "Plugin dir: $PLUGIN_DIR"
echo ""

# ── 1. Virtual environment ──────────────────────────────────────────────────
echo "[1/4] Creating Python virtual environment..."
python3 -m venv "$PLUGIN_DIR/.venv"
"$PLUGIN_DIR/.venv/bin/pip" install -q --upgrade pip
"$PLUGIN_DIR/.venv/bin/pip" install -q -r "$PLUGIN_DIR/requirements.txt"
echo "      OK — .venv created, deps installed"

# ── 2. Credentials ──────────────────────────────────────────────────────────
echo "[2/4] Setting up credentials..."
CREDS="$PLUGIN_DIR/tools/.credentials"
if [ ! -f "$CREDS" ]; then
    cp "$PLUGIN_DIR/tools/.credentials.example" "$CREDS"
    echo ""
    echo "  ⚠️  ACTION REQUIRED: fill in $CREDS"
    echo "       KAGGLE_USERNAME, KAGGLE_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID"
    echo ""
else
    echo "      OK — credentials file already exists"
fi

# ── 3. Skills → ~/.claude/skills/ ───────────────────────────────────────────
echo "[3/4] Installing skills to $SKILLS_DST..."
mkdir -p "$SKILLS_DST"
for skill_dir in "$PLUGIN_DIR/skills"/*/; do
    skill_name="$(basename "$skill_dir")"
    mkdir -p "$SKILLS_DST/$skill_name"
    cp "$skill_dir/SKILL.md" "$SKILLS_DST/$skill_name/SKILL.md"
    echo "      /$(echo "$skill_name" | sed 's/kaggle-/kaggle-/') → installed"
done

# ── 4. SessionStart hook → ~/.claude/settings.json ──────────────────────────
echo "[4/4] Registering SessionStart hook..."
"$PLUGIN_DIR/.venv/bin/python" "$PLUGIN_DIR/install_hook.py"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "=== Installation complete ==="
echo ""
echo "Next steps:"
echo "  1. Fill in credentials:  $CREDS"
echo "  2. Restart Claude Code (hooks are loaded at startup)"
echo "  3. Open any Claude Code session and run: /kaggle-status"
echo ""
echo "All tools must be run from the plugin directory:"
echo "  cd $PLUGIN_DIR"
