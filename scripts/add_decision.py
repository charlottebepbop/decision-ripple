"""Record a new decision, optionally replacing or amending an older one.

    python scripts/add_decision.py "Open the Rotterdam South hub in Q2" \
        --project hub-2-rotterdam-south --by olu-adeyemi --by tomasz-wilk \
        --rests-on south-hub-lease-signed:critical --rests-on series-a-close-march \
        --supersedes 2026-07-29-open-south-hub-q1 \
        --rationale "The Q1 budget was cut by 20%." \
        --context "The north hub still runs at 92% capacity." \
        --option "Open in Q2." \
        --option "Cancel the hub. Lost because the north hub stays full." \
        --who-decided "Olu Adeyemi and Tomasz Wilk decided." \
        --confidence medium

The decision becomes a note under Decision/ in DECISION_VAULT, or in vault/ when that
variable is unset. The note keeps the rationale, and Context, Options considered, and
Who decided when those are passed. A superseded decision gets status superseded.

Pass slugs from list_slugs.py. --new-assumption and --new-person create a note that
is not in the vault yet; a slug that is merely missing is refused, so a typo does not
become an empty note. The new assumption has to be in --rests-on, and the new person
in --by. --dry-run prints the note and writes nothing. The filename slug is cut at 60
characters.
"""

import argparse
import datetime as dt
import re
from pathlib import Path

from graph import ROOT, VAULT, cypher, missing, names, query, slug


SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
# A trailing newline makes Relate store `text` in the header instead of the note body.
# decision_body() therefore does not end with a newline. Do not add one before the write.


def show(path):
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def decision_body(title, rationale, context="", options=(), who_decided=""):
    """Markdown body. No trailing newline: Relate would otherwise hide it in the header."""
    parts = [f"# {title.strip()}", "", f"**Rationale:** {rationale.strip()}"]
    context = (context or "").strip()
    if context:
        parts += ["", "## Context", context]
    block = option_block(options)
    if block:
        parts += ["", "## Options considered", block]
    who = (who_decided or "").strip()
    if who:
        parts += ["", "## Who decided", who]
    return "\n".join(parts).rstrip("\n")


def option_block(options):
    lines = []
    for item in options or ():
        text = item.strip()
        if text.startswith("- "):
            text = text[2:].strip()
        if not text or text == "-":
            continue
        lines.append(f"- {text}")
    return "\n".join(lines)


def one_line(text):
    return " ".join(text.split())


def check_slug(ap, flag, value):
    if not SLUG_RE.fullmatch(value):
        ap.error(f"{flag} {value}: use lowercase words separated by hyphens")


def person_text(display, role):
    sentence = role if role.endswith((".", "!", "?")) else role + "."
    # No trailing newline. See decision_body.
    return f"# {display}\n\n{sentence}"


def assumption_text(statement):
    return f"# {statement}"


def heading_key(text):
    for line in (text or "").splitlines():
        if line.startswith("# "):
            return " ".join(line[2:].casefold().split())
    return ""


def note_body(path):
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    return text[end + 4:]


