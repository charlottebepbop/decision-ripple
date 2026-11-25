---
type: Signal
name: {{title}}
title: ""
date: {{date}}
source: ""
BREAKS:
  - "[[Assumption/assumption-slug]]"
---

# What happened, in one line.

## Filling this in

Delete this section when the note is done, then run `python3 scripts/check_vault.py`.

Recording a fact with `python3 scripts/add_signal.py` writes this note for you. Use the template when you are writing it by hand.

- Name the file `<date>-<slug>`, for example `2026-12-01-finance-cuts-the-q1-budget-by-20`, then insert this template. `name` must match that filename without `.md`. The script cuts the slug at 60 characters and drops a hyphen left at the cut.
- `source` is where it came from: a report, a memo, an email. `date` is `YYYY-MM-DD`.
- Point the link at an assumption slug. Keep one of these headers and delete the ones you are not using:
  - `CONFIRMS` — the assumption held.
  - `SUPPORTS` — evidence for it, not proof.
  - `WEAKENS` — it is under pressure.
  - `BREAKS` — it no longer holds.
- The link is quoted: `"[[Assumption/assumption-slug]]"`. A link to a missing note makes Relate create an empty file. `python3 scripts/list_slugs.py assumption` lists the real slugs.
