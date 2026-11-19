"""Create an empty decision vault outside this repo.

    python3 scripts/init_vault.py ~/notes/my-decisions

Creates the five note folders and copies the Obsidian templates into
.obsidian/templates. Relate ignores a folder whose name starts with a dot,
so those templates do not become notes. Prints DECISION_VAULT and
DECISION_BRIEFS. Refuses to touch the sample vault/ in this repo.
"""

import argparse
import shlex
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "vault"
LABELS = ("Decision", "Assumption", "Person", "Project", "Signal")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", help="new notes folder, outside this repo")
    parser.add_argument("--force", action="store_true", help="write into a folder that already has files")
    args = parser.parse_args()

    dest = Path(args.path).expanduser()
    if dest.exists() and not dest.is_dir():
        sys.exit(f"{dest} is a file. Pass a folder.")
    try:
        same = dest.resolve() == SAMPLE.resolve()
    except OSError:
        same = False
    if same or (dest.exists() and dest.resolve() == SAMPLE.resolve()):
        sys.exit(
            f"{dest} is the sample vault in this repo. "
            "Pick another folder so your notes stay out of git."
        )
    if dest.exists() and any(dest.iterdir()) and not args.force:
        sys.exit(
            f"{dest} already has files. Pass a new folder, or --force to add the note folders there."
        )

    for label in LABELS:
        (dest / label).mkdir(parents=True, exist_ok=True)
    templates = ROOT / "templates"
    target = dest / ".obsidian" / "templates"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(templates, target, dirs_exist_ok=True)

    vault = dest.resolve()
    briefs = vault.parent / f"{vault.name}-briefs"
    print(f"Created {vault}")
    print("The five note folders are ready. Templates are in .obsidian/templates.")
    print("In the shell where you run the scripts, and before you start Claude Code:")
    print()
    print(f"export DECISION_VAULT={shlex.quote(str(vault))}")
    print(f"export DECISION_BRIEFS={shlex.quote(str(briefs))}")
    print()
    print("Open that folder in Obsidian. Turn on the Templates core plugin and set")
    print("the template folder to .obsidian/templates.")
    print("Add a person, a project, and an assumption before the decision that rests on it.")
    print("One RESTS_ON link in the vault has to be a bare wikilink, or Relate will not")
    print("open a decision that uses weight: critical.")
    print("After you edit, run: python3 scripts/check_vault.py")


if __name__ == "__main__":
    main()
