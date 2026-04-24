---
name: kaggle-classify
preamble-tier: 2
version: 1.0.0
description: |
  Reclassify one or more saved Kaggle competitions without re-fetching from the API.
  Used to correct misclassifications interactively.
---

# /kaggle-classify

Reclassify one or more competitions already in the DB.

This skill is for correcting misclassifications without re-fetching from the API.

## Usage

- `/kaggle-classify` — show all saved competitions with their current type, ask which to reclassify
- `/kaggle-classify "Competition Title"` — reclassify specific competition

## Steps

1. **Get current state**:
   ```bash
   python tools/status.py
   ```
   And list pending competitions:
   ```bash
   python tools/get_pending.py --limit 50
   ```

2. **Show** the user the list with titles and current types. Ask which to reclassify, or accept the title from the command argument.

3. **Reclassify**: for each selected competition, ask the user for the new type (or determine yourself if obvious from title/description).

4. **Update** by calling save_classifications.py with the corrected data (it does upsert — will update type, keep status):
   ```bash
   python tools/save_classifications.py << 'EOF'
   [
     {
       "title": "Exact Title",
       "link": "https://...",
       "date_start": "...",
       "deadline": "...",
       "description": "...",
       "tags": "...",
       "competition_type": "CV"
     }
   ]
   EOF
   ```

5. **Confirm** the update to the user.

## Notes
- Valid types: `CLASSIC ML`, `LLM/NLP`, `CV`.
- If user changes type to `Other`, the competition stays in DB with its current status — no auto-delete.
- Reclassification does not reset notification status.