def person_headings():
    """Map a heading to the person slug. check_vault treats two equal headings as one person."""
    folder = VAULT / "Person"
    taken = {}
    if not folder.is_dir():
        return taken
    for path in sorted(folder.glob("*.md")):
        if path.name in {"index.md", "log.md"}:
            continue
        key = heading_key(note_body(path))
        if key:
            taken.setdefault(key, path.stem)
    return taken


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("title")
    ap.add_argument("--project", action="append", required=True, help="Project it steers (repeat)")
    ap.add_argument("--by", action="append", required=True, help="Person who decided (repeat)")
    ap.add_argument("--rests-on", action="append", default=[],
                    help="Assumption it needs; add :critical if it fails without it (repeat)")
    old = ap.add_mutually_exclusive_group()
    old.add_argument("--supersedes", help="Decision this one replaces")
    old.add_argument("--amends", help="Decision this one changes but keeps live")
    ap.add_argument("--rationale", required=True)
    ap.add_argument("--context", default="", help="Situation, stored under Context")
    ap.add_argument("--option", action="append", default=[],
                    help="One option considered (repeat). Stored as a bullet")
    ap.add_argument("--who-decided", default="", help="Who decided, in a sentence or two")
    ap.add_argument("--new-assumption", action="append", nargs=2, default=None,
                    metavar=("SLUG", "STATEMENT"),
                    help="Create this assumption. Also pass it to --rests-on (repeat)")
    ap.add_argument("--new-person", action="append", nargs=3, default=None,
                    metavar=("SLUG", "NAME", "ROLE"),
                    help="Create this person. Also pass the slug to --by (repeat)")
    ap.add_argument("--confidence", choices=("low", "medium", "high"), default="medium")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true", help="Print the note and write nothing")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        ap.error(f"--date {args.date}: use YYYY-MM-DD")
    try:
        dt.date.fromisoformat(args.date)
    except ValueError:
        ap.error(f"--date {args.date}: use YYYY-MM-DD")

    title = one_line(args.title)
    if not title:
        ap.error("the title is empty")
    rationale = args.rationale.strip()
    if not rationale:
        ap.error("--rationale is empty")

    new_assumptions = []
    seen_assumptions = set()
    for raw_slug, raw_statement in args.new_assumption or []:
        check_slug(ap, "--new-assumption", raw_slug)
        statement = one_line(raw_statement)
        if not statement:
            ap.error(f"--new-assumption {raw_slug}: the statement is empty")
        if raw_slug in seen_assumptions:
            ap.error(f"{raw_slug} is listed twice")
        seen_assumptions.add(raw_slug)
        new_assumptions.append((raw_slug, statement))

    new_people = []
    seen_people = set()
    seen_headings = {}
    for raw_slug, raw_name, raw_role in args.new_person or []:
        check_slug(ap, "--new-person", raw_slug)
        display = one_line(raw_name)
        role = one_line(raw_role)
        if not display:
            ap.error(f"--new-person {raw_slug}: the name is empty")
        if not role:
            ap.error(f"--new-person {raw_slug}: the role is empty")
        if raw_slug in seen_people:
            ap.error(f"{raw_slug} is listed twice")
        key = display.casefold()
        if key in seen_headings:
            ap.error(f"{display} is already the new person {seen_headings[key]}")
        seen_people.add(raw_slug)
        seen_headings[key] = raw_slug
        new_people.append((raw_slug, display, role))

    rests = []
    seen_rests = set()
    for item in args.rests_on:
        assumption, _, weight = item.partition(":")
        if weight not in ("", "critical"):
            ap.error(f"--rests-on {item}: the only weight is critical")
        check_slug(ap, "--rests-on", assumption)
        if assumption in seen_rests:
            ap.error(f"{assumption} is listed twice")
        seen_rests.add(assumption)
        rests.append({"a": assumption, "critical": weight == "critical"})
    for assumption, _statement in new_assumptions:
        if assumption not in seen_rests:
            ap.error(
                f"{assumption} is a new assumption, and this decision does not rest on it. "
                f"Pass --rests-on {assumption} or --rests-on {assumption}:critical."
            )
    for person, _display, _role in new_people:
        if person not in args.by:
            ap.error(f"{person} is a new person, and they are not in --by. Pass --by {person}.")

    known_assumptions = names("Assumption")
    known_people = names("Person")
    known_projects = names("Project")
    known_decisions = names("Decision")

    for assumption, _statement in new_assumptions:
        if assumption in known_assumptions:
            ap.error(
                f"Assumption '{assumption}' already exists. "
                "Link it with --rests-on instead of --new-assumption."
            )
    for person, _display, _role in new_people:
        if person in known_people:
            ap.error(f"Person '{person}' already exists. Pass --by {person} and drop --new-person.")

    for project in args.project:
        message = missing("Project", project, known_projects)
        if message:
            raise SystemExit(message)
    for person in args.by:
        if person in seen_people or person in known_people:
            continue
        message = missing("Person", person, known_people)
        if message:
            raise SystemExit(message)
    for item in rests:
        if item["a"] in seen_assumptions or item["a"] in known_assumptions:
            continue
        message = missing("Assumption", item["a"], known_assumptions)
        if message:
            raise SystemExit(message)

    if new_people:
        taken = person_headings()
        for _person, display, _role in new_people:
            key = display.casefold()
            if key in taken:
                raise SystemExit(
                    f"A person note is already headed '{display}' ({taken[key]}). "
                    f"Use --by {taken[key]}."
                )

    previous = args.supersedes or args.amends
    if previous:
        message = missing("Decision", previous, known_decisions)
        if message:
            raise SystemExit(message)
        status = cypher("MATCH (d:Decision {name: $n}) RETURN d.status AS s", n=previous)[0]["s"]
        if status != "live":
            ap.error(f"{previous} is {status}. Replace or amend the live decision instead.")

    name = f"{args.date}-{slug(title)}"
    if name in known_decisions:
        raise SystemExit(f"Decision '{name}' already exists.")

    body = decision_body(title, rationale, args.context, args.option, args.who_decided)
    if args.dry_run:
        print(render_plan(name, title, args, rests, new_assumptions, new_people, body))
        return

    for person, display, role in new_people:
        cypher(
            "MERGE (p:Person {name: $name}) SET p.role = $role, p.text = $text",
            name=person, role=role, text=person_text(display, role),
        )
    for assumption, statement in new_assumptions:
        cypher(
            "MERGE (a:Assumption {name: $name}) SET a.statement = $statement, a.text = $text",
            name=assumption, statement=statement, text=assumption_text(statement),
        )
    cypher(
        "MERGE (d:Decision {name: $name}) "
        "SET d.title = $title, d.date = $date, d.confidence = $confidence, d.status = 'live', "
        "    d.text = $text "
        "WITH d "
        "UNWIND $projects AS p MATCH (pr:Project {name: p}) MERGE (d)-[:STEERS]->(pr) "
        "WITH DISTINCT d "
        "UNWIND $people AS who MATCH (pe:Person {name: who}) MERGE (d)-[:DECIDED_BY]->(pe)",
        name=name, title=title, date=args.date, confidence=args.confidence,
        text=body, projects=args.project, people=args.by,
    )
    # Relate writes a weighted edge in the map form, which needs one bare RESTS_ON in the vault.
    # The seed data has many, so critical and supporting links can be written separately.
    for item in rests:
        props = " {weight: 'critical'}" if item["critical"] else ""
        cypher(
            f"MATCH (d:Decision {{name: $d}}), (a:Assumption {{name: $a}}) "
            f"MERGE (d)-[:RESTS_ON{props}]->(a)",
            d=name, a=item["a"],
        )
    if args.supersedes:
        cypher(
            "MATCH (d:Decision {name: $d}), (o:Decision {name: $o}) "
            "MERGE (d)-[:SUPERSEDES]->(o) SET o.status = 'superseded'",
            d=name, o=args.supersedes,
        )
    if args.amends:
        cypher(
            "MATCH (d:Decision {name: $d}), (o:Decision {name: $o}) MERGE (d)-[:AMENDS]->(o)",
            d=name, o=args.amends,
        )

    print(f"Decision note: {show(VAULT / 'Decision' / f'{name}.md')}")
    for project in args.project:
        print(f"\nPrecheck for {project}:")
        for row in query("3-precheck", project=project):
            replaced = [item for item in (row["replaced_by"] or []) if item]
            amended = sorted(item for item in (row["amended_by"] or []) if item)
            grounds = sorted(item for item in (row["amendment_rests_on"] or []) if item)
            extra = f" (replaced by: {'; '.join(replaced)})" if replaced else ""
            if amended:
                extra += f" (amended by: {'; '.join(amended)})"
            if grounds:
                extra += f" (amendment rests on: {'; '.join(grounds)})"
            pressure = f" | pressure: {'; '.join(row['pressure'])}" if row["pressure"] else ""
            print(f"- [{row['status']}] {row['decision']}{extra}{pressure}")


