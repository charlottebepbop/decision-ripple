"""Record a new signal in the vault and write a "who to tell" brief.

    python scripts/signal.py q1-budget-holds BREAKS "Finance cuts the Q1 budget by 20%" \
        --source "Board memo" --date 2026-12-01

The signal becomes a note in vault/Signal/. The brief lands in briefs/.
"""

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "vault"
QUERIES = ROOT / "queries"
BRIEFS = ROOT / "briefs"
EFFECTS = ("BREAKS", "WEAKENS", "CONFIRMS")


def cypher(statement, **params):
    # The Python client has no markdown snapshot option yet, so writes go through the CLI.
    cmd = ["relate", "query", "--snapshot-format", "markdown",
           "--database", str(VAULT), "--json", "--max-rows", "0"]
    for key, value in params.items():
        # --param parses JSON first, so "2026-12-01" would fail as a number. Quote it.
        cmd += ["--param", f"{key}={json.dumps(value)}"]
    out = subprocess.run(cmd, input=statement, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"relate failed ({out.returncode}): {out.stdout or out.stderr}")
    return json.loads(out.stdout)["data"]


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("assumption", help="name of the Assumption note the signal hits")
    ap.add_argument("effect", choices=EFFECTS)
    ap.add_argument("title", help="one line: what happened")
    ap.add_argument("--source", default="unknown")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()

    found = cypher("MATCH (a:Assumption {name: $a}) RETURN a.statement AS statement", a=args.assumption)
    if not found:
        known = cypher("MATCH (a:Assumption) RETURN a.name AS name ORDER BY name")
        sys.exit(f"No assumption '{args.assumption}'. Known: {', '.join(r['name'] for r in known)}")
    statement = found[0]["statement"]

    name = f"{args.date}-{slug(args.title)}"
    # The relationship type cannot be a parameter, so it is checked against EFFECTS above.
    cypher(
        "MATCH (a:Assumption {name: $a}) "
        "MERGE (s:Signal {name: $name}) "
        "SET s.title = $title, s.source = $source, s.date = $date "
        f"MERGE (s)-[:{args.effect}]->(a)",
        a=args.assumption, name=name, title=args.title, source=args.source, date=args.date,
    )

    ripple = cypher((QUERIES / "1-ripple.cypher").read_text(), assumption=args.assumption)
    tell = cypher((QUERIES / "4-tell.cypher").read_text(), assumption=args.assumption)

    lines = [
        f"# {args.title}",
        "",
        f"Signal `{name}` ({args.source}, {args.date}) **{args.effect}** the assumption:",
        f"> {statement}",
        "",
    ]
    if args.effect == "CONFIRMS" or not ripple:
        lines.append("No live decision needs a second look.")
    else:
        crit = sum(1 for r in ripple if r["weight"] == "critical")
        lines += [
            f"## {len(ripple)} live decisions rest on it, {crit} of them critically",
            "",
            "| Decision | Weight | Confidence | Projects |",
            "|---|---|---|---|",
        ]
        for r in ripple:
            lines.append(f"| {r['decision']} | {r['weight']} | {r['confidence']} | {', '.join(r['projects'])} |")
        lines += ["", f"## Tell {len(tell)} people, most exposed first", ""]
        for t in tell:
            lines.append(f"- **{t['person']}** ({t['role']}): {'; '.join(t['decisions'])}")
    lines.append("")

    BRIEFS.mkdir(exist_ok=True)
    path = BRIEFS / f"{name}.md"
    path.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"Signal note: vault/Signal/{name}.md\nBrief: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
