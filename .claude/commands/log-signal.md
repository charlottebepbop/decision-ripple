---
description: Draft a signal from this conversation or a pasted memo, write it after confirmation, and suggest a follow-up decision when the memo states one
argument-hint: "[memo, or leave empty to use the conversation]"
disable-model-invocation: true
allowed-tools: Bash(python3 scripts/list_slugs.py:*), Bash(python3 scripts/add_signal.py:*), Bash(python3 scripts/check_vault.py:*)
disallowed-tools: Write, Edit
---

Draft a signal and write it only after the user confirms. A signal is a fact from a report, a memo, or a notice. It confirms, supports, weakens, or breaks an assumption that already exists. You are talking to someone on the business side who uses this command instead of composing the note by hand.

The words after the command are the memo:

$ARGUMENTS

When that is empty, the memo is the conversation so far. Use only facts the user stated.

## Assumptions already in the vault

The first line is the folder the script will write to. Link only to an assumption slug this list prints.

!`python3 scripts/list_slugs.py assumption decision`

Run `python3 scripts/list_slugs.py assumption` again from the repo root when you need a fresh list. Leave `DECISION_VAULT` and `DECISION_BRIEFS` as they are. When the vault line is this repo's `vault/`, say so before they confirm.

## Resolve the signal

Fields follow `templates/Signal.md`. `scripts/add_signal.py` writes the note. Do not copy the template into the notes folder.

- Title: what happened, in one line.
- Date: the day the user gave, as `YYYY-MM-DD`. Otherwise today, and say you used today.
- Source: where it came from. Ask when the memo does not name one. Do not invent a source.
- Each assumption it hits, and one effect: `CONFIRMS` (it held), `SUPPORTS` (evidence, not proof), `WEAKENS` (under pressure), or `BREAKS` (it no longer holds). The first pair is the positional arguments. Further pairs are `--and SLUG EFFECT`.

Match the memo to an assumption slug and to the statement printed under it.

- A slug in the list is the note to pass.
- A name that is only close to a slug is a typo. Propose the existing slug and say the other name is not a note.
- An assumption that matches nothing is not created here. A signal needs an assumption a decision already rests on. Say no assumption matched, show the closest statements, and stop. When the memo is really a decision, point them at `/log-decision`.
- Two plausible slugs means you ask which one.

## Show the draft, then wait

Run `add_signal.py` with `--dry-run`. Show that output. Above it, note any slug you corrected. When the dry run fails, fix the slug and run it again. Do not write.

Then stop. Ask them to confirm or to tell you what to change. A yes is "yes", "write it", or "confirm". Anything else is an edit: dry-run again and ask again.

## Write, then check, then the brief

After a yes, run the same command without `--dry-run`. The script prints the brief. Show it.

Then run:

```bash
python3 scripts/check_vault.py
```

Quote any problem it prints, including the fix line. Do not edit the file yourself.

## Suggest a follow-up decision, and do not write it

After the brief:

- When every effect is `SUPPORTS` or `CONFIRMS`, stop after the brief. No replacement is implied.
- When an effect is `BREAKS` or `WEAKENS`, name the live decisions in the brief and the weight on each.
- When the memo also states a decision the user says was made (a change of plan, a date that moved, a choice that replaces a live decision), print a follow-up draft: title, who decided, which `[live]` decision it supersedes or amends, rationale, and the assumptions it would rest on. Tell them to run `/log-decision` with that memo. Do not run `add_decision.py`.
- When the memo does not state a new decision, say those live decisions need a second look, and stop.

```bash
python3 scripts/add_signal.py assumption-slug BREAKS "What happened, in one line" \
  --and other-assumption-slug WEAKENS \
  --source "Board memo" \
  --date YYYY-MM-DD \
  --dry-run
```