def render_plan(name, title, args, rests, new_assumptions, new_people, body):
    new_assumption_slugs = {item for item, _statement in new_assumptions}
    new_person_slugs = {item for item, _display, _role in new_people}
    decided = []
    for person in args.by:
        decided.append(f"{person} (new)" if person in new_person_slugs else person)
    lines = [
        f"Vault: {VAULT}",
        "Dry run. Nothing written.",
        "",
        f"Decision file: Decision/{name}.md",
        f"Title: {title}",
        f"Date: {args.date}",
        f"Confidence: {args.confidence}",
        "Status: live",
        "Steers: " + ", ".join(args.project),
        "Decided by: " + ", ".join(decided),
        "Rests on:",
    ]
    for item in rests:
        weight = "critical" if item["critical"] else "supporting"
        mark = ", new" if item["a"] in new_assumption_slugs else ""
        lines.append(f"  {item['a']} ({weight}{mark})")
    if args.supersedes:
        lines.append(f"Supersedes: {args.supersedes}")
    if args.amends:
        lines.append(f"Amends: {args.amends}")
    if new_people or new_assumptions:
        lines.append("New notes:")
        for person, display, role in new_people:
            lines.append(f"  Person/{person}: {display}, {role}")
        for assumption, statement in new_assumptions:
            lines.append(f"  Assumption/{assumption}: {statement}")
    else:
        lines.append("New notes: none")
    lines += ["", body]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
