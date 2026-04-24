---
name: kaggle-notify
preamble-tier: 2
version: 1.0.0
description: |
  Translate pending Kaggle competitions to Russian and send formatted HTML notifications to Telegram.
  Marks each sent competition as shown.
---

# /kaggle-notify

Translate pending competitions to Russian and send to Telegram.

## Steps

1. **Get pending** competitions:
   ```bash
   python tools/get_pending.py --limit 5
   ```
   Prints JSON array sorted by deadline. If empty — report "No pending competitions" and stop.

2. **For each competition** in the list:

   a. **Translate** the `description` field to Russian. Write a concise, informative translation (3–5 sentences max). Focus on: what data is provided, what to predict, evaluation metric if mentioned.

   b. **Send to Telegram** by piping JSON to send_telegram.py:
      ```bash
      python tools/send_telegram.py << 'EOF'
      {
        "title": "...",
        "link": "...",
        "deadline": "...",
        "competition_type": "...",
        "description_ru": "Перевод описания..."
      }
      EOF
      ```

   c. **Mark as shown**:
      ```bash
      python tools/mark_shown.py --title "Exact Competition Title"
      ```

3. **Report**: how many sent successfully, any errors.

## Notes
- Stop on first Telegram error (don't mark as shown if send failed).
- If `get_pending.py` returns empty list, suggest running `/kaggle-import` first.
- Translate description faithfully but concisely — Telegram messages should be readable, not academic.
