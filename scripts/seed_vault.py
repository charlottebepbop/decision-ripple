"""Write the sample decision vault for Kestrel Cargo, a made-up company.

Run: python scripts/seed_vault.py
Writes markdown into ./vault. Relate reads it with the markdown codec:
folder = label, filename = key, frontmatter wikilink lists = relationships.
"""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent / "vault"

PEOPLE = {
    "ines-varga": "CEO",
    "tomasz-wilk": "COO",
    "priya-raman": "Head of Finance",
    "olu-adeyemi": "Head of Operations",
    "hanna-berg": "Head of Growth",
    "diego-morales": "Fleet Lead",
    "saskia-de-wit": "People Lead",
    "ken-ito": "CTO",
    "lea-novak": "BizOps Lead",
    "ruth-mensah": "Customer Success Lead",
}

# slug: (title, owner, stakeholders)
PROJECTS = {
    "lyon-launch": ("Launch in Lyon", "hanna-berg", ["ines-varga", "olu-adeyemi", "priya-raman"]),
    "fleet-ebike-upgrade": ("Replace 60 bikes with e-cargo bikes", "diego-morales", ["priya-raman", "tomasz-wilk"]),
    "route-optimizer-v2": ("Route optimizer v2", "ken-ito", ["olu-adeyemi", "diego-morales"]),
    "hub-2-rotterdam-south": ("Second hub, Rotterdam South", "olu-adeyemi", ["priya-raman", "tomasz-wilk"]),
    "enterprise-pricing": ("Enterprise pricing tier", "hanna-berg", ["priya-raman", "ruth-mensah"]),
    "driver-hiring-q1": ("Driver hiring Q1", "saskia-de-wit", ["olu-adeyemi", "priya-raman"]),
    "ops-dashboard": ("Ops dashboard", "lea-novak", ["tomasz-wilk", "olu-adeyemi"]),
    "customer-sla-program": ("Customer SLA program", "ruth-mensah", ["olu-adeyemi", "hanna-berg"]),
}

ASSUMPTIONS = {
    "q1-budget-holds": "The Q1 budget stays at plan, EUR 2.4m.",
    "lyon-permit-by-jan": "Lyon grants the cargo-bike depot permit by 15 Jan.",
    "ebike-supplier-delivers-feb": "The supplier delivers 60 e-cargo bikes by end of February.",
    "driver-churn-under-8": "Monthly driver churn stays under 8%.",
    "route-api-pricing-stable": "The mapping API price stays flat through 2027.",
    "south-hub-lease-signed": "The Rotterdam South lease is signed by December.",
    "enterprise-demand-3-pilots": "At least 3 enterprise pilots convert by end of Q1.",
    "winter-volume-dip-15": "Winter parcel volume drops by at most 15%.",
    "series-a-close-march": "The Series A closes by end of March.",
    "cs-headcount-flat": "Customer Success stays at 5 people.",
    "eu-cargo-bike-subsidy": "The Dutch e-cargo-bike subsidy renews for 2027.",
    "ops-data-complete": "Delivery scans cover at least 95% of trips.",
    "hiring-pipeline-40": "We get 40 qualified driver applicants a month.",
    "sla-penalties-capped": "SLA penalties are capped at 5% of contract value.",
}

C, S = "critical", "supporting"

