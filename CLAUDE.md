# Kestrel Cargo decision graph

`vault/` is a Relate graph in markdown. Folder = label, frontmatter = properties and edges.
The `kestrel-decisions` MCP server reads it, read-only, and sees new writes live.

Labels: Decision, Assumption, Project, Person, Signal.
Edges: RESTS_ON (weight: critical, else supporting), STEERS, DECIDED_BY, SUPERSEDES, AMENDS,
OWNED_BY, STAKEHOLDER, and CONFIRMS / SUPPORTS / WEAKENS / BREAKS from a Signal to an Assumption.

Rules for agents:
- Read the graph only through the `kestrel-decisions` MCP tools (`read_cypher`, `get_schema`).
  Do not read, grep or count files in `vault/`. Reading files is blocked in `.claude/settings.json`.
- For a named question, run the matching file in `queries/` through `read_cypher`:
  fragile ground = `2-fragile`, before work on a project = `3-precheck`, who to tell = `4-tell`,
  why a decision was made = `5-why` (full-text search, pass a few words as `term`).
- Before you plan or change work on a project, run the precheck for it. Name any superseded decision and any assumption under pressure.
- Never act on a superseded decision. Follow SUPERSEDES to the live one.
- To record new information, run `scripts/add_signal.py`. Always pass the real `--source`.
- To record a new decision, or one that replaces or amends another, run `scripts/add_decision.py`.
  Only record a decision the user says was made, with who made it.
- Do not write vault files by hand.
- Answer with decision titles and person names from the graph, not guesses.
