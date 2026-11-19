"""Record a new signal in the vault and write a "who to tell" brief.

    python scripts/add_signal.py q1-budget-holds BREAKS "Finance cuts the Q1 budget by 20%" \
        --source "Board memo" --date 2026-12-01

The signal becomes a note in vault/Signal/. The brief lands in briefs/.
"""

import argparse
import datetime as dt

from graph import ROOT, cypher, query, require, slug

BRIEFS = ROOT / "briefs"
# SUPPORTS is a weaker CONFIRMS: evidence for the assumption, not proof.
EFFECTS = ("BREAKS", "WEAKENS", "SUPPORTS", "CONFIRMS")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("assumption", help="name of the Assumption note the signal hits")
    ap.add_argument("effect", choices=EFFECTS)
    ap.add_argument("title", help="one line: what happened")
    ap.add_argument("--source", required=True, help="where it came from: a report, memo or notice")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()

    require("Assumption", args.assumption)
    statement = cypher("MATCH (a:Assumption {name: $a}) RETURN a.statement AS s", a=args.assumption)[0]["s"]

    name = f"{args.date}-{slug(args.title)}"
    # The relationship type cannot be a parameter, so it is checked against EFFECTS above.
    cypher(
        "MATCH (a:Assumption {name: $a}) "
        "MERGE (s:Signal {name: $name}) "
        "SET s.title = $title, s.source = $source, s.date = $date "
        f"MERGE (s)-[:{args.effect}]->(a)",
        a=args.assumption, name=name, title=args.title, source=args.source, date=args.date,
    )

    ripple = query("1-ripple", assumption=args.assumption)
    tell = query("4-tell", assumption=args.assumption)

    lines = [
        f"# {args.title}",
        "",
        f"Signal `{name}` ({args.source}, {args.date}) **{args.effect}** the assumption:",
        f"> {statement}",
        "",
    ]
    if args.effect in ("SUPPORTS", "CONFIRMS") or not ripple:
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
            lines.append(f"- **{t['person']}** ({t['role']}, {t['critical']} critical): {'; '.join(t['decisions'])}")
    lines.append("")

    BRIEFS.mkdir(exist_ok=True)
    path = BRIEFS / f"{name}.md"
    path.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"Signal note: vault/Signal/{name}.md\nBrief: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