# slug: dict(title, confidence, status, rests_on[(assumption, weight)], steers, by,
#            supersedes, amends, rationale)
DECISIONS = {
    "2026-06-05-driver-bonus-for-retention": dict(
        title="Pay a 3-month retention bonus to drivers", confidence="high",
        rests_on=[("driver-churn-under-8", S)], steers=["driver-hiring-q1"], by=["saskia-de-wit"],
        rationale="Replacing a driver costs more than the bonus."),
    "2026-06-12-launch-lyon-before-paris": dict(
        title="Launch Lyon before Paris", confidence="high",
        rests_on=[("lyon-permit-by-jan", C), ("series-a-close-march", S)],
        steers=["lyon-launch"], by=["ines-varga", "hanna-berg"],
        rationale="Lyon is smaller, and its permit process is faster."),
    "2026-06-20-buy-ebikes-not-lease": dict(
        title="Buy the e-cargo bikes outright", confidence="medium", status="superseded",
        rests_on=[("q1-budget-holds", C), ("eu-cargo-bike-subsidy", S)],
        steers=["fleet-ebike-upgrade"], by=["priya-raman", "diego-morales"],
        rationale="Buying is cheaper over 3 years with the subsidy."),
    "2026-06-30-paris-waits-for-lyon-data": dict(
        title="Paris waits for 3 months of Lyon data", confidence="high",
        rests_on=[("lyon-permit-by-jan", S)], steers=["lyon-launch"], by=["ines-varga"],
        rationale="We want unit economics from one French city first."),
    "2026-07-03-lyon-depot-in-guillotiere": dict(
        title="Put the Lyon depot in Guillotiere", confidence="medium",
        rests_on=[("lyon-permit-by-jan", C)], steers=["lyon-launch"], by=["olu-adeyemi"],
        rationale="Shortest average route to the customers we have signed."),
    "2026-07-08-apply-for-ebike-subsidy": dict(
        title="Apply for the Dutch e-cargo-bike subsidy", confidence="high",
        rests_on=[("eu-cargo-bike-subsidy", C)], steers=["fleet-ebike-upgrade"], by=["priya-raman"],
        rationale="Covers 30% of the purchase price."),
    "2026-07-15-cs-stays-at-five": dict(
        title="Customer Success stays at 5 people", confidence="medium",
        rests_on=[("cs-headcount-flat", C), ("enterprise-demand-3-pilots", S)],
        steers=["customer-sla-program"], by=["ruth-mensah", "tomasz-wilk"],
        rationale="Ticket volume per customer is falling."),
    "2026-07-29-open-south-hub-q1": dict(
        title="Open the Rotterdam South hub in Q1", confidence="medium",
        rests_on=[("south-hub-lease-signed", C), ("q1-budget-holds", C), ("winter-volume-dip-15", S)],
        steers=["hub-2-rotterdam-south"], by=["olu-adeyemi", "tomasz-wilk"],
        rationale="The north hub runs at 92% capacity."),
    "2026-08-01-runway-plan-assumes-march-close": dict(
        title="Runway plan assumes the Series A closes in March", confidence="high",
        rests_on=[("series-a-close-march", C)],
        steers=["hub-2-rotterdam-south", "lyon-launch"], by=["ines-varga", "priya-raman"],
        rationale="Lead investor gave a verbal term sheet."),
    "2026-08-11-build-route-optimizer-in-house": dict(
        title="Build the route optimizer in house", confidence="low",
        rests_on=[("route-api-pricing-stable", C), ("ops-data-complete", C)],
        steers=["route-optimizer-v2"], by=["ken-ito"],
        rationale="Vendor tools do not handle bike lanes and loading zones."),
    "2026-08-25-enterprise-tier-at-1800": dict(
        title="Price the enterprise tier at EUR 1,800 a month", confidence="medium",
        rests_on=[("enterprise-demand-3-pilots", C)],
        steers=["enterprise-pricing"], by=["hanna-berg", "priya-raman"],
        rationale="Three prospects named a budget between 1,500 and 2,000."),
    "2026-09-02-staff-south-hub-from-north": dict(
        title="Staff the south hub with drivers from the north hub", confidence="low",
        rests_on=[("driver-churn-under-8", C), ("hiring-pipeline-40", S)],
        steers=["hub-2-rotterdam-south", "driver-hiring-q1"], by=["olu-adeyemi", "saskia-de-wit"],
        rationale="Experienced drivers lower the error rate in a new hub."),
    "2026-09-09-mapping-api-annual-contract": dict(
        title="Sign an annual mapping API contract", confidence="medium", status="superseded",
        rests_on=[("route-api-pricing-stable", S)],
        steers=["route-optimizer-v2"], by=["ken-ito", "priya-raman"],
        rationale="20% cheaper than monthly."),
    "2026-09-18-hire-lyon-city-lead-in-dec": dict(
        title="Hire the Lyon city lead in December", confidence="medium",
        rests_on=[("q1-budget-holds", C), ("lyon-permit-by-jan", S)],
        steers=["lyon-launch", "driver-hiring-q1"], by=["hanna-berg", "saskia-de-wit"],
        rationale="The lead needs 6 weeks before the first driver starts."),
    "2026-09-30-ops-dashboard-on-scan-data": dict(
        title="Build the ops dashboard on scan data", confidence="medium",
        rests_on=[("ops-data-complete", C)], steers=["ops-dashboard"], by=["lea-novak"],
        rationale="Scans are the only per-trip record we have."),
    "2026-10-02-lease-half-buy-half": dict(
        title="Lease half the e-cargo bikes, buy half", confidence="medium",
        rests_on=[("ebike-supplier-delivers-feb", C), ("q1-budget-holds", S), ("eu-cargo-bike-subsidy", S)],
        steers=["fleet-ebike-upgrade"], by=["priya-raman", "diego-morales", "tomasz-wilk"],
        supersedes=["2026-06-20-buy-ebikes-not-lease"],
        rationale="Keeps cash for the south hub."),
    "2026-10-07-winter-shift-plan-two-waves": dict(
        title="Run winter shifts in two waves", confidence="medium",
        rests_on=[("winter-volume-dip-15", C)],
        steers=["driver-hiring-q1", "customer-sla-program"], by=["olu-adeyemi"],
        rationale="Matches the morning and afternoon parcel peaks."),
    "2026-10-14-hire-25-drivers-q1": dict(
        title="Hire 25 drivers in Q1", confidence="medium",
        rests_on=[("q1-budget-holds", C), ("hiring-pipeline-40", C), ("winter-volume-dip-15", S)],
        steers=["driver-hiring-q1"], by=["saskia-de-wit", "olu-adeyemi"],
        rationale="Covers the south hub and Lyon."),
    "2026-10-21-optimizer-uses-scan-data-only": dict(
        title="The optimizer trains on scan data only", confidence="low",
        rests_on=[("ops-data-complete", C)],
        steers=["route-optimizer-v2", "ops-dashboard"], by=["ken-ito", "lea-novak"],
        rationale="GPS traces are too noisy in the old town."),
    "2026-10-28-sla-98-percent-on-time": dict(
        title="Promise 98% on-time delivery in the SLA", confidence="low",
        rests_on=[("driver-churn-under-8", C), ("sla-penalties-capped", C), ("winter-volume-dip-15", S)],
        steers=["customer-sla-program"], by=["ruth-mensah", "olu-adeyemi"],
        rationale="Enterprise prospects asked for a number above 97%."),
    "2026-11-04-enterprise-tier-adds-sla": dict(
        title="The enterprise tier includes the SLA", confidence="low",
        rests_on=[("sla-penalties-capped", C), ("enterprise-demand-3-pilots", S)],
        steers=["enterprise-pricing", "customer-sla-program"], by=["hanna-berg", "ruth-mensah"],
        amends=["2026-08-25-enterprise-tier-at-1800"],
        rationale="Two of three pilots made the SLA a condition."),
    "2026-11-06-mapping-api-monthly-until-optimizer": dict(
        title="Pay the mapping API monthly until the optimizer ships", confidence="low",
        rests_on=[("route-api-pricing-stable", C)],
        steers=["route-optimizer-v2"], by=["ken-ito"],
        supersedes=["2026-09-09-mapping-api-annual-contract"],
        rationale="We may not need it after v2."),
    "2026-11-10-weekly-ops-review-from-dashboard": dict(
        title="Run the weekly ops review from the dashboard", confidence="low",
        rests_on=[("ops-data-complete", S)],
        steers=["ops-dashboard"], by=["tomasz-wilk", "lea-novak"],
        rationale="One set of numbers in the room."),
    "2026-11-12-freeze-hires-outside-ops": dict(
        title="Freeze hiring outside Operations until the Series A closes", confidence="medium",
        rests_on=[("series-a-close-march", C), ("q1-budget-holds", S)],
        steers=["driver-hiring-q1"], by=["ines-varga"],
        rationale="Protects runway if the round slips."),
}

