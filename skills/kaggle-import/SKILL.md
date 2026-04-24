---
name: kaggle-import
preamble-tier: 2
version: 1.0.0
description: |
  Fetch Kaggle competitions from the API, classify them (CLASSIC ML / LLM/NLP / CV / Other),
  and save non-Other competitions to the local SQLite DB as pending_notify.
---

# /kaggle-import

Fetch Kaggle competitions, classify them, and save to local DB.

## Steps

1. **Fetch** raw competitions from Kaggle API:
   ```bash
   python tools/fetch_competitions.py
   ```
   This prints a JSON array of competitions. Each has: `title`, `link`, `date_start`, `deadline`, `description`, `tags`.

2. **Classify** each competition using your judgment. For each item in the JSON, assign one of:
   - `CLASSIC ML` — tabular data, gradient boosting, feature engineering, structured data
   - `LLM/NLP` — language models, text tasks, RAG, NLP, transformers
   - `CV` — images, video, object detection, segmentation, computer vision
   - `Other` — anything else (robotics, simulations, pure math, games, etc.)

   Add field `"competition_type"` to each object.

3. **Filter**: remove all items with `competition_type: "Other"` from the list.

4. **Save** the classified (non-Other) list by piping JSON to save_classifications.py:
   ```bash
   python tools/save_classifications.py << 'EOF'
   [
     {"title": "...", "link": "...", "competition_type": "LLM/NLP", ...},
     ...
   ]
   EOF
   ```
   The script prints a summary JSON: `{"fetched": N, "saved_new": M, "updated": K, "skipped_other": J}`.

5. **Report** to user:
   - How many fetched total
   - How many classified per category
   - How many new saved vs updated vs skipped

## Notes
- Run from the plugin root directory: `cd /path/to/kaggle-claude-plugin`
- If fetch fails (credentials missing), remind user to copy `tools/.credentials.example` → `tools/.credentials` and fill in values.
- `save_classifications.py` is idempotent: re-importing already-saved competitions updates metadata without changing their notification status.
