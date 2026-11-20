---
type: Project
name: {{title}}
title: ""
OWNED_BY:
  - "[[Person/person-slug]]"
STAKEHOLDER:
  - "[[Person/person-slug]]"
---

# Project title

## Filling this in

Delete this section when the note is done, then run `python3 scripts/check_vault.py`.

- Create the note with a slug as the filename (`hub-2-rotterdam-south`), then insert this template. `name` must match that filename without `.md`. `title` is the name people say out loud.
- `OWNED_BY` is the person accountable for the project. `STAKEHOLDER` is who else has to hear when a decision on this project is at risk. Both are quoted links: `"[[Person/person-slug]]"`.
- A decision lists this note under `STEERS`. The pre-check takes the project slug: `--param project=hub-2-rotterdam-south`.
