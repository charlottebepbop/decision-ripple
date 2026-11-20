"""Weekly briefing on a throwaway copy of the vault.

The committed notes are not modified. These tests cover the window, grouping,
mixed evidence, a decision counted once, and assumptions that have gone quiet.
"""

import subprocess
import unittest

from harness import ROOT, TempVault


SCAN = "Scan coverage was 88% of trips in October"
SUPPLIER = "Supplier flags a 3-week slip on e-cargo bikes"
CHURN = "October driver churn was 6.9%"
BUY = "Buy the e-cargo bikes outright"
LAUNCH = "Launch Lyon before Paris"
PARIS = "Paris waits for 3 months of Lyon data"
HOLD = "Hold both the budget and the subsidy"

QUIET = [
    "At least 3 enterprise pilots convert by end of Q1.",
    "Lyon grants the cargo-bike depot permit by 15 Jan.",
    "SLA penalties are capped at 5% of contract value.",
    "Support tickets per customer stay at or below 1.4 a month.",
    "The Dutch e-cargo-bike subsidy renews for 2027.",
    "The Q1 budget stays at plan, EUR 2.4m.",
    "The Rotterdam South lease is signed by December.",
    "The Series A closes by end of March.",
    "The mapping API price stays flat through 2027.",
    "We get 40 qualified driver applicants a month.",
    "Winter parcel volume drops by at most 15%.",
]


def section(text, heading):
    marker = f"## {heading}\n"
    start = text.index(marker) + len(marker)
    rest = text[start:]
    nxt = rest.find("\n## ")
    return rest if nxt == -1 else rest[:nxt]


