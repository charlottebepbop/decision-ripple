"""Run Cypher against vault/ through the Relate CLI."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERIES = ROOT / "queries"


def vault_path():
    # Read on each call. A test points DECISION_VAULT at a throwaway copy after import.
    raw = os.environ.get("DECISION_VAULT")
    return Path(raw) if raw else ROOT / "vault"


class _Vault:
    def __fspath__(self):
        return str(vault_path())

    def __str__(self):
        return str(vault_path())

    def __truediv__(self, other):
        return vault_path() / other


VAULT = _Vault()


def cypher(statement, **params):
    # The Python client has no markdown snapshot option yet, so all access goes through the CLI.
    # --markdown-body-properties maps the note body to `text`, so a write can set it.
    cmd = ["relate", "query", "--snapshot-format", "markdown", "--markdown-body-properties", "text",
           "--database", str(VAULT), "--json", "--max-rows", "0"]
    for key, value in params.items():
        # --param parses JSON first, so "2026-12-01" would fail as a number. Quote it.
        cmd += ["--param", f"{key}={json.dumps(value)}"]
    out = subprocess.run(cmd, input=statement, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"relate failed ({out.returncode}): {out.stdout or out.stderr}")
    return json.loads(out.stdout)["data"]


def query(name, **params):
    return cypher((QUERIES / f"{name}.cypher").read_text(), **params)


def names(label):
    return [r["name"] for r in cypher(f"MATCH (n:{label}) RETURN n.name AS name ORDER BY name")]


def require(label, name):
    if name not in names(label):
        sys.exit(f"No {label} '{name}'. Known: {', '.join(names(label))}")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]
