"""Run Cypher against vault/ through the Relate CLI."""

import difflib
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


def cypher(query_text, **params):
    # The Python client has no markdown snapshot option yet, so all access goes through the CLI.
    # --markdown-body-properties maps the note body to `text`, so a write can set it.
    # The first argument is not named `statement`: callers pass a Cypher parameter of that name.
    cmd = ["relate", "query", "--snapshot-format", "markdown", "--markdown-body-properties", "text",
           "--database", str(VAULT), "--json", "--max-rows", "0"]
    for key, value in params.items():
        # --param parses JSON first, so "2026-12-01" would fail as a number. Quote it.
        cmd += ["--param", f"{key}={json.dumps(value)}"]
    out = subprocess.run(cmd, input=query_text, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"relate failed ({out.returncode}): {out.stdout or out.stderr}")
    return json.loads(out.stdout)["data"]


def query(name, **params):
    return cypher((QUERIES / f"{name}.cypher").read_text(), **params)


def names(label):
    return [r["name"] for r in cypher(f"MATCH (n:{label}) RETURN n.name AS name ORDER BY name")]


def missing(label, name, known=None):
    """Empty string when `name` is a real note. Otherwise the message to exit with.

    A close slug is named so a typo is not treated as a note that still has to be created.
    """
    if known is None:
        known = names(label)
    if name in known:
        return ""
    close = difflib.get_close_matches(name, list(known), n=1, cutoff=0.8)
    hint = f" Did you mean {close[0]}?" if close else ""
    return f"No {label} '{name}'.{hint} Known: {', '.join(known)}"


def require(label, name):
    message = missing(label, name)
    if message:
        sys.exit(message)


def person(who):
    """Return the slug for a person given by slug or by full name."""
    rows = cypher("MATCH (p:Person) WHERE p.name = $w OR p.title = $w RETURN p.name AS name", w=who)
    if not rows:
        known = [f"{r['t']} ({r['n']})" for r in cypher("MATCH (p:Person) RETURN p.title AS t, p.name AS n ORDER BY n")]
        sys.exit(f"No Person '{who}'. Known: {', '.join(known)}")
    return rows[0]["name"]


def slug(text):
    # Cut at 60 characters, then drop a hyphen the cut left on the end.
    cut = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]
    return cut.strip("-")
