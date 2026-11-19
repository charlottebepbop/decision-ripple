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
  what is already broken = `6-exposed` (no parameter), fragile ground = `2-fragile` (no parameter),
  before work on a project = `3-precheck` (parameter `project`, a slug), who to tell = `4-tell`
  (parameter `assumption`, a slug), why a decision was made = `5-why` (full-text search, pass a few words as `term`).
  `1-ripple` also takes `assumption`. Slugs are filenames, not titles. Run `scripts/list_slugs.py` to list them.
- The notes folder is `DECISION_VAULT` when that variable is set, otherwise `vault/` in this repo. Briefs go to `DECISION_BRIEFS` when set, otherwise `briefs/`. Record into the sample vault only when the user is working the Kestrel example. `scripts/serve.sh` reads the same variable.
- Before you plan or change work on a project, run `6-exposed` and the precheck for it. Name any superseded decision and any assumption under pressure. The precheck follows SUPERSEDES to the decision that is still live.
- Never act on a superseded decision. Follow SUPERSEDES to the live one.
- To record new information, run `scripts/add_signal.py`. Always pass the real `--source`. Repeat `--and ASSUMPTION EFFECT` when one memo hits more than one assumption.
- To record a new decision, or one that replaces or amends another, run `scripts/add_decision.py`.
  Only record a decision the user says was made, with who made it.
- Do not write vault files by hand.
- Answer with decision titles and person names from the graph, not guesses.
