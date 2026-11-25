# Note templates

These are Obsidian templates for the five note types. The folder name is the label Relate stores: `Decision`, `Assumption`, `Person`, `Project`, `Signal`.

`scripts/init_vault.py` copies this folder into `.obsidian/templates` inside a new vault. Relate skips folders whose names start with a dot, so that copy does not become notes. If you open this repo as the Obsidian vault, set the template folder to `templates` (this directory). Do not copy these files into `vault/` or into your notes folder under any other name: a markdown file there becomes a note, and the folder name becomes its label.

In Obsidian: Settings → Core plugins → Templates, then set the template folder. Create the note **with the slug as its filename**, then insert the template. `{{title}}` becomes that filename. `{{date}}` becomes today's date. If your Obsidian date format is not `YYYY-MM-DD`, type the date yourself.

## Rules that apply to every note

- `name` must match the filename without `.md`. `name: ops-data-complete` lives in `ops-data-complete.md`. If you rename the file, change `name` to the new filename and update every link. A mismatch makes Relate refuse every query, with: key property `name` does not match its filename.
- The slug is that filename, not the human title. Queries and `scripts/add_signal.py` take the slug. `python3 scripts/list_slugs.py` prints them.
- Links are quoted wikilinks: `"[[Assumption/ops-data-complete]]"`. The folder is `Decision`, `Assumption`, `Person`, `Project`, or `Signal`, with that capitalisation. No spaces in the path, and no `#heading`. An unquoted link in the header makes Relate reject the note. A link to a missing note makes Relate create an empty file, and the vault then looks connected when it is not.
- After you edit, run `python3 scripts/check_vault.py`. With `DECISION_VAULT` set, that checks your folder. The message names the file and the change to make.

## Decision

- `status: live` is required for a decision you still stand by. The ripple, the tell list, and the already-broken view keep only `status: live`. A missing status drops the decision out of all three. Use `superseded` only when a newer decision links to this one with `SUPERSEDES`.
- `confidence` is `low`, `medium`, or `high`.
- `date` is `YYYY-MM-DD`.
- A decision rests on at least one assumption, steers at least one project, and names who decided.
- Supporting `RESTS_ON` is a bare quoted link. Critical `RESTS_ON` (the decision fails without that assumption) is the map form, and the only weight is `critical`:

```yaml
RESTS_ON:
  - "[[Assumption/supporting-assumption-slug]]"
  - weight: critical
    target: "[[Assumption/critical-assumption-slug]]"
```

The vault needs at least one bare `RESTS_ON` link somewhere. If every `RESTS_ON` uses the weight form, Relate refuses to open the vault.

## Assumption

`statement` is the sentence the decision assumed. A signal confirms, supports, weakens, or breaks that sentence. Some decision has to list this note under `RESTS_ON`, or the vault check says the assumption has no owner.

## Person

`role` is required. The heading is the person's name. Two person notes with the same heading split the tell list.

## Project

`title` is the project name people say out loud. `name` is the slug, such as `hub-2-rotterdam-south`. `OWNED_BY` is the person who owns it. `STAKEHOLDER` lists the others who need to hear about it.

## Signal

`source` is where the fact came from (a report, a memo, an email). `date` is `YYYY-MM-DD`. The signal links to an assumption with one of:

- `CONFIRMS` — the assumption held.
- `SUPPORTS` — evidence for it, not proof.
- `WEAKENS` — it is under pressure.
- `BREAKS` — it no longer holds.

One signal can carry more than one of those. `scripts/add_signal.py` writes this note for you and is the usual way to record a fact. The filename it writes is `<date>-<slug>`. The slug is the title in lower case, cut at 60 characters, with a hyphen at the cut removed.
