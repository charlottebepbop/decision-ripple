# Kestrel Cargo decision graph

`vault/` is a Relate graph in markdown. Folder = label, frontmatter = properties and edges.
The `kestrel-decisions` MCP server reads it, read-only, and sees new writes live.

Labels: Decision, Assumption, Project, Person, Signal.
Edges: RESTS_ON (weight: critical, else supporting), STEERS, DECIDED_BY, SUPERSEDES, AMENDS,
OWNED_BY, STAKEHOLDER, and CONFIRMS / WEAKENS / BREAKS from a Signal to an Assumption.

Rules for agents:
- Before you plan or change work on a project, run `queries/3-precheck.cypher` for it
  through `read_cypher`. Name any superseded decision and any assumption under pressure.
- Never act on a superseded decision. Follow SUPERSEDES to the live one.
- To record new information, run `scripts/signal.py`. Do not write vault files by hand.
- Answer with decision titles and person names from the graph, not guesses.
