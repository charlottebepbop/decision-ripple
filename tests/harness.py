"""Throwaway copy of vault/ for scenario tests.

DECISION_VAULT points at the copy, so the committed notes stay as they are.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _ignore(directory, names):
    skip = []
    for name in names:
        if name in {".cypherlite", ".obsidian", "__pycache__"} or name.startswith(".cypherlite"):
            skip.append(name)
    return skip


class TempVault:
    def __init__(self):
        import tempfile

        self._prev_vault = os.environ.get("DECISION_VAULT")
        self._prev_briefs = os.environ.get("DECISION_BRIEFS")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.vault = self.root / "vault"
        self.briefs = self.root / "briefs"
        shutil.copytree(ROOT / "vault", self.vault, ignore=_ignore)
        self.briefs.mkdir()
        os.environ["DECISION_VAULT"] = str(self.vault)
        os.environ["DECISION_BRIEFS"] = str(self.briefs)
        self.env = os.environ.copy()
        setup = subprocess.run(
            [
                "relate", "query", "--snapshot-format", "markdown",
                "--markdown-body-properties", "text", "--database", str(self.vault),
                "--max-rows", "0",
            ],
            input=(ROOT / "queries" / "0-setup.cypher").read_text(),
            text=True, capture_output=True,
        )
        if setup.returncode != 0:
            raise RuntimeError(setup.stdout + setup.stderr)

    def close(self):
        if self._prev_vault is None:
            os.environ.pop("DECISION_VAULT", None)
        else:
            os.environ["DECISION_VAULT"] = self._prev_vault
        if self._prev_briefs is None:
            os.environ.pop("DECISION_BRIEFS", None)
        else:
            os.environ["DECISION_BRIEFS"] = self._prev_briefs
        self.tmp.cleanup()

    def run(self, cmd):
        result = subprocess.run(cmd, cwd=ROOT, env=self.env, text=True, capture_output=True)
        if result.returncode != 0:
            raise AssertionError(f"{' '.join(cmd)}\n{result.stdout}\n{result.stderr}")
        return result.stdout

    def add_signal(self, assumption, effect, title, source, date, also=()):
        cmd = [
            "python3", "scripts/add_signal.py", assumption, effect, title,
            "--source", source, "--date", date,
        ]
        for extra_assumption, extra_effect in also:
            cmd += ["--and", extra_assumption, extra_effect]
        return self.run(cmd)

    def add_decision(self, title, *, date, project, by, rationale, rests=(), supersedes=None, amends=None):
        cmd = ["python3", "scripts/add_decision.py", title, "--rationale", rationale, "--date", date]
        projects = project if isinstance(project, (list, tuple)) else [project]
        people = by if isinstance(by, (list, tuple)) else [by]
        for name in projects:
            cmd += ["--project", name]
        for person in people:
            cmd += ["--by", person]
        for item in rests:
            cmd += ["--rests-on", item]
        if supersedes:
            cmd += ["--supersedes", supersedes]
        if amends:
            cmd += ["--amends", amends]
        return self.run(cmd)

    def query(self, name, **params):
        os.environ["DECISION_VAULT"] = str(self.vault)
        from graph import query
        return query(name, **params)

    def brief(self, filename):
        return (self.briefs / filename).read_text()


def ripple_view(rows):
    return [
        (row["decision"], row["weight"], row["confidence"], tuple(sorted(row["projects"])))
        for row in rows
    ]


def tell_view(rows):
    return [
        (row["person"], row["critical"], row["role"], tuple(sorted(row["decisions"])))
        for row in rows
    ]


def exposed_view(rows):
    return [
        (
            row["signal"], row["effect"], row["assumption"], row["decision"],
            row["weight"], tuple(sorted(row["projects"])),
        )
        for row in rows
    ]


def where(rows, **equals):
    picked = []
    for row in rows:
        if all(row[key] == value for key, value in equals.items()):
            picked.append(row)
    return picked
