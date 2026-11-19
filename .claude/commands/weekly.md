---
description: Write this week's decision briefing from the vault, short enough to read in a couple of minutes
argument-hint: "[--since YYYY-MM-DD] [--as-of YYYY-MM-DD] [--review-after N]"
disable-model-invocation: true
allowed-tools: Bash(python3 scripts/weekly.py:*)
disallowed-tools: Write, Edit
---

Write the weekly briefing and show it. You are talking to someone on the business side. The briefing is the thing they read. Do not rewrite its sections, and do not add a decision or a signal from it.

The words after the command are flags, if any:

$ARGUMENTS

Leave `DECISION_VAULT` and `DECISION_BRIEFS` as they are. The script reads the notes folder and writes `weekly-<as-of>.md` into the briefs folder. It does not change the notes.

Pass flags only. Turn a date they say in words into `--since` or `--as-of` as `YYYY-MM-DD`. "Last 14 days" is `--since` set to 14 days before `--as-of`. "Review anything quiet for 30 days" is `--review-after 30`. When they name no date, pass no flags. The window is then the 7 days before today, through today. Assumptions with no signal in 90 days are worth a review.

From the repo root:

```bash
python3 scripts/weekly.py
```

The first line of the output is the vault folder. When that folder is this repo's `vault/`, say the briefing is the Kestrel sample. The last line is the brief file. Show the markdown between those two lines.

When they want to record something they saw in the briefing, point them at `/log-signal` or `/log-decision`. Do not write it yourself.
