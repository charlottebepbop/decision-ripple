"""The vault check catches messy notes and does not drop a link it saw."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_vault import check_vault, render

MESSY = ROOT / "tests" / "fixtures" / "messy-vault"


def link_opens(root):
    total = 0
    for path in root.rglob("*.md"):
        parts = path.relative_to(root).parts
        if any(part.startswith(".") for part in parts):
            continue
        total += path.read_text(encoding="utf-8").count("[[")
    return total


def blob(report):
    return "\n".join(f"{issue.path}\n{issue.message}\n{issue.fix}" for issue in report.issues)


class CheckVaultTests(unittest.TestCase):
    def test_committed_vault_is_consistent_and_every_link_is_counted(self):
        report = check_vault(ROOT / "vault")
        self.assertTrue(report.ok, render(report, ROOT / "vault"))
        self.assertEqual(report.notes, 59)
        self.assertEqual(report.links_seen, link_opens(ROOT / "vault"))

    def test_messy_fixture_exits_nonzero_and_names_each_problem(self):
        report = check_vault(MESSY)
        self.assertFalse(report.ok)
        text = blob(report)
        expect = [
            ("Decision/paint-the-door.md", "rests on no assumption"),
            ("Decision/paint-the-door.md", "sky-high"),
            ("Decision/paint-the-door.md", "missing status"),
            ("Decision/paint-the-door.md", "disappears from all three"),
            ("Assumption/also-ground.md", "does not match its filename"),
            ("Assumption/also-ground.md", "Every query fails"),
            ("Assumption/q1-budget-hold.md", "only has type and name"),
            ("Decision/typo-budget.md", "[[Assumption/q1-budget-hold]]"),
            ("Decision/typo-budget.md", "q1-budget-holds"),
            ("Assumption/orphan-weather.md", "has no owner"),
            ("Assumption/also-ground.md", "name: ground"),
            ("Assumption/also-ground.md", "also uses the name"),
            ("Person/ada-okafor-copy.md", "same person"),
            ("Person/no-role.md", "missing role"),
            ("Signal/bad-date.md", "yesterday"),
            ("Signal/quiet-week.md", "does not confirm, support, weaken, or break"),
            ("Project/mislabeled.md", "type: Decision"),
            ("Decision/still-live.md", "supersedes this decision"),
            ("Decision/marked-old.md", "no decision links to it with SUPERSEDES"),
            ("Decision/bad-links.md", "Assumption/grond"),
            ("Decision/bad-links.md", "renamed"),
            ("Decision/bad-links.md", "zzzz-not-a-note"),
            ("Decision/bad-links.md", "similar name"),
            ("Decision/bad-links.md", "person/ada-okafor"),
            ("Decision/bad-links.md", "Relate drops it"),
            ("Decision/bad-links.md", "ada-okafor#role"),
            ("Decision/bad-links.md", "not in quotes"),
            ("Decision/bad-links.md", "not a wikilink"),
            ("Decision/bad-links.md", "weight is 'high'"),
            ("Decision/bad-links.md", "RESTS_ON links to Project/dock"),
            ("Decision/bad-links.md", "never closes"),
            ("index.md", "keep-the-dor"),
            ("index.md", "keep-the-door"),
        ]
        for path, snippet in expect:
            self.assertIn(path, text, snippet)
            self.assertIn(snippet, text, path)
        kept = [issue for issue in report.issues if issue.path == "Decision/keep-the-door.md"]
        self.assertEqual(kept, [], "a map link, an alias and a body link were flagged")

    def test_every_link_marker_is_counted_including_broken_ones(self):
        report = check_vault(MESSY)
        self.assertEqual(report.links_seen, link_opens(MESSY))
        self.assertGreater(report.links_seen, 0)
        # The lowercase folder is a link Relate drops. It must be in the report, not ignored.
        text = blob(report)
        self.assertIn("[[person/ada-okafor]]", text)

    def test_dangling_wikilink_names_the_empty_note_relate_would_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "Assumption/q1-budget-holds.md": """---
type: Assumption
name: q1-budget-holds
statement: The Q1 budget stays at plan.
---

# The Q1 budget stays at plan.
""",
                "Person/ada-okafor.md": """---
type: Person
name: ada-okafor
role: Depot clerk
---

# Ada Okafor
""",
                "Project/dock.md": """---
type: Project
name: dock
title: North dock
OWNED_BY:
  - "[[Person/ada-okafor]]"
---

# North dock
""",
                "Decision/spend.md": """---
type: Decision
name: spend
title: Spend the budget
date: 2026-04-04
confidence: medium
status: live
RESTS_ON:
  - "[[Assumption/q1-budget-hold]]"
DECIDED_BY:
  - "[[Person/ada-okafor]]"
STEERS:
  - "[[Project/dock]]"
---

# Spend the budget
""",
            }
            for rel, text in files.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            report = check_vault(root)
            text = blob(report)
            self.assertIn("[[Assumption/q1-budget-hold]]", text)
            self.assertIn("empty note", text)
            self.assertIn("[[Assumption/q1-budget-holds]]", text)
            self.assertFalse((root / "Assumption" / "q1-budget-hold.md").exists())

    def test_a_tidy_vault_passes_map_alias_and_body_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "Person/ada-okafor.md": """---
type: Person
name: ada-okafor
role: Depot clerk
---

# Ada Okafor
""",
                "Assumption/ground.md": """---
type: Assumption
name: ground
statement: The dock floor holds the bikes.
---

# The dock floor holds the bikes.
""",
                "Project/dock.md": """---
type: Project
name: dock
title: North dock
OWNED_BY:
  - "[[Person/ada-okafor]]"
---

# North dock
""",
                "Decision/keep-the-door.md": """---
type: Decision
name: keep-the-door
title: Keep the depot door blue
date: 2026-04-02
confidence: high
status: live
RESTS_ON:
  - "[[Assumption/ground]]"
  - target: "[[Assumption/ground]]"
    weight: critical
DECIDED_BY:
  - "[[Person/ada-okafor|Ada Okafor]]"
STEERS:
  - "[[Project/dock]]"
---

# Keep the depot door blue

See [[Project/dock]] and [[Person/ada-okafor|Ada]].
""",
                "Signal/floor-note.md": """---
type: Signal
name: floor-note
title: The dock floor was checked
source: Floor note
date: 2026-04-02
CONFIRMS:
  - "[[Assumption/ground]]"
---

# The dock floor was checked
""",
            }
            for rel, text in files.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            report = check_vault(root)
            self.assertTrue(report.ok, render(report, root))
            self.assertEqual(report.links_seen, link_opens(root))
            self.assertEqual(report.notes, 5)

    def test_cli_exit_codes(self):
        messy = subprocess.run(
            [sys.executable, "scripts/check_vault.py", str(MESSY)],
            cwd=ROOT, text=True, capture_output=True,
        )
        self.assertEqual(messy.returncode, 1)
        self.assertIn("The vault check failed", messy.stdout)
        self.assertIn("Fix:", messy.stdout)

        clean = subprocess.run(
            [sys.executable, "scripts/check_vault.py"],
            cwd=ROOT, text=True, capture_output=True,
        )
        self.assertEqual(clean.returncode, 0, clean.stdout)
        self.assertIn("looks consistent", clean.stdout)

        missing = subprocess.run(
            [sys.executable, "scripts/check_vault.py", str(ROOT / "no-such-vault")],
            cwd=ROOT, text=True, capture_output=True,
        )
        self.assertEqual(missing.returncode, 1)
        self.assertIn("not a folder", missing.stdout)


if __name__ == "__main__":
    unittest.main()