# Signals already in the vault. The demo adds a new one live.
SIGNALS = {
    "2026-10-20-churn-report-october": dict(
        title="October driver churn was 6.9%", source="People report",
        confirms=["driver-churn-under-8"]),
    "2026-11-02-supplier-delay-notice": dict(
        title="Supplier flags a 3-week slip on e-cargo bikes", source="Supplier email",
        weakens=["ebike-supplier-delivers-feb"]),
    "2026-11-15-scan-coverage-88": dict(
        title="Scan coverage was 88% of trips in October", source="Ops data check",
        breaks=["ops-data-complete"]),
}


def link(folder, slug):
    return f'"[[{folder}/{slug}]]"'


def write(folder, slug, fm_lines, body):
    path = ROOT / folder / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + "\n".join(fm_lines) + "\n---\n\n" + body.strip() + "\n")


def link_list(key, folder, slugs):
    if not slugs:
        return []
    return [f"{key}:"] + [f"  - {link(folder, s)}" for s in slugs]


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)

    for slug, role in PEOPLE.items():
        name = slug.replace("-", " ").title()
        write("Person", slug, ["type: Person", f"name: {slug}", f'role: "{role}"'],
              f"# {name}\n\n{role} at Kestrel Cargo.")

    for slug, (title, owner, stakeholders) in PROJECTS.items():
        fm = ["type: Project", f"name: {slug}", f'title: "{title}"']
        fm += link_list("OWNED_BY", "Person", [owner])
        fm += link_list("STAKEHOLDER", "Person", stakeholders)
        write("Project", slug, fm, f"# {title}")

    for slug, statement in ASSUMPTIONS.items():
        write("Assumption", slug, ["type: Assumption", f"name: {slug}", f'statement: "{statement}"'],
              f"# {statement}")

    for slug, d in DECISIONS.items():
        fm = ["type: Decision", f"name: {slug}", f'title: "{d["title"]}"',
              f"date: {slug[:10]}", f"confidence: {d['confidence']}",
              f"status: {d.get('status', 'live')}"]
        fm.append("RESTS_ON:")
        # Relate needs one bare link per edge type before it accepts the map form,
        # so supporting links stay bare and only critical ones carry a weight.
        for a, weight in d["rests_on"]:
            if weight == C:
                fm += [f"  - weight: {weight}", f"    target: {link('Assumption', a)}"]
            else:
                fm.append(f"  - {link('Assumption', a)}")
        fm += link_list("STEERS", "Project", d["steers"])
        fm += link_list("DECIDED_BY", "Person", d["by"])
        fm += link_list("SUPERSEDES", "Decision", d.get("supersedes"))
        fm += link_list("AMENDS", "Decision", d.get("amends"))
        write("Decision", slug, fm, f"# {d['title']}\n\n**Rationale:** {d['rationale']}")

    for slug, s in SIGNALS.items():
        fm = ["type: Signal", f"name: {slug}", f'title: "{s["title"]}"',
              f"date: {slug[:10]}", f'source: "{s["source"]}"']
        fm += link_list("CONFIRMS", "Assumption", s.get("confirms"))
        fm += link_list("WEAKENS", "Assumption", s.get("weakens"))
        fm += link_list("BREAKS", "Assumption", s.get("breaks"))
        write("Signal", slug, fm, f"# {s['title']}")

    total = len(PEOPLE) + len(PROJECTS) + len(ASSUMPTIONS) + len(DECISIONS) + len(SIGNALS)
    print(f"wrote {total} notes to {ROOT}")


if __name__ == "__main__":
    main()
