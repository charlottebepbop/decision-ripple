---
description: Draft a decision from this conversation or a pasted memo, check slugs, and write it only after confirmation
argument-hint: "[memo, or leave empty to use the conversation]"
disable-model-invocation: true
allowed-tools: Bash(python3 scripts/list_slugs.py:*), Bash(python3 scripts/add_decision.py:*), Bash(python3 scripts/check_vault.py:*)
disallowed-tools: Write, Edit
---

Draft a decision note and write it only after the user confirms. You are talking to someone on the business side who uses this command instead of composing the note by hand.

The words after the command are the memo:

$ARGUMENTS

When that is empty, the memo is the conversation so far. Use only facts the user stated. When a field is missing, ask once, then draft again.

## Notes already in the vault

The first line is the folder the scripts will write to. A decision line ends with `[live]` or `[superseded]`.

!`python3 scripts/list_slugs.py`

Run `python3 scripts/list_slugs.py` again from the repo root if you need one label on its own (`assumption`, `person`, `project`, `decision`). The scripts read `DECISION_VAULT`. Leave that variable as it is. When the vault line is this repo's `vault/`, say so in the draft: confirming will write the Kestrel sample.

## Resolve every link before the draft

Fields follow `templates/Decision.md`. The script writes them. Do not copy the template into the notes folder, and do not leave its "Filling this in" section in the note.

- Title: the decision in one sentence.
- Date: the day the user gave, as `YYYY-MM-DD`. Otherwise today, and say you used today.
- Confidence: `low`, `medium`, or `high`. Use `medium` when the user did not say, and say so.
- Rationale: why this was decided.
- Context: the situation. Omit it when the memo has none. Do not invent it.
- Options considered: each option the memo names, as its own `--option`. Mark the one chosen and why the others lost, using the user's words. When the memo names no alternative, one bullet for the choice is enough, and say that no alternative was stated.
- Who decided: the people the user said decided, as prose for `--who-decided`, and as `--by` slugs.
- Project: a slug from the Project list, passed to `--project`. When no project matches, stop and show the Project list. This command does not create projects.
- Assumptions: each one the decision needs. Critical means the decision fails without it (`--rests-on slug:critical`). Anything else is supporting (`--rests-on slug`). The vault needs one bare supporting `RESTS_ON` somewhere. On the first decision in an empty vault, keep at least one assumption supporting.
- Supersedes or amends: a replacement of a `[live]` decision is `--supersedes`. A change that keeps the old decision live is `--amends`. Pass neither when this decision stands on its own. When the named decision is `[superseded]`, do not pass it. Ask which live decision to replace.

Match people, projects, assumptions, and decisions to slugs in the list above. Match on the slug and on the title, statement, or role printed under it.

- A slug in that list is an existing note. Pass that slug.
- A name that is only close to a slug (for example `q1-budget-hold` next to `q1-budget-holds`, or `ines-varga-ceo` next to `ines-varga`) is a typo. Propose the existing slug and say the other name is not a note. Do not create it.
- An assumption or a person that matches nothing is new. Show the slug you will create, the statement or the name and role, and the word new. Create it only with `--new-assumption SLUG "statement"` or `--new-person SLUG "Display Name" "Role"`, and only after the user agrees. The new assumption also goes in `--rests-on`. The new person also goes in `--by`.
- Two plausible slugs means you ask which one. Do not pick silently.

## Show the draft, then wait

Run the `add_decision.py` command you would write, with `--dry-run` on the end. Fix the flags if it exits with an error, and run it again. Show the user the dry-run output. Above it, add a short note for any slug you corrected and any note marked new. When the vault line is the sample `vault/`, warn that a yes writes into the sample.

Then stop. Ask them to confirm or to tell you what to change. A yes is "yes", "write it", or "confirm". Anything else is an edit: change the draft, dry-run again, and ask again. Do not run the script without `--dry-run` until they say yes.

## Write, then check

After a yes, run the same command without `--dry-run`. Show the decision path and the precheck it prints. Then run:

```bash
python3 scripts/check_vault.py
```

Quote any problem it prints, including the fix line. Leave the note in place for the user to decide. Do not edit the file yourself.

The shell shape, omitting any flag the draft does not use:

```bash
python3 scripts/add_decision.py "TITLE" \
  --date YYYY-MM-DD \
  --confidence medium \
  --project project-slug \
  --by person-slug \
  --rests-on assumption-slug:critical \
  --rests-on assumption-slug \
  --new-assumption new-slug "The assumption, as one sentence." \
  --new-person new-slug "Display Name" "Role" \
  --supersedes live-decision-slug \
  --rationale "Why this was decided." \
  --context "The situation." \
  --option "The option that was chosen." \
  --option "Another option. Lost because ..." \
  --who-decided "Who decided, in a sentence." \
  --dry-run
```