class WeeklyTests(unittest.TestCase):
    def setUp(self):
        self.box = TempVault()

    def tearDown(self):
        self.box.close()

    def weekly(self, *args):
        return self.box.run(["python3", "scripts/weekly.py", *args])

    def brief(self, as_of):
        return (self.box.briefs / f"weekly-{as_of}.md").read_text()

    def test_default_window_groups_the_scan_break_and_leaves_the_vault_alone(self):
        """Seven days through 19 Nov include the 15 Nov scan break and not the 2 Nov supplier slip.

        Critical decisions come first. The brief is written under DECISION_BRIEFS.
        The notes are unchanged. A second run writes the same file.
        """
        before = sorted(path.name for path in self.box.vault.glob("Signal/*.md"))
        stdout = self.weekly("--as-of", "2026-11-19")
        text = self.brief("2026-11-19")
        self.assertEqual(sorted(path.name for path in self.box.vault.glob("Signal/*.md")), before)
        self.assertIn(f"Vault: {self.box.vault}", stdout)
        self.assertIn("Brief:", stdout)
        self.assertIn(str(self.box.briefs / "weekly-2026-11-19.md"), stdout)
        self.assertFalse(list((ROOT / "briefs").glob("weekly-*.md")))
        self.assertEqual(self.weekly("--as-of", "2026-11-19"), stdout)

        self.assertIn("# Weekly briefing, 12 Nov 2026 to 19 Nov 2026", text)
        self.assertIn(
            '1 signal breaks an assumption: "Delivery scans cover at least 95% of trips." '
            "4 live decisions are at risk, 3 of them critically. "
            "Tell 5 people, Olu Adeyemi first. "
            "11 assumptions have no signal in the last 90 days.",
            text,
        )
        self.assertIn(
            '- **15 Nov 2026** — Scan coverage was 88% of trips in October (Ops data check) '
            '**breaks** "Delivery scans cover at least 95% of trips."',
            text,
        )
        risk = section(text, "Live decisions at risk")
        self.assertLess(
            risk.index("**critical**, medium — Build the ops dashboard on scan data"),
            risk.index("**critical**, low — Build the route optimizer in house"),
        )
        self.assertLess(
            risk.index("**critical**, low — The optimizer trains on scan data only"),
            risk.index("supporting, low — Run the weekly ops review from the dashboard"),
        )
        tell = section(text, "Who to tell")
        self.assertIn(
            "**Olu Adeyemi** (Head of Operations, 3 critical): "
            "Build the ops dashboard on scan data; Build the route optimizer in house; "
            "The optimizer trains on scan data only; Run the weekly ops review from the dashboard",
            tell,
        )
        self.assertIn("**Ken Ito** (CTO, 2 critical)", tell)
        self.assertLess(tell.index("Olu Adeyemi"), tell.index("Diego Morales"))
        self.assertNotIn(SUPPLIER, text)
        self.assertNotIn(CHURN, text)
        self.assertNotIn(BUY, text)
        review = section(text, "Worth a review")
        for statement in QUIET:
            self.assertIn(statement, review)
        self.assertNotIn("Delivery scans cover at least 95% of trips", review)
        self.assertNotIn("Monthly driver churn stays under 8%", review)
        self.assertNotIn("The supplier delivers 60 e-cargo bikes", review)

    def test_since_moves_the_window_and_a_future_signal_stays_out(self):
        """--since is the first day. A signal dated after --as-of is not a touch and not in the window."""
        self.box.add_signal(
            "q1-budget-holds", "BREAKS", "Budget cut dated next week",
            source="Finance note", date="2026-11-25",
        )
        self.weekly("--since", "2026-11-16", "--as-of", "2026-11-19")
        narrow_text = self.brief("2026-11-19")
        self.assertIn("# Weekly briefing, 16 Nov 2026 to 19 Nov 2026", narrow_text)
        self.assertIn("Nothing broke or weakened in this window.", section(narrow_text, "Broke or weakened"))
        self.assertNotIn(SCAN, narrow_text)
        self.assertNotIn("Budget cut dated next week", narrow_text)
        review = section(narrow_text, "Worth a review")
        self.assertIn("The Q1 budget stays at plan, EUR 2.4m.", review)

        wide = self.weekly("--since", "2026-11-01", "--as-of", "2026-11-19")
        wide_text = self.brief("2026-11-19")
        broke = section(wide_text, "Broke or weakened")
        self.assertLess(broke.index(SCAN), broke.index(SUPPLIER))
        self.assertIn("**breaks**", broke)
        self.assertIn("**weakens**", broke)
        self.assertNotIn(CHURN, wide_text)
        self.assertNotIn("Budget cut dated next week", wide)
        self.assertIn(str(self.box.vault), wide)

        day = self.weekly("--since", "2026-11-15", "--as-of", "2026-11-15")
        self.assertIn("# Weekly briefing, 15 Nov 2026\n", self.brief("2026-11-15"))
        self.assertNotIn(" to ", self.brief("2026-11-15").splitlines()[0])
        self.assertIn(SCAN, day)

    def test_bad_dates_write_nothing(self):
        for args in (
            ["--as-of", "19-11-2026"],
            ["--since", "2026-11-20", "--as-of", "2026-11-19"],
            ["--review-after", "-1"],
            ["--as-of", "2026-02-31"],
        ):
            result = subprocess.run(
                ["python3", "scripts/weekly.py", *args],
                cwd=ROOT, env=self.box.env, text=True, capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0, args)
            self.assertEqual(list(self.box.briefs.glob("weekly-*.md")), [], args)

    def test_high_confidence_break_is_listed_and_fragile_ground_counts_it(self):
        """A break under high-confidence decisions shows up here and on 2-fragile.

        Launch Lyon before Paris is high confidence and rests on the permit, so lyon-launch is fragile ground.
        """
        self.box.add_signal(
            "lyon-permit-by-jan", "BREAKS", "The Lyon permit missed January",
            source="Permit office", date="2026-12-16",
        )
        self.weekly("--as-of", "2026-12-16")
        text = self.brief("2026-12-16")
        risk = section(text, "Live decisions at risk")
        self.assertIn("**critical**, high — Launch Lyon before Paris (Launch in Lyon)", risk)
        self.assertIn("**critical**, medium — Put the Lyon depot in Guillotiere (Launch in Lyon)", risk)
        self.assertIn("supporting, high — Paris waits for 3 months of Lyon data (Launch in Lyon)", risk)
        self.assertLess(risk.index(LAUNCH), risk.index(PARIS))
        self.assertLess(risk.index("**critical**, high — " + LAUNCH), risk.index("supporting, medium — Hire the Lyon city lead"))
        projects = {row["project"]: row for row in self.box.query("2-fragile")}
        self.assertIn("lyon-launch", projects)
        self.assertEqual(projects["lyon-launch"]["high_confidence_broken"], 2)
        self.assertIn(LAUNCH, risk)

    def test_support_sits_next_to_an_older_break_and_exposed_labels_it(self):
        """A support in the window names the earlier break and the critical decisions.

        6-exposed shows that support beside the break and labels it support, not risk.
        """
        self.box.add_signal(
            "ops-data-complete", "SUPPORTS", "A recount found the missing scans",
            source="Ops data check", date="2026-12-18",
        )
        self.weekly("--since", "2026-12-12", "--as-of", "2026-12-18")
        text = self.brief("2026-12-18")
        self.assertIn("Nothing broke or weakened in this window.", section(text, "Broke or weakened"))
        self.assertIn(
            "No live decision rests on what broke or weakened in this window.",
            section(text, "Live decisions at risk"),
        )
        good = section(text, "Confirmed or supported")
        self.assertIn("A recount found the missing scans", good)
        self.assertIn("**supports**", good)
        self.assertIn("Mixed:", good)
        self.assertIn(SCAN, good)
        self.assertIn("breaks it", good)
        self.assertIn("Build the ops dashboard on scan data", good)
        self.assertIn("Build the route optimizer in house", good)
        self.assertIn("The optimizer trains on scan data only", good)
        self.assertIn("1 supporting", good)
        exposed = [row for row in self.box.query("6-exposed") if row["assumption"] == "ops-data-complete"]
        effects = {row["effect"] for row in exposed}
        self.assertIn("BREAKS", effects)
        self.assertIn("SUPPORTS", effects)
        self.assertTrue(all(row["label"] == "support" for row in exposed if row["effect"] == "SUPPORTS"))
        self.assertTrue(all(row["label"] == "risk" for row in exposed if row["effect"] == "BREAKS"))
        self.assertIn(
            "1 signal supports an assumption that has also been broken or weakened.",
            text,
        )

    def test_support_in_the_same_window_is_mixed_evidence_on_the_break(self):
        self.box.add_signal(
            "ops-data-complete", "SUPPORTS", "A recount found the missing scans",
            source="Ops data check", date="2026-11-18",
        )
        self.weekly("--since", "2026-11-12", "--as-of", "2026-11-19")
        text = self.brief("2026-11-19")
        risk = section(text, "Live decisions at risk")
        self.assertIn("Also this week:", risk)
        self.assertIn("A recount found the missing scans", risk)
        self.assertIn("supports it", risk)
        good = section(text, "Confirmed or supported")
        self.assertIn("Mixed:", good)
        self.assertIn("this week", good)
        self.assertIn("See Live decisions at risk.", good)
        self.assertIn(SCAN, section(text, "Broke or weakened"))
        exposed = self.box.query("6-exposed")
        effects = {row["effect"] for row in exposed}
        self.assertIn("SUPPORTS", effects)
        self.assertTrue(all(
            row["label"] == "support" for row in exposed if row["effect"] == "SUPPORTS"
        ))

    def test_an_earlier_confirm_sits_next_to_a_new_weaken(self):
        self.box.add_signal(
            "driver-churn-under-8", "WEAKENS", "December churn hit 9%",
            source="People report", date="2026-12-11",
        )
        self.weekly("--as-of", "2026-12-12")
        text = self.brief("2026-12-12")
        risk = section(text, "Live decisions at risk")
        self.assertIn("Earlier:", risk)
        self.assertIn(CHURN, risk)
        self.assertIn("confirms it", risk)
        self.assertIn("**critical**, low — Promise 98% on-time delivery in the SLA", risk)
        self.assertLess(
            risk.index("**critical**, low — Promise 98% on-time delivery in the SLA"),
            risk.index("supporting, high — Pay a 3-month retention bonus to drivers"),
        )
        self.assertIn("**weakens**", section(text, "Broke or weakened"))

    def test_a_confirm_is_good_news_and_puts_nobody_at_risk(self):
        self.box.add_signal(
            "driver-churn-under-8", "CONFIRMS", "November driver churn was 7.4%",
            source="People report", date="2026-12-11",
        )
        self.weekly("--as-of", "2026-12-12")
        text = self.brief("2026-12-12")
        self.assertIn("Nothing broke or weakened in this window.", section(text, "Broke or weakened"))
        self.assertIn(
            "No live decision rests on what broke or weakened in this window.",
            section(text, "Live decisions at risk"),
        )
        self.assertIn("Nobody to tell.", section(text, "Who to tell"))
        good = section(text, "Confirmed or supported")
        self.assertIn("**confirms**", good)
        self.assertIn("November driver churn was 7.4%", good)
        self.assertIn("Monthly driver churn stays under 8%.", good)
        self.assertNotIn("Mixed:", good)
        self.assertNotIn("Pay a 3-month retention bonus to drivers", text)
        self.assertIn("1 signal confirms an assumption.", text)

    def test_tell_counts_a_doubly_critical_decision_once(self):
        """The same decision, critical under two assumptions hit this week, counts once per person.

        It is still listed under each assumption. The signal brief counts it once too.
        """
        self.box.add_decision(
            HOLD,
            date="2026-12-21", project="fleet-ebike-upgrade", by="priya-raman",
            rests=("q1-budget-holds:critical", "eu-cargo-bike-subsidy:critical"),
            rationale="One decision, two critical assumptions.",
        )
        self.box.add_signal(
            "q1-budget-holds", "BREAKS", "Both budget and subsidy fail together",
            source="Test memo", date="2026-12-22",
            also=[("eu-cargo-bike-subsidy", "BREAKS")],
        )
        self.weekly("--as-of", "2026-12-22")
        text = self.brief("2026-12-22")
        self.assertIn("1 signal breaks 2 assumptions.", text)
        risk = section(text, "Live decisions at risk")
        self.assertEqual(risk.count(HOLD), 2)
        self.assertLess(
            risk.index("**critical**, medium — " + HOLD),
            risk.index("supporting, medium — Lease half the e-cargo bikes, buy half"),
        )
        tell = section(text, "Who to tell")
        priya = next(line for line in tell.splitlines() if line.startswith("- **Priya Raman**"))
        self.assertIn("(Head of Finance, 5 critical)", priya)
        self.assertEqual(priya.count(HOLD), 1)
        self.assertIn("**Tomasz Wilk** (COO, 3 critical)", tell)
        self.assertIn("**Diego Morales** (Fleet Lead, 2 critical)", tell)
        self.assertNotIn("Ken Ito", tell)
        self.assertNotIn("Lea Novak", tell)
        self.assertNotIn(BUY, text)
        self.assertIn(
            f"{HOLD} is critical under more than one assumption and is counted once.",
            tell,
        )

    def test_review_after_keeps_a_recent_signal_and_surfaces_an_older_one(self):
        self.weekly("--as-of", "2026-12-12", "--review-after", "90")
        wide = section(self.brief("2026-12-12"), "Worth a review")
        self.assertIn("The Series A closes by end of March.", wide)
        self.assertNotIn("Monthly driver churn stays under 8%", wide)
        self.assertNotIn("The supplier delivers 60 e-cargo bikes", wide)
        self.assertIn("11 assumptions have no signal in the last 90 days.", wide)

        self.weekly("--as-of", "2026-12-12", "--review-after", "30")
        narrow = section(self.brief("2026-12-12"), "Worth a review")
        self.assertIn(
            'Monthly driver churn stays under 8%. Last signal 20 Oct 2026 confirmed it: '
            '"October driver churn was 6.9%".',
            narrow,
        )
        self.assertIn(
            'The supplier delivers 60 e-cargo bikes by end of February. '
            'Last signal 2 Nov 2026 weakened it: "Supplier flags a 3-week slip on e-cargo bikes".',
            narrow,
        )
        self.assertNotIn("Delivery scans cover at least 95% of trips", narrow)
        self.assertIn("13 assumptions have no signal in the last 30 days.", narrow)
        self.assertLess(
            narrow.index("The Series A closes by end of March."),
            narrow.index("Monthly driver churn stays under 8%."),
        )


if __name__ == "__main__":
    unittest.main()
