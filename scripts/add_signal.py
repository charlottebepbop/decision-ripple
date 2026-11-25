"""Record a new signal in the vault and write a "who to tell" brief.

    python scripts/add_signal.py q1-budget-holds BREAKS "Finance cuts the Q1 budget by 20%" \
        --source "Board memo" --date 2026-12-01

    python scripts/add_signal.py q1-budget-holds BREAKS \
        "Finance cuts the Q1 budget and the bike supplier slips" \
        --and ebike-supplier-delivers-feb WEAKENS \
        --source "Board memo" --date 2026-12-04

The signal becomes one note under Signal/ in DECISION_VAULT, or in vault/ when that
variable is unset. Repeat --and for each extra assumption. The brief lands in
DECISION_BRIEFS, or in briefs/. Pass the assumption slug from list_slugs.py, not the title.
--dry-run checks those slugs and writes neither the note nor the brief.
"""

import argparse
import datetime as dt
import difflib
import os
import sys
from pathlib import Path

from graph import ROOT, VAULT, cypher, names, query, require, slug

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


def good_news_lines(effect, ripple, heading=True):
    """Name the decisions a support or confirmation touches, without calling them risk."""
    if effect == "CONFIRMS":
        kind, verb = "Confirmation", "confirms"
    else:
        kind, verb = "Support", "supports"
    intro = f"This signal {verb} the assumption. It is not a break or a weakening."
    if not ripple:
        return [
            f"{kind}, not a risk. {intro} No live decision rests on it.",
            "No live decision needs a second look.",
        ]
    noun = "decision" if len(ripple) == 1 else "decisions"
    lines = []
    if heading:
        lines += [f"## {kind}, not a risk", ""]
    else:
        lines.append(f"{kind}, not a risk.")
    lines += [
        f"{intro} {len(ripple)} live {noun} rest on it.",
        "No live decision needs a second look.",
        "",
        "| Decision | Weight | Confidence | Projects |",
        "|---|---|---|---|",
    ]
    for r in ripple:
        lines.append(
            f"| {r['decision']} | {r['weight']} | {r['confidence']} | {', '.join(r['projects'])} |"
        )
    return lines


def merge_tell(groups):
    """Merge one tell list per assumption into one row per person.

    `groups` is `(tell rows, ripple rows)` for each assumption that needs a look.
    The critical count is distinct decision titles. A live decision that is
    critical under two assumptions counts once; summing each assumption's count
    would count it twice. Each title is still named once, in the order the tell
    lists returned it. The per-assumption sections keep listing it under each one.
    """
    people = {}
    for rows, ripple in groups:
        critical = {row["decision"] for row in ripple if row["weight"] == "critical"}
        for person in rows:
            slot = people.setdefault(
                person["person"],
                {"role": person["role"], "critical_decisions": set(), "decisions": []},
            )
            for decision in person["decisions"]:
                if decision not in slot["decisions"]:
                    slot["decisions"].append(decision)
                if decision in critical:
                    slot["critical_decisions"].add(decision)
    ordered = sorted(people.items(), key=lambda item: (-len(item[1]["critical_decisions"]), item[0]))
    return [
        {
            "person": name,
            "role": slot["role"],
            "critical": len(slot["critical_decisions"]),
            "decisions": slot["decisions"],
        }
        for name, slot in ordered
    ]


def assumption_statement(name):
    require("Assumption", name)
    statement = cypher("MATCH (a:Assumption {name: $a}) RETURN a.statement AS s", a=name)[0]["s"]
    if isinstance(statement, str) and statement.strip():
        return statement
    # Relate creates an empty note when a wikilink names a file that does not exist yet.
    # require() then sees that phantom and a signal would print "> None".
    others = [item for item in names("Assumption") if item != name]
    close = difflib.get_close_matches(name, others, n=1, cutoff=0.8)
    hint = f" Did you mean {close[0]}?" if close else ""
    sys.exit(
        f"{name} is an empty note, not a real assumption. "
        f"Relate creates one when a link is mistyped, and a signal against it would have nothing to say.{hint} "
        "Use the real assumption name, and delete the empty note."
    )


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
    ap.add_argument("--dry-run", action="store_true", help="Check the assumptions and write nothing")
    args = ap.parse_args()

    hits = [(args.assumption, args.effect)]
    for assumption, effect in args.also or []:
        if effect not in EFFECTS:
            ap.error(f"--and {assumption} {effect}: effect must be one of {', '.join(EFFECTS)}")
        hits.append((assumption, effect))
    seen = set()
    statements = {}
    for assumption, _effect in hits:
        if assumption in seen:
            ap.error(f"{assumption} is listed twice")
        seen.add(assumption)
        statements[assumption] = assumption_statement(assumption)

    name = f"{args.date}-{slug(args.title)}"
    if args.dry_run:
        print(f"Vault: {VAULT}")
        print("Dry run. Nothing written.")
        print()
        print(f"Signal file: Signal/{name}.md")
        print(f"Title: {args.title}")
        print(f"Date: {args.date}")
        print(f"Source: {args.source}")
        for assumption, effect in hits:
            print(f"{effect} {assumption}: {statements[assumption]}")
        return

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
        statement = statements[assumption]
        ripple = query("1-ripple", assumption=assumption)
        look = needs_look(effect, ripple)
        tell = query("4-tell", assumption=assumption) if look else []
        sections.append((effect, statement, ripple, look))
        if look:
            tell_groups.append((tell, ripple))

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
            lines += ["", *tell_lines(tell_groups[0][0])]
        elif effect in ("SUPPORTS", "CONFIRMS"):
            lines += good_news_lines(effect, ripple, heading=True)
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
            elif effect in ("SUPPORTS", "CONFIRMS"):
                lines += good_news_lines(effect, ripple, heading=False)
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
