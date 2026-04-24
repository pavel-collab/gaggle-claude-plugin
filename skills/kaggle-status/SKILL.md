---
name: kaggle-status
preamble-tier: 1
version: 1.0.0
description: |
  Show kaggle-claude-plugin pipeline stats: total competitions, pending notify, shown,
  breakdown by type, and last import time.
---

# /kaggle-status

Show pipeline statistics.

## Steps

1. Run:
   ```bash
   python tools/status.py
   ```

2. Format the JSON output as a readable summary table:

```
📊 Kaggle Assistant Status
──────────────────────────
Total saved:      42
  Pending notify: 7
  Shown:          35

By type:
  CLASSIC ML:  18
  LLM/NLP:     15
  CV:           9

Last import: 2026-04-24 14:30 (3.2h ago)
  Fetched: 120 | Saved new: 5
```

3. If DB is empty (total=0), suggest running `/kaggle-import`.
4. If `pending_notify` is 0, suggest running `/kaggle-import` or note all are shown.
5. If `last_import` is null, note that no import has been run yet.
