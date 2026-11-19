"""List the slugs queries and the record scripts expect.

    python3 scripts/list_slugs.py
    python3 scripts/list_slugs.py assumption
    python3 scripts/list_slugs.py decision project

A slug is the filename without .md. It matches the note's name field.
add_signal.py, add_decision.py, and the query parameters want that slug, not the title.
DECISION_VAULT selects the folder. Unset, this lists vault/ in this repo.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = ("Assumption", "Project", "Decision", "Person", "Signal")
SKIP = {"index.md", "log.md"}
BLURB = ("title", "statement", "role")


def vault_dir():
    raw = os.environ.get("DECISION_VAULT")
    return Path(raw) if raw else ROOT / "vault"


def blurb(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    for line in text[3:end].splitlines():
        if not line or line[0] == " " or ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip() in BLURB:
            return value.strip().strip('"').strip("'")
    return ""


def notes(root, label):
    folder = root / label
    if not folder.is_dir():
        return []
    found = []
    for path in sorted(folder.glob("*.md")):
        if path.name in SKIP:
            continue
        found.append((path.stem, blurb(path)))
    return found


def main():
    root = vault_dir()
    if not root.is_dir():
        sys.exit(
            f"{root} is not a folder. Set DECISION_VAULT to your notes, "
            "or run: python3 scripts/init_vault.py /path/to/your-vault"
        )
    asked = sys.argv[1:]
    labels = []
    known = {label.lower(): label for label in LABELS}
    for name in asked:
        label = known.get(name.lower())
        if label is None:
            sys.exit(f"No note type {name!r}. Choose from: {', '.join(LABELS)}")
        if label not in labels:
            labels.append(label)
    if not labels:
        labels = list(LABELS)

    for index, label in enumerate(labels):
        if index:
            print()
        print(label)
        rows = notes(root, label)
        if not rows:
            print("  (none yet)")
            continue
        for slug, text in rows:
            print(f"  {slug}")
            if text:
                print(f"      {text}")


if __name__ == "__main__":
    main()
