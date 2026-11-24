---
name: build-lead
description: Plan and run a multi-step build in this repo as a lead that writes no code. Use when the user says /build-lead, "plan the build" or "run the plan". Not for questions about the decision graph; CLAUDE.md covers those.
---

# Build lead

Two modes. `plan` writes one plan file. `run` builds from it in a fresh session.
The plan file lives in `plans/<slug>.md`. It is the only place build state is kept.

## plan

1. Write the goal as a user story with acceptance criteria. Ask the user about anything unclear before planning.
2. Read the code, queries and scripts the work touches. For each one, find what depends on it. If you can't tell, ask.
3. List what a fresh session must read first: file, line numbers, why.
4. Split the work into tasks by file. No two tasks in one checkpoint share a file.
   Each task names: files, change, code to copy (file and line), known pitfalls, the command that proves it.
   Mark which tasks run in parallel. Give the reason when one has to wait.
5. Group tasks into checkpoints. Each checkpoint works on its own and names its check. Skip checkpoints for a one-step change.
6. For each acceptance criterion, name the test and the one-line change that should make it fail.
7. Give the plan to a fresh subagent. It reads the file and answers four questions:
   does it serve the goal, is it complete, is it safe, can it be built first time.
   Write every finding into the plan, not only into the chat.
8. Tell the user to clear the context and start `run` in a fresh session.

## run

- Read the whole plan first. You write no code.
- At the start of each checkpoint, give each parallel task to its own subagent, all in one message.
  Use the brief below. Read-only tasks with a checkable answer use `model: sonnet`.
- Check the files, never the report. A mismatch goes back to its subagent.
- For each new test: make its one-line break, confirm it fails, undo with the exact reverse edit. Never reset files.
- You alone run the checkpoint's check and commit, and only when the user has said to commit.
  Write the result and the evidence into the plan.
- Anything not in the plan goes into the plan before anyone builds it.
- After each checkpoint, if your context is half full, write which checkpoint is next and stop.
- Before you call it done, use it through its real entry point the way a user would.

## Subagent brief

```
Task: <one task from the plan, copied>
Files: <yours, only these. Touch nothing else.>
Read first: <file:lines and why>
Bar: <the command that must pass>
Report, in this format and nothing else:
  changed: <file: one line per change>
  bar: <command> -> <pass | fail + the last 10 lines of output>
  open: <anything you could not do, or none>
Do not run git. Do not write outside your files.
```
