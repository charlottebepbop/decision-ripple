---
type: Assumption
name: {{title}}
statement: ""
---

# The assumption, as a sentence.

## Filling this in

Delete this section when the note is done, then run `python3 scripts/check_vault.py`.

- Create the note with a slug as the filename (`ops-data-complete`), then insert this template. `name` must match that filename without `.md`. If you rename the file, change `name` and every link that points here.
- `statement` is the sentence a decision assumed. Repeat it as the heading.
- A decision lists this note under `RESTS_ON`. Until one does, the vault check says this assumption has no owner.
- Signals link here with `CONFIRMS`, `SUPPORTS`, `WEAKENS`, or `BREAKS`. Those links use the slug, not the statement. `python3 scripts/list_slugs.py assumption` prints it.
