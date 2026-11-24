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
- If the user asks for work that follows a superseded decision, stop. Name the live decision and
  who made it, then ask who changed it and when. Do not draft the plan until a new decision is recorded.
- A broken or weakened assumption does not change a decision. Say the decision is still live,
  what broke, and who decided it. The people who made it make the next call.
- To record new information, run `scripts/add_signal.py`. Always pass the real `--source`.
- To record a new decision, or one that replaces or amends another, run `scripts/add_decision.py`.
  Only record a decision the user says was made, with who made it.
- When a new decision supersedes an old one, pass `--rests-on` for each assumption of the old
  decision that no signal has broken, with the same weight. Say which you carried over and which you left out.
  A decision with no assumptions cannot be flagged by a later signal.
- Do not write vault files by hand.
- Answer with decision titles and person names from the graph, not guesses.
  Name people by their `title` (Olu Adeyemi), never the slug (olu-adeyemi). `--by` takes either.
- Start with the answer in one or two sentences. Then at most 5 short bullets. No tables.
  Give more only when the user asks for it.
