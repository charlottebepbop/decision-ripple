"""Personal-vault helpers that do not need the Relate CLI.

serve.sh must follow DECISION_VAULT and, with the variable unset, still serve
the sample vault/. list_slugs.py and init_vault.py read and create folders.
"""

import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from graph import slug


class SlugTests(unittest.TestCase):
    def test_short_title_is_unchanged(self):
        self.assertEqual(slug("Finance cuts the Q1 budget by 20%"), "finance-cuts-the-q1-budget-by-20")

    def test_cut_at_60_drops_a_trailing_hyphen(self):
        got = slug(" ".join(["abcd"] * 20))
        self.assertLessEqual(len(got), 60)
        self.assertFalse(got.endswith("-"))
        self.assertTrue(got.startswith("abcd-abcd"))
        self.assertNotIn("--", got)


class ServeScriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.log = self.root / "relate-args.log"
        self.stdin_log = self.root / "relate-stdin.log"
        bindir = self.root / "bin"
        bindir.mkdir()
        fake = bindir / "relate"
        fake.write_text(textwrap.dedent(f"""\
            #!/bin/sh
            printf '%s\\n' "$@" >> {sh_quote(self.log)}
            echo ---- >> {sh_quote(self.log)}
            if [ "$1" = query ]; then
              cat >> {sh_quote(self.stdin_log)}
            fi
            exit 0
            """))
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
        self.env = os.environ.copy()
        self.env["PATH"] = f"{bindir}{os.pathsep}{self.env.get('PATH', '')}"
        self.env.pop("DECISION_VAULT", None)

    def tearDown(self):
        self.tmp.cleanup()

    def databases(self):
        lines = self.log.read_text().splitlines()
        found = []
        for index, line in enumerate(lines):
            if line == "--database" and index + 1 < len(lines):
                found.append(lines[index + 1])
        return found

    def run_serve(self):
        return subprocess.run(
            ["sh", str(ROOT / "scripts" / "serve.sh")],
            cwd="/tmp",
            env=self.env,
            text=True,
            capture_output=True,
        )

    def test_decision_vault_is_the_database_for_setup_and_serve(self):
        vault = self.root / "my vault"
        vault.mkdir()
        self.env["DECISION_VAULT"] = str(vault)
        result = self.run_serve()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.databases(), [str(vault), str(vault)])
        self.assertIn("CREATE FULLTEXT INDEX decision_text", self.stdin_log.read_text())
        self.assertNotIn(str(ROOT / "vault"), "\n".join(self.databases()))

    def test_unset_decision_vault_serves_the_sample(self):
        result = self.run_serve()
        self.assertEqual(result.returncode, 0, result.stderr)
        sample = str(ROOT / "vault")
        self.assertEqual(self.databases(), [sample, sample])


class ListSlugsTests(unittest.TestCase):
    def run_list(self, *args, vault=None):
        env = os.environ.copy()
        if vault is None:
            env.pop("DECISION_VAULT", None)
        else:
            env["DECISION_VAULT"] = str(vault)
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "list_slugs.py"), *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        return result

    def test_lists_slug_and_statement_not_the_filename_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "Assumption"
            folder.mkdir()
            (folder / "ops-data-complete.md").write_text(
                '---\ntype: Assumption\nname: ops-data-complete\n'
                'statement: "Scans cover the trips."\n---\n\n# Scans\n',
                encoding="utf-8",
            )
            (folder / "index.md").write_text("# index\n", encoding="utf-8")
            result = self.run_list("assumption", vault=root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ops-data-complete", result.stdout)
        self.assertIn("Scans cover the trips.", result.stdout)
        self.assertNotIn("index", result.stdout)
        self.assertNotIn(".md", result.stdout)

    def test_sample_vault_includes_a_known_assumption_slug(self):
        result = self.run_list("assumption")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ops-data-complete", result.stdout)
        self.assertIn("q1-budget-holds", result.stdout)

    def test_unknown_type_fails(self):
        result = self.run_list("customer")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Assumption", result.stderr)


class InitVaultTests(unittest.TestCase):
    def test_creates_folders_and_hides_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "my decisions"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "init_vault.py"), str(dest)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for label in ("Decision", "Assumption", "Person", "Project", "Signal"):
                self.assertTrue((dest / label).is_dir(), label)
            copied = dest / ".obsidian" / "templates" / "Decision.md"
            self.assertTrue(copied.is_file())
            self.assertIn("status: live", copied.read_text(encoding="utf-8"))
            self.assertIn(f"DECISION_VAULT={sh_quote(str(dest.resolve()))}", result.stdout)
            self.assertIn("DECISION_BRIEFS=", result.stdout)

    def test_refuses_the_sample_vault_and_a_nonempty_folder(self):
        sample = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "init_vault.py"), str(ROOT / "vault")],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(sample.returncode, 1)
        self.assertIn("sample vault", sample.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            (dest / "notes.txt").write_text("keep\n", encoding="utf-8")
            refused = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "init_vault.py"), str(dest)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(refused.returncode, 1)
            self.assertTrue((dest / "notes.txt").is_file())
            self.assertFalse((dest / "Decision").exists())


class CheckVaultEnvTests(unittest.TestCase):
    def test_env_selects_the_folder_and_an_argument_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty"
            empty.mkdir()
            env = os.environ.copy()
            env["DECISION_VAULT"] = str(empty)
            chosen = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "check_vault.py")],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(chosen.returncode, 0, chosen.stderr)
            self.assertIn(str(empty), chosen.stdout)
            messy = ROOT / "tests" / "fixtures" / "messy-vault"
            override = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "check_vault.py"), str(messy)],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(override.returncode, 1)
            self.assertIn("Decision/paint-the-door.md", override.stdout)
            self.assertNotIn(str(empty), override.stdout)
            self.assertNotIn("looks consistent", override.stdout)


def sh_quote(path):
    return "'" + str(path).replace("'", "'\\''") + "'"


if __name__ == "__main__":
    unittest.main()
