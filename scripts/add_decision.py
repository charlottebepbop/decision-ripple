"""Record a new decision, optionally replacing or amending an older one.

    python scripts/add_decision.py "Open the Rotterdam South hub in Q2" \
        --project hub-2-rotterdam-south --by olu-adeyemi --by tomasz-wilk \
        --rests-on south-hub-lease-signed:critical --rests-on series-a-close-march \
        --supersedes 2026-07-29-open-south-hub-q1 \
        --rationale "The Q1 budget was cut by 20%." --confidence medium

The decision becomes a note in vault/Decision/. A superseded decision gets status superseded.
"""

import argparse
import datetime as dt

from graph import cypher, query, require, slug


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
    ap.add_argument("--confidence", choices=("low", "medium", "high"), default="medium")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()

    for p in args.project:
        require("Project", p)
    for person in args.by:
        require("Person", person)
    rests = []
    for item in args.rests_on:
        a, _, weight = item.partition(":")
        if weight not in ("", "critical"):
            ap.error(f"--rests-on {item}: the only weight is critical")
        require("Assumption", a)
        rests.append({"a": a, "critical": weight == "critical"})
    previous = args.supersedes or args.amends
    if previous:
        require("Decision", previous)
        status = cypher("MATCH (d:Decision {name: $n}) RETURN d.status AS s", n=previous)[0]["s"]
        if status != "live":
            ap.error(f"{previous} is {status}. Replace or amend the live decision instead.")

    name = f"{args.date}-{slug(args.title)}"
    cypher(
        "MERGE (d:Decision {name: $name}) "
        "SET d.title = $title, d.date = $date, d.confidence = $confidence, d.status = 'live', "
        "    d.text = '# ' + $title + '\n\n**Rationale:** ' + $rationale "
        "WITH d "
        "UNWIND $projects AS p MATCH (pr:Project {name: p}) MERGE (d)-[:STEERS]->(pr) "
        "WITH DISTINCT d "
        "UNWIND $people AS who MATCH (pe:Person {name: who}) MERGE (d)-[:DECIDED_BY]->(pe)",
        name=name, title=args.title, date=args.date, confidence=args.confidence,
        rationale=args.rationale, projects=args.project, people=args.by,
    )
    # Relate writes a weighted edge in the map form, which needs one bare RESTS_ON in the vault.
    # The seed data has many, so critical and supporting links can be written separately.
    for r in rests:
        props = " {weight: 'critical'}" if r["critical"] else ""
        cypher(f"MATCH (d:Decision {{name: $d}}), (a:Assumption {{name: $a}}) MERGE (d)-[:RESTS_ON{props}]->(a)",
               d=name, a=r["a"])
    if args.supersedes:
        cypher("MATCH (d:Decision {name: $d}), (o:Decision {name: $o}) "
               "MERGE (d)-[:SUPERSEDES]->(o) SET o.status = 'superseded'", d=name, o=args.supersedes)
    if args.amends:
        cypher("MATCH (d:Decision {name: $d}), (o:Decision {name: $o}) MERGE (d)-[:AMENDS]->(o)",
               d=name, o=args.amends)

    print(f"Decision note: vault/Decision/{name}.md")
    for p in args.project:
        print(f"\nPrecheck for {p}:")
        for row in query("3-precheck", project=p):
            extra = f" (replaced by: {row['replaced_by']})" if row["replaced_by"] else ""
            pressure = f" | pressure: {'; '.join(row['pressure'])}" if row["pressure"] else ""
            print(f"- [{row['status']}] {row['decision']}{extra}{pressure}")


if __name__ == "__main__":
    main()
