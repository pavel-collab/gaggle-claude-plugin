---
name: kaggle-review
preamble-tier: 2
version: 1.0.0
description: |
  Interactively review pending Kaggle competitions before sending to Telegram.
  For each: send now, keep pending, or reclassify.
---

# /kaggle-review

Interactive review of pending competitions before sending to Telegram.

Lets you preview each competition and decide: send now, skip, or reclassify.

## Steps

1. **Get pending** competitions:
   ```bash
   python tools/get_pending.py --limit 20
   ```

2. **For each competition**, display:
   - Title
   - Type (CLASSIC ML / LLM/NLP / CV)
   - Deadline
   - Link
   - Description (first 300 chars)

3. **Ask user** what to do with each:
   - `s` / send — translate description and send to Telegram now (runs /kaggle-notify logic for this one)
   - `k` / keep — leave as pending_notify for later
   - `r` / reclassify — change competition_type
   - `x` / skip all — stop review

4. For `send` action: translate description, send via `send_telegram.py`, then mark shown via `mark_shown.py`.

5. **Summary** at the end: how many sent, kept, reclassified.

## Notes
- This is an interactive skill — ask the user one competition at a time, or show all and let them pick by number.
- Prefer showing all competitions first, then processing user's choices.
- Deadline sorting (soonest first) is already handled by get_pending.py.
