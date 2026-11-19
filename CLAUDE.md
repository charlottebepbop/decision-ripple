# Kestrel Cargo decision graph

`vault/` is a Relate graph in markdown. Folder = label, frontmatter = properties and edges.
The `kestrel-decisions` MCP server reads it, read-only, and sees new writes live.

Labels: Decision, Assumption, Project, Person, Signal.
Edges: RESTS_ON (weight: critical, else supporting), STEERS, DECIDED_BY, SUPERSEDES, AMENDS,
OWNED_BY, STAKEHOLDER, and CONFIRMS / WEAKENS / BREAKS from a Signal to an Assumption.

Rules for agents:
- Read the graph only through the `kestrel-decisions` MCP tools (`read_cypher`, `get_schema`).
  Do not read, grep or count files in `vault/`. Reading files is blocked in `.claude/settings.json`.
- For a named question, run the matching file in `queries/` through `read_cypher`:
  fragile ground = `2-fragile`, before work on a project = `3-precheck`, who to tell = `4-tell`.
- Before you plan or change work on a project, run the precheck for it. Name any superseded decision and any assumption under pressure.
- Never act on a superseded decision. Follow SUPERSEDES to the live one.
- To record new information, run `scripts/signal.py`. Do not write vault files by hand.
- Answer with decision titles and person names from the graph, not guesses.
