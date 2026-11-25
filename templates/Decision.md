---
type: Decision
name: {{title}}
title: ""
date: {{date}}
confidence: medium
status: live
RESTS_ON:
  - "[[Assumption/supporting-assumption-slug]]"
  - weight: critical
    target: "[[Assumption/critical-assumption-slug]]"
STEERS:
  - "[[Project/project-slug]]"
DECIDED_BY:
  - "[[Person/person-slug]]"
---

# Decision title

**Rationale:** Why this was decided.

## Filling this in

Delete this section when the note is done, then run `python3 scripts/check_vault.py`.

- Create the note with a slug as the filename, then insert this template. `name` is that filename (`{{title}}` fills it in). `name` has to match the filename without `.md`. If you rename the file, change `name` too. A mismatch makes Relate refuse every query.
- `status: live` is required. The ripple, the tell list, and the already-broken view keep only decisions with `status: live`. A missing status drops this decision out of all three. Use `superseded` only when a newer decision replaces this one.
- `confidence` is `low`, `medium`, or `high`. `date` is `YYYY-MM-DD`. If Obsidian inserted a different date shape, type the date yourself.
- Put the sentence people read in `title` and in the heading. The filename stays the slug. `python3 scripts/list_slugs.py` prints slugs.
- A supporting assumption is the bare link under `RESTS_ON`. A critical one (this decision fails without it) uses `weight: critical` and `target`. The only weight is `critical`. Leave the bare link in place: the vault needs at least one bare `RESTS_ON` somewhere, or Relate will not open a note that uses the weight form.
- Links are quoted and look like `"[[Assumption/assumption-slug]]"`. The folder is `Decision`, `Assumption`, `Person`, `Project`, or `Signal`. No spaces, and no `#heading`.
- Point `STEERS` at a project and `DECIDED_BY` at the person who decided. Replace every `...-slug` with a real filename from `list_slugs.py`.
