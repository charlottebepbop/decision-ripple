"""Given a signal, which decisions, people and projects get flagged.

Each test uses a throwaway copy of the vault. The committed notes are not modified.
Assertions are on query rows (and, where a sample brief exists, on that brief).
"""

import subprocess
import sys
import unittest
from pathlib import Path

from harness import (
    ROOT, TempVault, exposed_view, ripple_view, tell_view, where,
)

BUY = "Buy the e-cargo bikes outright"
LEASE = "Lease half the e-cargo bikes, buy half"
HUB_Q1 = "Open the Rotterdam South hub in Q1"
HUB_Q2 = "Open the Rotterdam South hub in Q2"
HUB_Q3 = "Open the Rotterdam South hub in Q3"
HIRE_25 = "Hire 25 drivers in Q1"
LYON_LEAD = "Hire the Lyon city lead in December"
FREEZE = "Freeze hiring outside Operations until the Series A closes"
LAUNCH = "Launch Lyon before Paris"
DEPOT = "Put the Lyon depot in Guillotiere"
PARIS = "Paris waits for 3 months of Lyon data"
RUNWAY = "Runway plan assumes the Series A closes in March"
BONUS = "Pay a 3-month retention bonus to drivers"
PRICE = "Price the enterprise tier at EUR 1,800 a month"
SLA_ADD = "The enterprise tier includes the SLA"
CS_FIVE = "Customer Success stays at 5 people"
ANNUAL = "Sign an annual mapping API contract"
MONTHLY = "Pay the mapping API monthly until the optimizer ships"
OPTIMIZER = "Build the route optimizer in house"
SCAN_ONLY = "The optimizer trains on scan data only"
DASHBOARD = "Build the ops dashboard on scan data"
WEEKLY = "Run the weekly ops review from the dashboard"
SLA_98 = "Promise 98% on-time delivery in the SLA"
STAFF = "Staff the south hub with drivers from the north hub"
SCAN_SIGNAL = "Scan coverage was 88% of trips in October"
SUPPLIER_SIGNAL = "Supplier flags a 3-week slip on e-cargo bikes"
CHURN_SIGNAL = "October driver churn was 6.9%"


def titles(rows):
    return [row["decision"] for row in rows]


