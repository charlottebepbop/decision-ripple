"""Record a new signal in the vault and write a "who to tell" brief.

    python scripts/add_signal.py q1-budget-holds BREAKS "Finance cuts the Q1 budget by 20%" \
        --source "Board memo" --date 2026-12-01

    python scripts/add_signal.py q1-budget-holds BREAKS \
        "Finance cuts the Q1 budget and the bike supplier slips" \
        --and ebike-supplier-delivers-feb WEAKENS \
        --source "Board memo" --date 2026-12-04

The signal becomes one note in vault/Signal/. Repeat --and for each extra assumption.
The brief lands in briefs/.
"""

import argparse
import datetime as dt
import os
from pathlib import Path

from graph import ROOT, VAULT, cypher, query, require, slug

BRIEFS = Path(os.environ["DECISION_BRIEFS"]) if os.environ.get("DECISION_BRIEFS") else ROOT / "briefs"
# SUPPORTS is a weaker CONFIRMS: evidence for the assumption, not proof.
EFFECTS = ("BREAKS", "WEAKENS", "SUPPORTS", "CONFIRMS")


def decision_heading(ripple):
    n = len(ripple)
    crit = sum(1 for r in ripple if r["weight"] == "critical")
    if n == 1 and crit == 1:
        return "## 1 live decision rests on it, critically"
    if n == 1:
        return "## 1 live decision rests on it"
    return f"## {n} live decisions rest on it, {crit} of them critically"


def decision_table(ripple):
    lines = [
        decision_heading(ripple),
        "",
        "| Decision | Weight | Confidence | Projects |",
        "|---|---|---|---|",
    ]
    for r in ripple:
        lines.append(f"| {r['decision']} | {r['weight']} | {r['confidence']} | {', '.join(r['projects'])} |")
    return lines


def tell_lines(tell):
    lines = [f"## Tell {len(tell)} people, most exposed first", ""]
    for t in tell:
        lines.append(f"- **{t['person']}** ({t['role']}, {t['critical']} critical): {'; '.join(t['decisions'])}")
    return lines


def needs_look(effect, ripple):
    return effect not in ("SUPPORTS", "CONFIRMS") and bool(ripple)


def merge_tell(groups):
    people = {}
    for rows in groups:
        for t in rows:
            slot = people.setdefault(t["person"], {"role": t["role"], "critical": 0, "decisions": []})
            slot["critical"] += t["critical"]
            for decision in t["decisions"]:
                if decision not in slot["decisions"]:
                    slot["decisions"].append(decision)
    ordered = sorted(people.items(), key=lambda item: (-item[1]["critical"], item[0]))
    return [{"person": person, **slot} for person, slot in ordered]


def show(path):
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("assumption", help="name of the Assumption note the signal hits")
    ap.add_argument("effect", choices=EFFECTS)
    ap.add_argument("title", help="one line: what happened")
    ap.add_argument("--and", dest="also", action="append", nargs=2, metavar=("ASSUMPTION", "EFFECT"),
                    help="another assumption this signal hits, and its effect (repeat)")
    ap.add_argument("--source", required=True, help="where it came from: a report, memo or notice")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()

    hits = [(args.assumption, args.effect)]
    for assumption, effect in args.also or []:
        if effect not in EFFECTS:
            ap.error(f"--and {assumption} {effect}: effect must be one of {', '.join(EFFECTS)}")
        hits.append((assumption, effect))
    seen = set()
    for assumption, _effect in hits:
        if assumption in seen:
            ap.error(f"{assumption} is listed twice")
        seen.add(assumption)
        require("Assumption", assumption)

    name = f"{args.date}-{slug(args.title)}"
    # The relationship type cannot be a parameter, so it is checked against EFFECTS above.
    cypher(
        "MERGE (s:Signal {name: $name}) "
        "SET s.title = $title, s.source = $source, s.date = $date",
        name=name, title=args.title, source=args.source, date=args.date,
    )
    for assumption, effect in hits:
        cypher(
            "MATCH (s:Signal {name: $name}), (a:Assumption {name: $a}) "
            f"MERGE (s)-[:{effect}]->(a)",
            name=name, a=assumption,
        )

    sections = []
    tell_groups = []
    for assumption, effect in hits:
        statement = cypher("MATCH (a:Assumption {name: $a}) RETURN a.statement AS s", a=assumption)[0]["s"]
        ripple = query("1-ripple", assumption=assumption)
        look = needs_look(effect, ripple)
        tell = query("4-tell", assumption=assumption) if look else []
        sections.append((effect, statement, ripple, look))
        if look:
            tell_groups.append(tell)

    if len(hits) == 1:
        effect, statement, ripple, look = sections[0]
        lines = [
            f"# {args.title}",
            "",
            f"Signal `{name}` ({args.source}, {args.date}) **{effect}** the assumption:",
            f"> {statement}",
            "",
        ]
        if look:
            lines += decision_table(ripple)
            lines += ["", *tell_lines(tell_groups[0])]
        else:
            lines.append("No live decision needs a second look.")
    else:
        lines = [
            f"# {args.title}",
            "",
            f"Signal `{name}` ({args.source}, {args.date}) hits:",
            "",
        ]
        for effect, statement, ripple, look in sections:
            lines += [f"## {effect}", f"> {statement}", ""]
            if look:
                lines += decision_table(ripple)
            else:
                lines.append("No live decision needs a second look.")
            lines.append("")
        if tell_groups:
            lines += tell_lines(merge_tell(tell_groups))
    lines.append("")

    BRIEFS.mkdir(exist_ok=True)
    path = BRIEFS / f"{name}.md"
    path.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"Signal note: {show(VAULT / 'Signal' / f'{name}.md')}\nBrief: {show(path)}")


if __name__ == "__main__":
    main()
