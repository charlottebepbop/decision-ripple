"""Run Cypher against vault/ through the Relate CLI."""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "vault"
QUERIES = ROOT / "queries"


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


def person(who):
    """Return the slug for a person given by slug or by full name."""
    rows = cypher("MATCH (p:Person) WHERE p.name = $w OR p.title = $w RETURN p.name AS name", w=who)
    if not rows:
        known = [f"{r['t']} ({r['n']})" for r in cypher("MATCH (p:Person) RETURN p.title AS t, p.name AS n ORDER BY n")]
        sys.exit(f"No Person '{who}'. Known: {', '.join(known)}")
    return rows[0]["name"]


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]