def by_title(rows):
    return {row["decision"]: row for row in rows}


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        self.box = TempVault()

    def tearDown(self):
        self.box.close()

    def test_budget_break_flags_five_live_decisions_not_the_superseded_purchase(self):
        """A board memo that breaks the Q1 budget flags five live decisions and eight people.

        It does not flag the superseded decision to buy the bikes outright, and it does not
        tell Ken Ito or Lea Novak.
        """
        self.box.add_signal(
            "q1-budget-holds", "BREAKS", "Finance cuts the Q1 budget by 20%",
            source="Board memo", date="2026-12-01",
        )
        self.assertEqual(
            self.box.brief("2026-12-01-finance-cuts-the-q1-budget-by-20.md"),
            (ROOT / "examples/briefs/2026-12-01-finance-cuts-the-q1-budget-by-20.md").read_text(),
        )
        ripple = self.box.query("1-ripple", assumption="q1-budget-holds")
        self.assertEqual(ripple_view(ripple), [
            (HIRE_25, "critical", "medium", ("driver-hiring-q1",)),
            (LYON_LEAD, "critical", "medium", ("driver-hiring-q1", "lyon-launch")),
            (HUB_Q1, "critical", "medium", ("hub-2-rotterdam-south",)),
            (FREEZE, "supporting", "medium", ("customer-sla-program", "enterprise-pricing")),
            (LEASE, "supporting", "medium", ("fleet-ebike-upgrade",)),
        ])
        self.assertNotIn(BUY, titles(ripple))
        self.assertNotIn(LAUNCH, titles(ripple))
        self.assertNotIn(OPTIMIZER, titles(ripple))
        projects = {project for row in ripple for project in row["projects"]}
        self.assertNotIn("route-optimizer-v2", projects)
        self.assertNotIn("ops-dashboard", projects)

        tell = self.box.query("4-tell", assumption="q1-budget-holds")
        self.assertEqual(
            [(row["person"], row["critical"]) for row in tell],
            [
                ("Olu Adeyemi", 3),
                ("Priya Raman", 3),
                ("Saskia de Wit", 2),
                ("Hanna Berg", 1),
                ("Ines Varga", 1),
                ("Tomasz Wilk", 1),
                ("Diego Morales", 0),
                ("Ruth Mensah", 0),
            ],
        )
        people = {row["person"] for row in tell}
        self.assertNotIn("Ken Ito", people)
        self.assertNotIn("Lea Novak", people)

        exposed = where(
            self.box.query("6-exposed"),
            signal="Finance cuts the Q1 budget by 20%", effect="BREAKS",
        )
        self.assertEqual(titles(exposed), titles(ripple))
        self.assertNotIn(BUY, titles(exposed))

    def test_confirmed_assumptions_are_labelled_and_not_risk(self):
        """On a fresh clone, scan coverage breaks four live decisions and the supplier slip weakens the lease.

        The October churn report confirms driver churn. Those rows are labelled confirmation,
        and they name the bonus, the south-hub staffing, and the 98% SLA. They are not risk.
        The superseded bike purchase is absent.
        """
        rows = self.box.query("6-exposed")
        self.assertEqual(exposed_view(rows), [
            (SCAN_SIGNAL, "BREAKS", "ops-data-complete", DASHBOARD, "critical", ("ops-dashboard",)),
            (SCAN_SIGNAL, "BREAKS", "ops-data-complete", OPTIMIZER, "critical", ("route-optimizer-v2",)),
            (SCAN_SIGNAL, "BREAKS", "ops-data-complete", SCAN_ONLY, "critical", ("ops-dashboard", "route-optimizer-v2")),
            (SCAN_SIGNAL, "BREAKS", "ops-data-complete", WEEKLY, "supporting", ("ops-dashboard",)),
            (SUPPLIER_SIGNAL, "WEAKENS", "ebike-supplier-delivers-feb", LEASE, "critical", ("fleet-ebike-upgrade",)),
            (CHURN_SIGNAL, "CONFIRMS", "driver-churn-under-8", SLA_98, "critical", ("customer-sla-program",)),
            (CHURN_SIGNAL, "CONFIRMS", "driver-churn-under-8", STAFF, "critical", ("driver-hiring-q1", "hub-2-rotterdam-south")),
            (CHURN_SIGNAL, "CONFIRMS", "driver-churn-under-8", BONUS, "supporting", ("driver-hiring-q1",)),
        ])
        for row in rows:
            if row["effect"] in ("BREAKS", "WEAKENS"):
                self.assertEqual(row["label"], "risk")
            elif row["effect"] == "CONFIRMS":
                self.assertEqual(row["label"], "confirmation")
        self.assertNotIn(BUY, titles(rows))
        self.assertEqual(
            [row["decision"] for row in rows if row["effect"] == "CONFIRMS"],
            [SLA_98, STAFF, BONUS],
        )

    def test_weaken_and_break_flag_the_same_lyon_decisions_and_support_is_labelled(self):
        """Weakening the Lyon permit flags four live decisions. Breaking it flags the same four, as BREAKS.

        A weaken is not a break, so lyon-launch stays off fragile ground. Supporting the Q1 budget
        lists those decisions in 6-exposed and in the brief, labelled support, and tells nobody.
        The runway plan steers Lyon but does not rest on the permit, so it stays off the ripple.
        So do Diego, Ken, Lea, Tomasz and Ruth.
        """
        self.box.add_signal(
            "lyon-permit-by-jan", "WEAKENS",
            "Lyon permit office asks for a second fire inspection",
            source="Email from the permit office", date="2026-12-03",
        )
        self.assertNotIn(
            "lyon-launch",
            {row["project"] for row in self.box.query("2-fragile")},
        )
        self.assertEqual(
            self.box.brief("2026-12-03-lyon-permit-office-asks-for-a-second-fire-inspection.md"),
            (ROOT / "examples/briefs/2026-12-03-lyon-permit-office-asks-for-a-second-fire-inspection.md").read_text(),
        )
        lyon = [
            (LAUNCH, "critical", "high", ("lyon-launch",)),
            (DEPOT, "critical", "medium", ("lyon-launch",)),
            (LYON_LEAD, "supporting", "medium", ("driver-hiring-q1", "lyon-launch")),
            (PARIS, "supporting", "high", ("lyon-launch",)),
        ]
        ripple = self.box.query("1-ripple", assumption="lyon-permit-by-jan")
        self.assertEqual(ripple_view(ripple), lyon)
        self.assertNotIn(RUNWAY, titles(ripple))
        self.assertNotIn(HIRE_25, titles(ripple))

        weakened = where(self.box.query("6-exposed"), assumption="lyon-permit-by-jan")
        self.assertEqual(
            [(row["effect"], row["decision"]) for row in weakened],
            [("WEAKENS", decision) for decision, *_rest in lyon],
        )

        tell = self.box.query("4-tell", assumption="lyon-permit-by-jan")
        self.assertEqual(
            [(row["person"], row["critical"]) for row in tell],
            [
                ("Hanna Berg", 2),
                ("Ines Varga", 2),
                ("Olu Adeyemi", 2),
                ("Priya Raman", 2),
                ("Saskia de Wit", 0),
            ],
        )
        people = {row["person"] for row in tell}
        for person in ("Diego Morales", "Ken Ito", "Lea Novak", "Tomasz Wilk", "Ruth Mensah"):
            self.assertNotIn(person, people)

        self.box.add_signal(
            "lyon-permit-by-jan", "BREAKS", "Lyon permit is refused",
            source="Permit office", date="2026-12-08",
        )
        broken = where(
            self.box.query("6-exposed"),
            signal="Lyon permit is refused", effect="BREAKS",
        )
        self.assertEqual(titles(broken), titles(ripple))
        self.assertNotIn(RUNWAY, titles(broken))
        still_weakened = where(
            self.box.query("6-exposed"),
            signal="Lyon permit office asks for a second fire inspection",
        )
        self.assertTrue(still_weakened)
        self.assertTrue(all(row["effect"] == "WEAKENS" for row in still_weakened))

        self.box.add_signal(
            "q1-budget-holds", "SUPPORTS", "The Q1 budget still matches the plan",
            source="Finance note", date="2026-12-09",
        )
        brief = self.box.brief("2026-12-09-the-q1-budget-still-matches-the-plan.md")
        self.assertIn("## Support, not a risk", brief)
        self.assertIn("No live decision needs a second look.", brief)
        self.assertIn(HIRE_25, brief)
        self.assertNotIn("most exposed", brief)
        self.assertNotIn(BUY, brief)
        supported = where(self.box.query("6-exposed"), signal="The Q1 budget still matches the plan")
        self.assertEqual(titles(supported), titles(self.box.query("1-ripple", assumption="q1-budget-holds")))
        self.assertTrue(supported)
        self.assertTrue(all(row["effect"] == "SUPPORTS" and row["label"] == "support" for row in supported))
        self.assertNotIn(BUY, titles(supported))

    def test_one_memo_hitting_two_assumptions_flags_the_union_once(self):
        """One memo breaks the budget and weakens the bike delivery.

        The lease is on both lists and is told once. The brief matches the sample.
        Ken and Lea are not told. The superseded bike purchase is not flagged.
        """
        self.box.add_signal(
            "q1-budget-holds", "BREAKS",
            "Finance cuts the Q1 budget and the bike supplier slips",
            source="Board memo", date="2026-12-04",
            also=[("ebike-supplier-delivers-feb", "WEAKENS")],
        )
        filename = "2026-12-04-finance-cuts-the-q1-budget-and-the-bike-supplier-slips.md"
        self.assertEqual(
            self.box.brief(filename),
            (ROOT / "examples/briefs" / filename).read_text(),
        )
        budget = self.box.query("1-ripple", assumption="q1-budget-holds")
        supplier = self.box.query("1-ripple", assumption="ebike-supplier-delivers-feb")
        self.assertEqual(titles(supplier), [LEASE])
        self.assertEqual(supplier[0]["weight"], "critical")
        self.assertIn(LEASE, titles(budget))
        self.assertEqual(len([row for row in budget if row["decision"] == LEASE]), 1)
        self.assertNotIn(BUY, titles(budget) + titles(supplier))

        exposed = self.box.query("6-exposed")
        budget_rows = where(
            exposed, signal="Finance cuts the Q1 budget and the bike supplier slips",
            assumption="q1-budget-holds", effect="BREAKS",
        )
        supplier_rows = where(
            exposed, signal="Finance cuts the Q1 budget and the bike supplier slips",
            assumption="ebike-supplier-delivers-feb", effect="WEAKENS",
        )
        self.assertEqual(titles(budget_rows), titles(budget))
        self.assertEqual(titles(supplier_rows), [LEASE])
        brief = self.box.brief(filename)
        self.assertNotIn("Ken Ito", brief)
        self.assertNotIn("Lea Novak", brief)

    def test_one_decision_critical_on_two_assumptions_counts_once(self):
        """A decision that rests critically on both assumptions in one memo counts once in the tell list.

        It is still flagged under each assumption. Priya is at 5 critical, not 6.
        """
        self.box.add_decision(
            "Hold both the budget and the subsidy",
            date="2026-12-21", project="fleet-ebike-upgrade", by="priya-raman",
            rests=("q1-budget-holds:critical", "eu-cargo-bike-subsidy:critical"),
            rationale="One decision, two critical assumptions.",
        )
        self.box.add_signal(
            "q1-budget-holds", "BREAKS", "Both budget and subsidy fail together",
            source="Test memo", date="2026-12-22",
            also=[("eu-cargo-bike-subsidy", "BREAKS")],
        )
        hold = "Hold both the budget and the subsidy"
        budget = self.box.query("1-ripple", assumption="q1-budget-holds")
        subsidy = self.box.query("1-ripple", assumption="eu-cargo-bike-subsidy")
        self.assertIn((hold, "critical"), [(row["decision"], row["weight"]) for row in budget])
        self.assertEqual(ripple_view(subsidy), [
            ("Apply for the Dutch e-cargo-bike subsidy", "critical", "high", ("fleet-ebike-upgrade",)),
            (hold, "critical", "medium", ("fleet-ebike-upgrade",)),
            (LEASE, "supporting", "medium", ("fleet-ebike-upgrade",)),
        ])
        self.assertNotIn(BUY, titles(budget) + titles(subsidy))

        exposed = where(self.box.query("6-exposed"), signal="Both budget and subsidy fail together")
        held = [row for row in exposed if row["decision"] == hold]
        self.assertEqual(
            sorted((row["assumption"], row["effect"], row["weight"]) for row in held),
            [
                ("eu-cargo-bike-subsidy", "BREAKS", "critical"),
                ("q1-budget-holds", "BREAKS", "critical"),
            ],
        )

    def test_one_memo_counts_a_doubly_critical_decision_once_per_person(self):
        """One memo on two assumptions counts a decision that is critical under both once per person.

        The decision is still named once on that person's line. Priya is at 5 critical, not 6.
        """
        self.box.add_decision(
            "Hold both the budget and the subsidy",
            date="2026-12-21", project="fleet-ebike-upgrade", by="priya-raman",
            rests=("q1-budget-holds:critical", "eu-cargo-bike-subsidy:critical"),
            rationale="One decision, two critical assumptions.",
        )
        self.box.add_signal(
            "q1-budget-holds", "BREAKS", "Both budget and subsidy fail together",
            source="Test memo", date="2026-12-22",
            also=[("eu-cargo-bike-subsidy", "BREAKS")],
        )
        hold = "Hold both the budget and the subsidy"
        brief = self.box.brief("2026-12-22-both-budget-and-subsidy-fail-together.md")
        self.assertIn("**Priya Raman** (Head of Finance, 5 critical)", brief)
        self.assertIn("**Tomasz Wilk** (COO, 3 critical)", brief)
        self.assertIn("**Diego Morales** (Fleet Lead, 2 critical)", brief)
        priya = next(line for line in brief.splitlines() if line.startswith("- **Priya Raman**"))
        self.assertEqual(priya.count(hold), 1)

    def test_superseding_twice_follows_to_the_live_hub_and_drops_the_old_budget_link(self):
        """Replacing the Q1 hub twice points both older notes at Q3, the one that is still live.

        Q2 and Q3 do not rest on the Q1 budget. After the budget break, Q1, Q2 and Q3 are not flagged.
        The other four budget decisions still are. Tomasz's critical count drops to zero.
        """
        self.box.add_decision(
            HUB_Q2, date="2026-12-05", project="hub-2-rotterdam-south",
            by=("olu-adeyemi", "tomasz-wilk"),
            rests=("south-hub-lease-signed:critical", "series-a-close-march"),
            supersedes="2026-07-29-open-south-hub-q1",
            rationale="The Q1 budget was cut by 20%.",
        )
        self.box.add_decision(
            HUB_Q3, date="2026-12-10", project="hub-2-rotterdam-south",
            by=("olu-adeyemi", "tomasz-wilk"),
            rests=("south-hub-lease-signed:critical", "series-a-close-march"),
            supersedes="2026-12-05-open-the-rotterdam-south-hub-in-q2",
            rationale="The Q2 opening slipped.",
        )
        self.box.add_signal(
            "q1-budget-holds", "BREAKS", "Finance cuts the Q1 budget by 20%",
            source="Board memo", date="2026-12-01",
        )
        pre = by_title(self.box.query("3-precheck", project="hub-2-rotterdam-south"))
        self.assertEqual(pre[HUB_Q1]["status"], "superseded")
        self.assertEqual(pre[HUB_Q1]["replaced_by"], [HUB_Q3])
        self.assertEqual(
            pre[HUB_Q1]["pressure"],
            ["q1-budget-holds: Finance cuts the Q1 budget by 20%"],
        )
        self.assertEqual(pre[HUB_Q2]["status"], "superseded")
        self.assertEqual(pre[HUB_Q2]["replaced_by"], [HUB_Q3])
        self.assertEqual(pre[HUB_Q2]["pressure"], [])
        self.assertEqual(pre[HUB_Q3]["status"], "live")
        self.assertEqual(pre[HUB_Q3]["replaced_by"], [])
        self.assertEqual(pre[HUB_Q3]["pressure"], [])
        self.assertNotIn(HUB_Q2, pre[HUB_Q1]["replaced_by"])

        ripple = self.box.query("1-ripple", assumption="q1-budget-holds")
        self.assertEqual(titles(ripple), [HIRE_25, LYON_LEAD, FREEZE, LEASE])
        for title in (HUB_Q1, HUB_Q2, HUB_Q3, BUY):
            self.assertNotIn(title, titles(ripple))
        exposed = where(self.box.query("6-exposed"), signal="Finance cuts the Q1 budget by 20%")
        self.assertEqual(titles(exposed), titles(ripple))

        tell = self.box.query("4-tell", assumption="q1-budget-holds")
        self.assertEqual(
            [(row["person"], row["critical"]) for row in tell],
            [
                ("Olu Adeyemi", 2),
                ("Priya Raman", 2),
                ("Saskia de Wit", 2),
                ("Hanna Berg", 1),
                ("Ines Varga", 1),
                ("Diego Morales", 0),
                ("Ruth Mensah", 0),
                ("Tomasz Wilk", 0),
            ],
        )

    def test_supersession_walk_stops_at_five_hops(self):
        """The pre-check and the why-search name the live decision up to five SUPERSEDES hops.

        A sixth hop does not. The live decision at the far end is not reported for the oldest note,
        and an unrelated decision on the same project is not swept into the chain.
        """
        from graph import slug

        titles = [
            "Hop zero anchor", "Hop one", "Hop two", "Hop three",
            "Hop four", "Hop five", "Hop six",
        ]
        previous = None
        for index, title in enumerate(titles[:6]):
            date = f"2026-12-{index + 1:02d}"
            self.box.add_decision(
                title, date=date, project="route-optimizer-v2", by="ken-ito",
                rests=("route-api-pricing-stable",),
                supersedes=previous,
                rationale="hopseed marks the oldest hop." if index == 0 else "The previous hop is done.",
            )
            previous = f"{date}-{slug(title)}"

        pre = by_title(self.box.query("3-precheck", project="route-optimizer-v2"))
        self.assertEqual(pre["Hop zero anchor"]["status"], "superseded")
        self.assertEqual(pre["Hop zero anchor"]["replaced_by"], ["Hop five"])
        self.assertEqual(pre["Hop one"]["replaced_by"], ["Hop five"])
        self.assertEqual(pre["Hop five"]["status"], "live")
        self.assertEqual(pre["Hop five"]["replaced_by"], [])
        why = by_title(self.box.query("5-why", term="hopseed"))
        self.assertEqual(set(why), {"Hop zero anchor"})
        self.assertEqual(why["Hop zero anchor"]["replaced_by"], ["Hop five"])

        self.box.add_decision(
            "Hop six", date="2026-12-07", project="route-optimizer-v2", by="ken-ito",
            rests=("route-api-pricing-stable",),
            supersedes=previous,
            rationale="The previous hop is done.",
        )
        pre = by_title(self.box.query("3-precheck", project="route-optimizer-v2"))
        self.assertEqual(pre["Hop zero anchor"]["replaced_by"], [])
        self.assertNotIn("Hop six", pre["Hop zero anchor"]["replaced_by"])
        self.assertEqual(pre["Hop one"]["replaced_by"], ["Hop six"])
        self.assertEqual(pre["Hop five"]["replaced_by"], ["Hop six"])
        self.assertEqual(pre["Hop six"]["status"], "live")
        self.assertEqual(pre["Hop six"]["replaced_by"], [])
        self.assertEqual(pre[ANNUAL]["replaced_by"], [MONTHLY])
        self.assertEqual(pre[MONTHLY]["replaced_by"], [])
        why = by_title(self.box.query("5-why", term="hopseed"))
        self.assertEqual(set(why), {"Hop zero anchor"})
        self.assertEqual(why["Hop zero anchor"]["replaced_by"], [])
        self.assertEqual(why["Hop zero anchor"]["status"], "superseded")

    def test_an_amendment_stays_live_and_gets_flagged(self):
        """Amending the enterprise price keeps the original live. It is not reported as replaced.

        Breaking enterprise demand flags the original, the amendment, and customer success staying at five.
        It does not flag driver hiring or the bike lease.
        """
        self.box.add_signal(
            "enterprise-demand-3-pilots", "BREAKS", "Two pilots pulled out",
            source="Sales note", date="2026-12-11",
        )
        ripple = self.box.query("1-ripple", assumption="enterprise-demand-3-pilots")
        self.assertEqual(ripple_view(ripple), [
            (PRICE, "critical", "medium", ("enterprise-pricing",)),
            (CS_FIVE, "supporting", "medium", ("customer-sla-program",)),
            (SLA_ADD, "supporting", "low", ("customer-sla-program", "enterprise-pricing")),
        ])
        self.assertNotIn(HIRE_25, titles(ripple))
        self.assertNotIn(LEASE, titles(ripple))
        self.assertNotIn(BUY, titles(ripple))

        pre = by_title(self.box.query("3-precheck", project="enterprise-pricing"))
        self.assertEqual(pre[PRICE]["status"], "live")
        self.assertEqual(pre[PRICE]["replaced_by"], [])
        self.assertEqual(pre[SLA_ADD]["status"], "live")
        self.assertEqual(pre[SLA_ADD]["replaced_by"], [])
        self.assertEqual(
            pre[PRICE]["pressure"],
            ["enterprise-demand-3-pilots: Two pilots pulled out"],
        )
        self.assertNotIn(HUB_Q1, pre)
        self.assertNotIn(ANNUAL, pre)

        exposed = where(self.box.query("6-exposed"), signal="Two pilots pulled out")
        self.assertEqual(
            [(row["decision"], row["effect"], row["weight"]) for row in exposed],
            [
                (PRICE, "BREAKS", "critical"),
                (CS_FIVE, "BREAKS", "supporting"),
                (SLA_ADD, "BREAKS", "supporting"),
            ],
        )
        tell = self.box.query("4-tell", assumption="enterprise-demand-3-pilots")
        self.assertEqual(
            [(row["person"], row["critical"]) for row in tell],
            [
                ("Hanna Berg", 1),
                ("Priya Raman", 1),
                ("Ruth Mensah", 1),
                ("Olu Adeyemi", 0),
                ("Tomasz Wilk", 0),
            ],
        )
        people = {row["person"] for row in tell}
        for person in ("Ken Ito", "Lea Novak", "Diego Morales", "Saskia de Wit", "Ines Varga"):
            self.assertNotIn(person, people)

    def test_precheck_names_an_amendment_on_the_decision_it_changes(self):
        """3-precheck follows AMENDS the way it follows SUPERSEDES.

        The EUR 1,800 price stays live and is not reported as replaced. The row names the
        amendment and the two assumptions that amendment rests on. The amendment's own row
        does not name itself.
        """
        pre = by_title(self.box.query("3-precheck", project="enterprise-pricing"))
        shown = " ".join(str(value) for value in pre[PRICE].values())
        self.assertIn(SLA_ADD, shown)
        self.assertEqual(pre[PRICE]["status"], "live")
        self.assertEqual(pre[PRICE]["replaced_by"], [])
        self.assertEqual(pre[PRICE]["amended_by"], [SLA_ADD])
        self.assertEqual(sorted(pre[PRICE]["amendment_rests_on"]), [
            f"{SLA_ADD}: enterprise-demand-3-pilots (supporting)",
            f"{SLA_ADD}: sla-penalties-capped (critical)",
        ])
        self.assertEqual(pre[SLA_ADD]["amended_by"], [])
        self.assertEqual(pre[SLA_ADD]["amendment_rests_on"], [])
        self.assertEqual(pre[FREEZE]["amended_by"], [])

    def test_decision_with_no_assumptions_is_not_flagged(self):
        """A decision that rests on nothing is not flagged when the Lyon permit breaks.

        The pre-check still lists it, with no pressure. The four decisions that do rest on the permit stay flagged.
        """
        self.box.add_decision(
            "Publish the depot hours", date="2026-12-15", project="lyon-launch",
            by="olu-adeyemi", rationale="Riders need the hours on the door.",
        )
        self.box.add_signal(
            "lyon-permit-by-jan", "BREAKS", "The Lyon permit missed January",
            source="Permit office", date="2026-12-16",
        )
        ripple = self.box.query("1-ripple", assumption="lyon-permit-by-jan")
        self.assertEqual(titles(ripple), [LAUNCH, DEPOT, LYON_LEAD, PARIS])
        self.assertNotIn("Publish the depot hours", titles(ripple))
        exposed = where(self.box.query("6-exposed"), signal="The Lyon permit missed January")
        self.assertEqual(titles(exposed), titles(ripple))
        self.assertNotIn("Publish the depot hours", titles(exposed))

        pre = by_title(self.box.query("3-precheck", project="lyon-launch"))
        hours = pre["Publish the depot hours"]
        self.assertEqual(hours["status"], "live")
        self.assertEqual(hours["replaced_by"], [])
        self.assertEqual(hours["pressure"], [])
        self.assertEqual(
            pre[LAUNCH]["pressure"],
            ["lyon-permit-by-jan: The Lyon permit missed January"],
        )
        self.assertIn(DEPOT, pre)
        self.assertNotIn(HIRE_25, pre)

    def test_precheck_names_pressure_and_the_live_replacement(self):
        """Before work on the route optimizer: two decisions are under the scan-coverage break, and the annual contract points at the live monthly one.

        The south hub pre-check is quiet: three live decisions, no pressure, no replacement.
        The bike lease does not steer the hub, so it is not on that list.
        """
        route = self.box.query("3-precheck", project="route-optimizer-v2")
        self.assertEqual(titles(route), [OPTIMIZER, MONTHLY, SCAN_ONLY, ANNUAL])
        found = by_title(route)
        self.assertEqual(found[OPTIMIZER]["status"], "live")
        self.assertEqual(
            found[OPTIMIZER]["pressure"],
            ["ops-data-complete: Scan coverage was 88% of trips in October"],
        )
        self.assertEqual(found[OPTIMIZER]["replaced_by"], [])
        self.assertEqual(
            found[SCAN_ONLY]["pressure"],
            ["ops-data-complete: Scan coverage was 88% of trips in October"],
        )
        self.assertEqual(found[MONTHLY]["pressure"], [])
        self.assertEqual(found[MONTHLY]["status"], "live")
        self.assertEqual(found[ANNUAL]["status"], "superseded")
        self.assertEqual(found[ANNUAL]["replaced_by"], [MONTHLY])
        self.assertEqual(found[ANNUAL]["pressure"], [])
        self.assertNotIn(HUB_Q1, found)

        hub = self.box.query("3-precheck", project="hub-2-rotterdam-south")
        self.assertEqual(titles(hub), [HUB_Q1, RUNWAY, STAFF])
        for row in hub:
            self.assertEqual(row["status"], "live")
            self.assertEqual(row["replaced_by"], [])
            self.assertEqual(row["amended_by"], [])
            self.assertEqual(row["amendment_rests_on"], [])
            self.assertEqual(row["pressure"], [])
        self.assertNotIn(LEASE, titles(hub))
        self.assertNotIn(ANNUAL, titles(hub))
        for row in route:
            self.assertEqual(row["amended_by"], [])
            self.assertEqual(row["amendment_rests_on"], [])

    def test_fragile_ground_is_only_the_three_weak_projects(self):
        """Fragile ground is the route optimizer, the ops dashboard, and the SLA program.

        The route optimizer and the dashboard already sit on the scan-coverage break.
        The SLA program is fragile and not yet hit. The hub, Lyon, hiring, fleet and enterprise pricing are not fragile.
        """
        rows = {row["project"]: row for row in self.box.query("2-fragile")}
        self.assertEqual(
            set(rows),
            {"route-optimizer-v2", "ops-dashboard", "customer-sla-program"},
        )
        self.assertEqual(rows["route-optimizer-v2"]["low_confidence_decisions"], 3)
        self.assertEqual(
            set(rows["route-optimizer-v2"]["decisions"]),
            {MONTHLY, SCAN_ONLY, OPTIMIZER},
        )
        self.assertEqual(rows["route-optimizer-v2"]["hit_assumptions"], ["ops-data-complete (BREAKS)"])
        self.assertEqual(rows["ops-dashboard"]["low_confidence_decisions"], 2)
        self.assertEqual(set(rows["ops-dashboard"]["decisions"]), {WEEKLY, SCAN_ONLY})
        self.assertEqual(rows["ops-dashboard"]["hit_assumptions"], ["ops-data-complete (BREAKS)"])
        self.assertEqual(rows["customer-sla-program"]["low_confidence_decisions"], 2)
        self.assertEqual(set(rows["customer-sla-program"]["decisions"]), {SLA_ADD, SLA_98})
        self.assertEqual(rows["customer-sla-program"]["hit_assumptions"], [])
        for project in rows:
            self.assertEqual(rows[project]["high_confidence_broken"], 0)
        for project in (
            "hub-2-rotterdam-south", "lyon-launch", "driver-hiring-q1",
            "fleet-ebike-upgrade", "enterprise-pricing",
        ):
            self.assertNotIn(project, rows)

    def test_why_search_finds_the_decision_and_what_replaced_it(self):
        """Searching 'mapping' finds the superseded annual contract and names the live monthly decision.

        It also finds the in-house optimizer, which mentions the contract in its note, and not driver hiring.
        'Guillotiere' finds only the depot decision. A nonsense term finds nothing.
        """
        found = by_title(self.box.query("5-why", term="mapping"))
        self.assertEqual(set(found), {ANNUAL, MONTHLY, OPTIMIZER})
        self.assertEqual(found[ANNUAL]["status"], "superseded")
        self.assertEqual(found[ANNUAL]["replaced_by"], [MONTHLY])
        self.assertEqual(sorted(found[ANNUAL]["rests_on"]), ["route-api-pricing-stable"])
        self.assertEqual(sorted(found[ANNUAL]["decided_by"]), ["Ken Ito", "Priya Raman"])
        self.assertEqual(found[MONTHLY]["status"], "live")
        self.assertEqual(found[MONTHLY]["replaced_by"], [])
        self.assertEqual(sorted(found[MONTHLY]["decided_by"]), ["Ken Ito"])
        self.assertEqual(found[OPTIMIZER]["status"], "live")
        self.assertEqual(
            sorted(found[OPTIMIZER]["rests_on"]),
            ["ops-data-complete", "route-api-pricing-stable"],
        )
        self.assertNotIn(HIRE_25, found)

        depot = by_title(self.box.query("5-why", term="Guillotiere"))
        self.assertEqual(set(depot), {DEPOT})
        self.assertEqual(depot[DEPOT]["status"], "live")
        self.assertEqual(depot[DEPOT]["replaced_by"], [])
        self.assertEqual(sorted(depot[DEPOT]["decided_by"]), ["Olu Adeyemi"])
        self.assertEqual(sorted(depot[DEPOT]["rests_on"]), ["lyon-permit-by-jan"])
        self.assertNotIn(LAUNCH, depot)

        self.assertEqual(self.box.query("5-why", term="zzznomatch"), [])

    def test_fragile_includes_high_confidence_decisions_on_a_broken_assumption(self):
        """A break under high-confidence decisions puts that project on 2-fragile and counts those decisions.

        Launch Lyon before Paris and Paris waits for 3 months of Lyon data are high confidence
        and rest on the Lyon permit. The depot decision is critical but medium confidence, so
        it is not part of this count. driver-hiring-q1 is not fragile from the city-lead hire.
        """
        self.box.add_signal(
            "lyon-permit-by-jan", "BREAKS", "The Lyon permit missed January",
            source="Permit office", date="2026-12-16",
        )
        rows = {row["project"]: row for row in self.box.query("2-fragile")}
        self.assertIn("lyon-launch", rows)
        lyon = rows["lyon-launch"]
        self.assertEqual(lyon["high_confidence_broken"], 2)
        self.assertEqual(lyon["low_confidence_decisions"], 0)
        self.assertEqual(set(lyon["decisions"]), {LAUNCH, PARIS})
        self.assertEqual(lyon["hit_assumptions"], ["lyon-permit-by-jan (BREAKS)"])
        self.assertNotIn("driver-hiring-q1", rows)
        self.assertIn("route-optimizer-v2", rows)
        self.assertEqual(rows["route-optimizer-v2"]["high_confidence_broken"], 0)

    def test_exposed_keeps_supporting_evidence_next_to_a_break(self):
        """A SUPPORTS signal on an assumption that is also broken shows up beside the break, labelled support."""
        self.box.add_signal(
            "ops-data-complete", "SUPPORTS", "A recount found the missing scans",
            source="Ops data check", date="2026-12-18",
        )
        rows = where(self.box.query("6-exposed"), assumption="ops-data-complete")
        effects = {row["effect"] for row in rows}
        self.assertIn("BREAKS", effects)
        self.assertIn("SUPPORTS", effects)
        self.assertTrue(all(row["label"] == "risk" for row in rows if row["effect"] == "BREAKS"))
        self.assertTrue(all(row["label"] == "support" for row in rows if row["effect"] == "SUPPORTS"))
        self.assertIn("A recount found the missing scans", [row["signal"] for row in rows if row["effect"] == "SUPPORTS"])

    def test_add_signal_refuses_an_empty_phantom_assumption(self):
        """A signal against the empty note Relate made from a typo is refused, and the closest real name is given."""
        phantom = self.box.vault / "Assumption" / "q1-budget-hold.md"
        phantom.write_text("---\ntype: Assumption\nname: q1-budget-hold\n---\n")
        result = subprocess.run(
            [
                "python3", "scripts/add_signal.py", "q1-budget-hold", "BREAKS", "Budget typo",
                "--source", "Test", "--date", "2026-12-20",
            ],
            cwd=ROOT, env=self.box.env, text=True, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        text = result.stdout + result.stderr
        self.assertIn("empty note", text)
        self.assertIn("q1-budget-holds", text)
        self.assertEqual(list(self.box.vault.glob("Signal/*budget-typo*")), [])
        self.box.add_signal(
            "q1-budget-holds", "BREAKS", "Finance cuts the Q1 budget by 20%",
            source="Board memo", date="2026-12-01",
        )
        self.assertIn(HIRE_25, titles(self.box.query("1-ripple", assumption="q1-budget-holds")))

    def test_decision_missing_status_disappears_from_the_ripple(self):
        """A decision with no status is dropped by 1-ripple, 4-tell and 6-exposed. The vault check says so. The queries stay as they are."""
        note = self.box.vault / "Decision" / "2026-12-18-paint-without-status.md"
        note.write_text(
            "---\n"
            "type: Decision\n"
            "name: 2026-12-18-paint-without-status\n"
            "title: Paint without a status\n"
            "date: 2026-12-18\n"
            "confidence: high\n"
            "RESTS_ON:\n"
            "  - target: \"[[Assumption/q1-budget-holds]]\"\n"
            "    weight: critical\n"
            "DECIDED_BY:\n"
            "  - \"[[Person/priya-raman]]\"\n"
            "STEERS:\n"
            "  - \"[[Project/fleet-ebike-upgrade]]\"\n"
            "---\n\n"
            "# Paint without a status\n"
        )
        self.box.add_signal(
            "q1-budget-holds", "BREAKS", "Finance cuts the Q1 budget by 20%",
            source="Board memo", date="2026-12-01",
        )
        ripple = self.box.query("1-ripple", assumption="q1-budget-holds")
        self.assertNotIn("Paint without a status", titles(ripple))
        self.assertIn(HIRE_25, titles(ripple))
        exposed = where(self.box.query("6-exposed"), signal="Finance cuts the Q1 budget by 20%")
        self.assertNotIn("Paint without a status", titles(exposed))
        told = " ".join(" ".join(row["decisions"]) for row in self.box.query("4-tell", assumption="q1-budget-holds"))
        self.assertNotIn("Paint without a status", told)
        from check_vault import check_vault
        text = "\n".join(
            f"{issue.path}\n{issue.message}" for issue in check_vault(self.box.vault).issues
        )
        self.assertIn("2026-12-18-paint-without-status.md", text)
        self.assertIn("missing status", text)
        self.assertIn("disappears from all three", text)


    def test_logged_decision_keeps_the_reasoning_and_names_new_notes(self):
        """Context, options, and who decided are stored, and a new assumption or person is created only when named.

        A dry run writes nothing. The Q1 hub decision points at the Q2 note. The new assumption is supporting.
        """
        title = "Open the Rotterdam South hub in Q2"
        cmd = [
            sys.executable, "scripts/add_decision.py", title,
            "--date", "2026-12-01",
            "--project", "hub-2-rotterdam-south",
            "--by", "olu-adeyemi", "--by", "tomasz-wilk", "--by", "mina-kowalski",
            "--rests-on", "south-hub-lease-signed:critical",
            "--rests-on", "series-a-close-march",
            "--rests-on", "q2-fit-out-fits",
            "--new-assumption", "q2-fit-out-fits", "The Q2 fit-out fits the revised budget.",
            "--new-person", "mina-kowalski", "Mina Kowalski", "Hub planner",
            "--supersedes", "2026-07-29-open-south-hub-q1",
            "--rationale", "The Q1 budget was cut by 20%.",
            "--context", "The north hub still runs at 92% capacity. The revised Q2 envelope covers the fit-out.",
            "--option", "Open in Q2.",
            "--option", "Cancel the hub. Lost because the north hub stays full.",
            "--who-decided", 'Olu Adeyemi and Tomasz Wilk decided. Mina Kowalski said "Q2".',
        ]
        note = self.box.vault / "Decision" / "2026-12-01-open-the-rotterdam-south-hub-in-q2.md"
        person = self.box.vault / "Person" / "mina-kowalski.md"
        assumption = self.box.vault / "Assumption" / "q2-fit-out-fits.md"
        preview = subprocess.run(cmd + ["--dry-run"], cwd=ROOT, env=self.box.env, text=True, capture_output=True)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertIn("Dry run. Nothing written.", preview.stdout)
        self.assertIn("q2-fit-out-fits (supporting, new)", preview.stdout)
        self.assertIn("mina-kowalski (new)", preview.stdout)
        self.assertIn("## Context", preview.stdout)
        self.assertIn("## Options considered", preview.stdout)
        self.assertIn("## Who decided", preview.stdout)
        self.assertIn("Supersedes: 2026-07-29-open-south-hub-q1", preview.stdout)
        self.assertFalse(note.exists())
        self.assertFalse(person.exists())
        self.assertFalse(assumption.exists())

        written = subprocess.run(cmd, cwd=ROOT, env=self.box.env, text=True, capture_output=True)
        self.assertEqual(written.returncode, 0, written.stderr + written.stdout)
        self.assertIn("replaced by: Open the Rotterdam South hub in Q2", written.stdout)
        text = note.read_text(encoding="utf-8")
        frontmatter, body = text.split("---", 2)[1], text.split("---", 2)[2]
        self.assertNotIn("\ntext:", frontmatter)
        self.assertIn("status: live", frontmatter)
        self.assertIn("**Rationale:** The Q1 budget was cut by 20%.", body)
        self.assertIn("## Context\nThe north hub still runs at 92% capacity.", body)
        self.assertIn("## Options considered\n- Open in Q2.", body)
        self.assertIn('Mina Kowalski said "Q2".', body)
        self.assertIn("# Mina Kowalski", person.read_text(encoding="utf-8"))
        self.assertIn("Hub planner", person.read_text(encoding="utf-8"))
        self.assertIn("# The Q2 fit-out fits the revised budget.", assumption.read_text(encoding="utf-8"))

        found = by_title(self.box.query("5-why", term="revised Q2 envelope"))
        self.assertIn(title, found)
        self.assertEqual(
            sorted(found[title]["decided_by"]),
            ["Mina Kowalski", "Olu Adeyemi", "Tomasz Wilk"],
        )
        fit = by_title(self.box.query("1-ripple", assumption="q2-fit-out-fits"))
        self.assertEqual(fit[title]["weight"], "supporting")
        lease = by_title(self.box.query("1-ripple", assumption="south-hub-lease-signed"))
        self.assertEqual(lease[title]["weight"], "critical")
        hub = by_title(self.box.query("3-precheck", project="hub-2-rotterdam-south"))
        self.assertEqual(hub[HUB_Q1]["status"], "superseded")
        self.assertEqual(hub[HUB_Q1]["replaced_by"], [title])
        self.assertEqual(hub[title]["status"], "live")

        checked = subprocess.run(
            [sys.executable, "scripts/check_vault.py"],
            cwd=ROOT, env=self.box.env, text=True, capture_output=True,
        )
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_a_typo_or_an_unlinked_new_note_writes_nothing(self):
        """A missing slug is refused and named when it is close. A new assumption that nothing rests on is refused."""
        typo = subprocess.run(
            [
                sys.executable, "scripts/add_decision.py", "Paint the dock",
                "--date", "2026-12-02",
                "--project", "hub-2-rotterdam-south",
                "--by", "olu-adeyemi",
                "--rests-on", "q1-budget-hold:critical",
                "--rationale", "A typo must not become a note.",
            ],
            cwd=ROOT, env=self.box.env, text=True, capture_output=True,
        )
        self.assertNotEqual(typo.returncode, 0, typo.stdout)
        self.assertIn("Did you mean q1-budget-holds?", typo.stderr)
        self.assertFalse((self.box.vault / "Assumption" / "q1-budget-hold.md").exists())
        self.assertEqual(list(self.box.vault.glob("Decision/*paint-the-dock*")), [])

        unlinked = subprocess.run(
            [
                sys.executable, "scripts/add_decision.py", "Paint the dock",
                "--date", "2026-12-02",
                "--project", "hub-2-rotterdam-south",
                "--by", "olu-adeyemi",
                "--rests-on", "q1-budget-holds",
                "--new-assumption", "q2-fit-out-fits", "The Q2 fit-out fits the revised budget.",
                "--rationale", "The new assumption is not linked.",
            ],
            cwd=ROOT, env=self.box.env, text=True, capture_output=True,
        )
        self.assertNotEqual(unlinked.returncode, 0, unlinked.stdout)
        self.assertIn("does not rest on it", unlinked.stderr)
        self.assertFalse((self.box.vault / "Assumption" / "q2-fit-out-fits.md").exists())

        duplicate = subprocess.run(
            [
                sys.executable, "scripts/add_decision.py", "Rename the hub lead",
                "--date", "2026-12-03",
                "--project", "hub-2-rotterdam-south",
                "--by", "nia-okonkwo",
                "--new-person", "nia-okonkwo", "Olu Adeyemi", "Planner",
                "--rests-on", "q1-budget-holds",
                "--rationale", "This person already has a note.",
            ],
            cwd=ROOT, env=self.box.env, text=True, capture_output=True,
        )
        self.assertNotEqual(duplicate.returncode, 0, duplicate.stdout)
        self.assertIn("already headed 'Olu Adeyemi' (olu-adeyemi)", duplicate.stderr)
        self.assertFalse((self.box.vault / "Person" / "nia-okonkwo.md").exists())
        self.assertEqual(list(self.box.vault.glob("Decision/*rename-the-hub-lead*")), [])

    def test_signal_dry_run_writes_neither_note_nor_brief(self):
        before = sorted(path.name for path in self.box.vault.glob("Signal/*.md"))
        result = subprocess.run(
            [
                sys.executable, "scripts/add_signal.py", "q1-budget-holds", "BREAKS",
                "Finance cuts the Q1 budget by 20%",
                "--source", "Board memo", "--date", "2026-12-01", "--dry-run",
            ],
            cwd=ROOT, env=self.box.env, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Dry run. Nothing written.", result.stdout)
        self.assertIn("BREAKS q1-budget-holds:", result.stdout)
        self.assertEqual(sorted(path.name for path in self.box.vault.glob("Signal/*.md")), before)
        self.assertEqual(list(self.box.briefs.glob("*.md")), [])


if __name__ == "__main__":
    unittest.main()
