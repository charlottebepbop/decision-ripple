# Kestrel decision graph <!-- [C] working title, hers to change -->

<!-- HER WORDS: one-line pitch -->

## Use case

<!-- HER WORDS: the problem, who has it, and why it hurts. 3 to 5 sentences. -->

The sample company is made up: **Kestrel Cargo**, a cargo-bike delivery firm in Rotterdam with
10 people, 8 projects and 24 decisions. The relationships that matter:

- A **decision rests on assumptions**. Some are critical, some only support it.
- A **decision steers projects**, and **people** made it, own the project or hold a stake.
- A **signal** (a report, a memo, a supplier notice) **confirms, weakens or breaks** an assumption.
- A newer decision **supersedes** or **amends** an older one.

So one new fact can reach decisions, projects and people that never mention it. The graph
finds them. A flat list of notes cannot.

## How it uses Relate

- **Mode: directory.** The store is `vault/`, a folder of markdown notes read by Relate's
  markdown codec.
- **Why this mode:**
  - The store is the notes. People read and edit them in Obsidian or any editor. Git diffs
    show what changed and who changed it. A decision log people can't read is a decision log
    nobody keeps.
  - Cypher writes go back into the files. `scripts/signal.py` adds a signal with `MERGE` and
    a new note appears in `vault/Signal/`.
  - A directory store lets one process write while the MCP server follows along
    (`--read-only=live`). A single `.rl` file refuses live mode.
- **What the graph models:** 59 nodes and 141 relationships.

| Label | Count | Example |
|---|---|---|
| Decision | 24 | "Open the Rotterdam South hub in Q1" (status, confidence) |
| Assumption | 14 | "The Q1 budget stays at plan, EUR 2.4m" |
| Person | 10 | Head of Operations, Head of Finance, ... |
| Project | 8 | `hub-2-rotterdam-south`, `lyon-launch`, ... |
| Signal | 3 | "October driver churn was 6.9%" |

Relationships: `RESTS_ON` (with `weight: critical`, else supporting), `STEERS`, `DECIDED_BY`,
`OWNED_BY`, `STAKEHOLDER`, `SUPERSEDES`, `AMENDS`, `CONFIRMS`, `WEAKENS`, `BREAKS`.

A note looks like this. Frontmatter wikilinks become relationships:

```markdown
---
type: Signal
name: 2026-11-15-scan-coverage-88
title: Scan coverage was 88% of trips in October
source: Ops data check
BREAKS:
  - "[[Assumption/ops-data-complete]]"
---
```

## Setup and run

You need the Relate CLI (tested on v1.1.0) and Python 3 (tested on 3.14). No Python packages.

```bash
curl -sSfL https://relatedb.ai/install.sh | bash
relate --version

git clone https://github.com/charlottebepbop/<repo>.git   # [C] fill in after the repo exists
cd <repo>
```

**1. Ask the graph.** Four queries in `queries/`, each run against the vault:

```bash
cd vault
relate query --snapshot-format markdown --database . --mode table \
  --param assumption=q1-budget-holds < ../queries/1-ripple.cypher
```

| Query | Question | Parameter |
|---|---|---|
| `1-ripple.cypher` | This assumption broke. Which live decisions rest on it, which projects do they steer, who must hear? | `assumption` |
| `2-fragile.cypher` | Which projects stand on 2 or more low-confidence decisions, and is any of the ground already hit? | none |
| `3-precheck.cypher` | Before working on a project: what binds it, what replaced old decisions, what is under pressure? | `project` |
| `4-tell.cypher` | The ripple, turned around per person, most exposed first | `assumption` |

**2. Record a new signal.** From the repo root:

```bash
python3 scripts/signal.py q1-budget-holds BREAKS "Finance cuts the Q1 budget by 20%" --source "Board memo"
```

This writes `vault/Signal/<date>-finance-cuts-the-q1-budget-by-20.md` and a brief in
`briefs/`: 5 live decisions at risk (3 critical) and 7 people to tell, most exposed first.

**3. Let an agent use it.** `.mcp.json` starts Relate's MCP server on the vault, read-only and
live. It offers two tools: `read_cypher` and `get_schema`. `CLAUDE.md` tells the agent to run
the pre-check before it plans work on a project. With Claude Code:

```bash
claude
> I want to speed up the Rotterdam South hub. Anything I should know first?
```

The agent finds the 3 decisions that steer the hub. It then follows shared assumptions to
decisions that never name the hub: driver hiring, the hiring freeze, and a bike lease whose
supplier has flagged a slip. Run step 2, ask again, and the budget break shows up.

**Reset** to the seed data at any time:

```bash
python3 scripts/seed_vault.py
```

## Where the data lives

`vault/` is the persistent store. One markdown file per node, one folder per label.
`vault/.cypherlite/` holds Relate's derived state and is not committed. Relate rebuilds it from
the notes on first open. `scripts/seed_vault.py` generates the notes, so the data can be
rebuilt from code.

## Notes on Relate

Found while building, all on v1.1.0:

- The map form for relationship properties needs at least one bare wikilink of that type
  somewhere in the vault. So supporting `RESTS_ON` links are bare, and only critical ones carry
  `weight`.
- The Python client has no markdown snapshot option, so `signal.py` writes through the CLI.
- `--param` parses its value as JSON first. `signal.py` JSON-quotes every value so a date stays
  a string.
- `relate serve` does not take `--markdown-body-properties`.
