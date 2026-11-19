"""Check vault notes for links and headers Relate would misread.

    python3 scripts/check_vault.py
    python3 scripts/check_vault.py path/to/vault

With no path, DECISION_VAULT is checked when that variable is set.

Prints a plain-language fix for each problem and exits non-zero when any are found.
Python 3 only. No third-party packages.

The scan walks every `[[...]]` in the files, including ones in odd places, so a link
is reported or counted and never skipped. Relate drops some of those forms silently
(the folder name must match exactly) and rejects others (an unquoted link in a header).
"""

import argparse
import datetime as dt
import difflib
import os
import re
import sys
from pathlib import Path

LABELS = ("Decision", "Assumption", "Person", "Project", "Signal")
# Navigation files Relate writes. They are not notes, but their links still have to resolve.
SKIP_NAMES = {"index.md", "log.md"}
EDGE_TARGET = {
    "RESTS_ON": "Assumption",
    "STEERS": "Project",
    "DECIDED_BY": "Person",
    "SUPERSEDES": "Decision",
    "AMENDS": "Decision",
    "OWNED_BY": "Person",
    "STAKEHOLDER": "Person",
    "CONFIRMS": "Assumption",
    "SUPPORTS": "Assumption",
    "WEAKENS": "Assumption",
    "BREAKS": "Assumption",
}
SIGNAL_EFFECTS = ("CONFIRMS", "SUPPORTS", "WEAKENS", "BREAKS")
REQUIRED = {
    "Decision": ("name", "title", "date", "confidence", "status"),
    "Assumption": ("name", "statement"),
    "Person": ("name", "role"),
    "Project": ("name", "title"),
    "Signal": ("name", "title", "source", "date"),
}
CONFIDENCE = {"low", "medium", "high"}
STATUS = {"live", "superseded"}
LINK_RE = re.compile(r"\[\[([^\]\n]*)\]\]")
HEADING_RE = re.compile(r"^# +(.+?)\s*$", re.M)


class Issue:
    def __init__(self, path, message, fix):
        self.path = path
        self.message = message
        self.fix = fix


class Report:
    def __init__(self):
        self.issues = []
        self.links_seen = 0
        self.notes = 0

    def add(self, path, message, fix):
        self.issues.append(Issue(path, message, fix))

    @property
    def ok(self):
        return not self.issues


def unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def split_frontmatter(text):
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, text, None
    newline = 4 if text.startswith("---\n") else 5
    rest = text[newline:]
    for fence in ("\n---\n", "\n---\r\n"):
        idx = rest.find(fence)
        if idx != -1:
            return rest[:idx], rest[idx + len(fence):], len(text) - len(rest) + idx
    if rest.endswith("\n---"):
        return rest[:-4], "", len(text) - 3
    return "UNCLOSED", "", None


def parse_frontmatter(fm_text):
    data = {}
    current_key = None
    current_map = None
    for lineno, line in enumerate(fm_text.splitlines(), 1):
        if not line.strip():
            continue
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if stripped.startswith("- ") and indent >= 2:
            if current_key is None:
                raise ValueError(f"line {lineno} is a list item with no field above it")
            raw = stripped[2:].strip()
            current_map = None
            bucket = data.setdefault(current_key, [])
            if not isinstance(bucket, list):
                bucket = []
                data[current_key] = bucket
            if raw[:1] in ("'", '"') or raw.startswith("[["):
                bucket.append(unquote(raw))
            elif ":" in raw:
                key, value = raw.split(":", 1)
                current_map = {key.strip(): unquote(value.strip())}
                bucket.append(current_map)
            else:
                bucket.append(raw)
            continue
        if indent >= 4 and current_map is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_map[key.strip()] = unquote(value.strip())
            continue
        if indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            current_map = None
            value = value.strip()
            if value == "":
                if not isinstance(data.get(current_key), list):
                    data[current_key] = []
            else:
                data[current_key] = unquote(value)
            continue
        raise ValueError(f"line {lineno} does not look like a header field: {stripped}")
    return data


def link_inners(value):
    if isinstance(value, str):
        return LINK_RE.findall(value)
    return []


def scan_links(text):
    """Every `[[` is either a closed target or an unclosed fragment. Nothing is skipped."""
    found = []
    i = 0
    while True:
        start = text.find("[[", i)
        if start < 0:
            break
        end = text.find("]]", start + 2)
        newline = text.find("\n", start + 2)
        if end < 0 or (newline >= 0 and newline < end):
            line_end = newline if newline >= 0 else len(text)
            found.append({"closed": False, "inner": text[start:line_end].rstrip(), "start": start, "end": line_end})
            i = line_end
            continue
        found.append({"closed": True, "inner": text[start + 2:end], "start": start, "end": end + 2})
        i = end + 2
    return found


def quoted_link(text, link):
    before = text[link["start"] - 1] if link["start"] else ""
    after = text[link["end"]] if link["end"] < len(text) else ""
    return before == after and before in ("'", '"')


def heading(body):
    match = HEADING_RE.search(body or "")
    if not match:
        return ""
    return " ".join(match.group(1).casefold().split())


def valid_date(value):
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def stems(root, folder):
    directory = root / folder
    if not directory.is_dir():
        return []
    return sorted(p.stem for p in directory.glob("*.md"))


def suggest(root, folder, slug):
    """Return (label/stem, reason) for the closest real note, or (None, None)."""
    folder_stems = stems(root, folder)
    for stem in folder_stems:
        if stem.casefold() == slug.casefold() and stem != slug:
            return f"{folder}/{stem}", "capitals"
    for label in LABELS:
        if label.casefold() == folder.casefold() and label != folder:
            for stem in stems(root, label):
                if stem.casefold() == slug.casefold():
                    return f"{label}/{stem}", "folder-case"
    close = difflib.get_close_matches(slug, folder_stems, n=1, cutoff=0.8)
    if close:
        return f"{folder}/{close[0]}", "rename"
    for label in LABELS:
        if label == folder:
            continue
        for stem in stems(root, label):
            if stem == slug or stem.casefold() == slug.casefold():
                return f"{label}/{stem}", "other-folder"
    folder_close = difflib.get_close_matches(folder, list(LABELS), n=1, cutoff=0.7)
    if folder_close:
        label = folder_close[0]
        label_stems = stems(root, label)
        if slug in label_stems:
            return f"{label}/{slug}", "folder-typo"
        close = difflib.get_close_matches(slug, label_stems, n=1, cutoff=0.8)
        if close:
            return f"{label}/{close[0]}", "folder-typo"
    return None, None


def split_target(inner):
    path = inner.split("|", 1)[0]
    if path != path.strip() or " " in path or "\t" in path:
        return None, None, "spaces"
    if "#" in path:
        return None, None, "hash"
    if "/" not in path:
        return None, None, "no-folder"
    folder, slug = path.split("/", 1)
    if not folder or not slug or "/" in slug:
        return None, None, "shape"
    return folder, slug, None


def check_closed_link(root, rel, text, link, fm_end, report):
    inner = link["inner"]
    display = f"[[{inner}]]"
    in_header = fm_end is not None and link["start"] < fm_end
    if in_header and not quoted_link(text, link):
        report.add(
            rel, f"Link {display} in the header is not in quotes.",
            'Write it as "' + display + '". An unquoted link makes Relate reject the whole note.',
        )
    folder, slug, problem = split_target(inner)
    if problem == "spaces":
        report.add(
            rel, f"Link {display} has spaces in the path, so it does not match a file.",
            "Remove the spaces. A link has to be exactly [[Folder/note-name]].",
        )
        return
    if problem == "hash":
        base = inner.split("|", 1)[0].split("#", 1)[0].strip()
        hint = f"[[{base}]]" if base else "the note, with no #heading"
        report.add(
            rel,
            f"Link {display} will not reach that note. Relate turns '#' into a different note name.",
            f"Link to {hint}. Put the heading in the body of the note.",
        )
        return
    if problem:
        report.add(
            rel, f"Link {display} is not a folder plus a note name.",
            "Write [[Folder/note-name]], using Decision, Assumption, Person, Project, or Signal.",
        )
        return
    target = root / folder / f"{slug}.md"
    if target.is_file():
        return
    suggestion, reason = suggest(root, folder, slug)
    if reason in ("capitals", "folder-case"):
        report.add(
            rel,
            f"Link {display} does not match a file exactly, so Relate drops it and the connection never reaches the graph.",
            f"Change it to [[{suggestion}]]. Capitals and the folder name have to match the file.",
        )
        return
    if suggestion and reason == "rename":
        report.add(
            rel,
            f"Link {display} points at no note. Relate would create an empty note with this name, so the typo looks connected. The name is close to one that exists, which usually means a typo or the note was renamed.",
            f"Change it to [[{suggestion}]]. Do not leave the empty note in place.",
        )
        return
    if suggestion:
        report.add(
            rel, f"Link {display} points at no note.",
            f"Change it to [[{suggestion}]].",
        )
        return
    report.add(
        rel, f"Link {display} points at no note.",
        "Point it at a note that exists, or create that note. Nothing in the vault has a similar name.",
    )


def edge_items(data, key):
    value = data.get(key)
    if isinstance(value, list):
        return value
    return []


def check_edges(rel, data, report):
    for key, expected in EDGE_TARGET.items():
        for item in edge_items(data, key):
            weight = None
            if isinstance(item, dict):
                inners = link_inners(item.get("target", ""))
                weight = item.get("weight")
                if not inners:
                    report.add(
                        rel, f"The {key} entry has no wikilink, so Relate will not store that connection.",
                        f'Give it a target, for example target: "[[{expected}/note-name]]".',
                    )
                    continue
            elif isinstance(item, str):
                inners = link_inners(item)
                if not inners:
                    report.add(
                        rel, f"The {key} entry {item!r} is not a wikilink, so Relate rejects the note.",
                        f'Write a quoted link, for example "[[{expected}/note-name]]".',
                    )
                    continue
            else:
                report.add(
                    rel, f"A {key} entry is not a link.",
                    f'Write a quoted link, for example "[[{expected}/note-name]]".',
                )
                continue
            if weight is not None and key != "RESTS_ON":
                report.add(
                    rel, f"{key} carries a weight, and only RESTS_ON uses one.",
                    "Remove the weight, or move the link under RESTS_ON.",
                )
            if weight is not None and weight != "critical":
                report.add(
                    rel, f"The weight is {weight!r}. The only weight is critical.",
                    "Set weight to critical, or leave it off. A link with no weight is supporting.",
                )
            folder, slug, problem = split_target(inners[0])
            if problem or folder is None:
                continue
            if folder.casefold() != expected.casefold():
                report.add(
                    rel,
                    f"{key} links to {folder}/{slug}, but {key} has to point at a {expected}.",
                    f"Move the link under the matching header, or point it at a {expected} note.",
                )


def resolved_targets(root, data, key, expected):
    found = []
    for item in edge_items(data, key):
        raw = item.get("target", "") if isinstance(item, dict) else item
        for inner in link_inners(raw):
            folder, slug, problem = split_target(inner)
            if problem or folder != expected:
                continue
            if (root / folder / f"{slug}.md").is_file():
                found.append(slug)
    return found


def check_fields(root, rel, folder, data, report):
    declared = data.get("type")
    if not isinstance(declared, str) or not declared:
        report.add(rel, "The header has no type.", f"Add type: {folder}, matching the folder the file is in.")
        return
    if declared != folder:
        report.add(
            rel,
            f"The header says type: {declared}, but the file is in the {folder} folder. Relate uses the folder as the label.",
            f"Set type: {folder}, or move the file into {declared}/.",
        )
        return
    for field in REQUIRED[folder]:
        value = data.get(field)
        if isinstance(value, str) and value.strip():
            continue
        if folder == "Decision" and field == "status":
            report.add(
                rel,
                "The header is missing status. The ripple, the tell list, and the already-broken view only keep decisions with status live, so this decision disappears from all three.",
                "Add status: live, or status: superseded if a newer decision replaced it.",
            )
            continue
        report.add(
            rel, f"The header is missing {field}.",
            f"Add {field} to the header. Queries read these fields by name.",
        )
    name = data.get("name")
    filename = Path(rel).stem
    if isinstance(name, str) and name and name != filename:
        report.add(
            rel,
            f"The file is named {filename}.md but the header says name: {name}. "
            f"Relate refuses to open the vault: key property 'name' value '{name}' does not match its filename '{filename}'. "
            "Every query fails until they match.",
            f"Rename the file to {name}.md, or set name to {filename} and update every link.",
        )
    if folder == "Decision":
        confidence = data.get("confidence")
        if isinstance(confidence, str) and confidence and confidence not in CONFIDENCE:
            report.add(
                rel, f"confidence is {confidence!r}. Fragile-ground only understands low, medium, and high.",
                "Set confidence to low, medium, or high.",
            )
        status = data.get("status")
        if isinstance(status, str) and status and status not in STATUS:
            report.add(
                rel, f"status is {status!r}. A decision is live or superseded.",
                "Set status to live, or to superseded when a newer decision replaces it.",
            )
        if not resolved_targets(root, data, "RESTS_ON", "Assumption"):
            report.add(
                rel,
                "This decision rests on no assumption. A signal that breaks an assumption can never flag it.",
                "Add RESTS_ON with a link to each assumption it needs. Use weight: critical only when the decision fails without that assumption.",
            )
    if folder == "Signal":
        if isinstance(data.get("date"), str) and data.get("date") and not valid_date(data["date"]):
            report.add(
                rel, f"date is {data['date']!r}. Dates are written YYYY-MM-DD.",
                "Set date to a day, for example 2026-12-01.",
            )
        if not any(resolved_targets(root, data, effect, "Assumption") for effect in SIGNAL_EFFECTS):
            # Still complain when the keys are missing entirely or every target is broken.
            has_attempt = any(edge_items(data, effect) for effect in SIGNAL_EFFECTS)
            if not has_attempt:
                report.add(
                    rel,
                    "This signal does not confirm, support, weaken, or break an assumption, so it can never show up as pressure.",
                    "Add CONFIRMS, SUPPORTS, WEAKENS, or BREAKS with a link to the assumption it is about.",
                )
    if folder in ("Decision", "Signal") and isinstance(data.get("date"), str) and data.get("date"):
        if folder == "Decision" and not valid_date(data["date"]):
            report.add(
                rel, f"date is {data['date']!r}. Dates are written YYYY-MM-DD.",
                "Set date to a day, for example 2026-12-01.",
            )
    if folder == "Person":
        role = data.get("role")
        if isinstance(role, str) and not role.strip():
            report.add(rel, "role is empty.", "Name the person's role, for example Head of Operations.")


def check_status_and_owners(root, notes, report):
    superseded_by = {}
    rests = {}
    for note in notes:
        if note["folder"] != "Decision":
            continue
        for slug in resolved_targets(root, note["data"], "SUPERSEDES", "Decision"):
            superseded_by.setdefault(slug, []).append(note)
        for slug in resolved_targets(root, note["data"], "RESTS_ON", "Assumption"):
            rests.setdefault(slug, []).append(note)
    decisions = {note["stem"]: note for note in notes if note["folder"] == "Decision" and note["stem"]}
    for stem, note in decisions.items():
        status = note["data"].get("status")
        incoming = superseded_by.get(stem, [])
        if incoming and status != "superseded":
            names = ", ".join(item["rel"] for item in incoming)
            report.add(
                note["rel"],
                f"status is {status!r}, but {names} supersedes this decision. The ripple would keep flagging the old decision.",
                "Set status to superseded. The pre-check follows SUPERSEDES to the decision that is still live.",
            )
        if status == "superseded" and not incoming:
            report.add(
                note["rel"],
                "status is superseded, but no decision links to it with SUPERSEDES. The pre-check cannot name a replacement.",
                "Point the newer decision at this one with SUPERSEDES, or set status back to live if it was not replaced.",
            )
    for note in notes:
        if note["folder"] != "Assumption" or note.get("phantom"):
            continue
        if rests.get(note["stem"]):
            continue
        report.add(
            note["rel"],
            "This assumption has no owner. No decision rests on it, so a signal that breaks it flags nobody.",
            "On the decision that depends on it, add a RESTS_ON link here. If nothing depends on it, delete the note.",
        )


def check_duplicates(notes, report):
    by_name = {}
    by_heading = {}
    for note in notes:
        name = note["data"].get("name")
        if isinstance(name, str) and name:
            by_name.setdefault((note["folder"], name), []).append(note)
        if note["folder"] == "Person":
            title = heading(note["body"])
            if title:
                by_heading.setdefault(title, []).append(note)
    for (folder, name), group in by_name.items():
        if len(group) < 2:
            continue
        paths = ", ".join(item["rel"] for item in group)
        for note in group:
            report.add(
                note["rel"],
                f"Another {folder} note also uses the name {name!r} ({paths}).",
                "Keep one note. Give the other a new name and point every link at the one you keep.",
            )
    for title, group in by_heading.items():
        if len(group) < 2:
            continue
        paths = ", ".join(item["rel"] for item in group)
        for note in group:
            report.add(
                note["rel"],
                f"This is the same person as another note, both headed {title!r} ({paths}).",
                "Keep one person note. Two notes split the decisions between them, so the tell list can miss someone.",
            )


def is_phantom(data, body):
    """Relate's empty note: type and name, no body, no other fields. A mistyped wikilink creates one."""
    if body and body.strip():
        return False
    for key, value in data.items():
        if key in ("type", "name"):
            continue
        if isinstance(value, str) and value.strip():
            return False
        if isinstance(value, list) and value:
            return False
    return bool(data.get("type")) and bool(data.get("name"))


def flag_phantoms(root, notes, report):
    phantom_keys = {(note["folder"], note["stem"]) for note in notes if note.get("phantom")}
    real = {}
    for note in notes:
        if note.get("phantom"):
            continue
        real.setdefault(note["folder"], []).append(note["stem"])
    for note in notes:
        if not note.get("phantom"):
            continue
        close = difflib.get_close_matches(note["stem"], real.get(note["folder"], []), n=1, cutoff=0.8)
        if close:
            report.add(
                note["rel"],
                f"This note only has type and name. Relate created this empty {note['folder']} when a link pointed at a note that does not exist yet.",
                f"Point the link at [[{note['folder']}/{close[0]}]] and delete {note['rel']}.",
            )
        else:
            report.add(
                note["rel"],
                f"This note only has type and name. It is an empty {note['folder']}, so a signal or a query has nothing to say about it.",
                f"Add the fields a {note['folder']} needs, or delete the file if a mistyped link created it.",
            )
    for path in iter_markdown(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for link in scan_links(text):
            if not link["closed"]:
                continue
            folder, slug, problem = split_target(link["inner"])
            if problem or (folder, slug) not in phantom_keys:
                continue
            close = difflib.get_close_matches(slug, real.get(folder, []), n=1, cutoff=0.8)
            display = f"[[{link['inner']}]]"
            if close:
                report.add(
                    rel,
                    f"Link {display} points at an empty note. Relate created {folder}/{slug}.md because that note did not exist, and the link looks connected.",
                    f"Change it to [[{folder}/{close[0]}]] and delete {folder}/{slug}.md.",
                )
            else:
                report.add(
                    rel,
                    f"Link {display} points at an empty note that only has type and name.",
                    f"Fill in {folder}/{slug}.md, or delete it and point the link at a real {folder}.",
                )


def iter_markdown(root):
    for path in sorted(root.rglob("*.md")):
        parts = path.relative_to(root).parts
        if any(part.startswith(".") for part in parts):
            continue
        yield path


def check_vault(root):
    root = Path(root)
    report = Report()
    notes = []
    if not root.is_dir():
        report.add(".", f"{root} is not a folder of notes.", "Pass the vault directory, the one that contains Decision/ and Assumption/.")
        return report
    for path in iter_markdown(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        fm, body, fm_end = split_frontmatter(text)
        links = scan_links(text)
        report.links_seen += len(links)
        for link in links:
            if not link["closed"]:
                report.add(
                    rel,
                    f"A link starts and never closes, so Relate ignores it: {link['inner']}",
                    "Close it with ]]. A link looks like [[Assumption/note-name]].",
                )
                continue
            check_closed_link(root, rel, text, link, fm_end, report)
        folder = path.parent.name
        if path.name in SKIP_NAMES or folder not in LABELS:
            continue
        report.notes += 1
        if fm is None:
            report.add(
                rel, "This note has no header.",
                f"Start the file with --- and the fields for a {folder}, then close the header with ---.",
            )
            continue
        if fm == "UNCLOSED":
            report.add(
                rel, "The header opens with --- and never closes, so Relate will not read the note.",
                "Add a line that is only --- under the fields.",
            )
            continue
        try:
            data = parse_frontmatter(fm)
        except ValueError as exc:
            report.add(rel, f"The header is malformed ({exc}).", "Use field: value, and quoted wikilinks in lists.")
            continue
        phantom = is_phantom(data, body)
        notes.append({
            "rel": rel,
            "folder": folder,
            "stem": path.stem,
            "data": data,
            "body": body,
            "phantom": phantom,
        })
        if phantom:
            continue
        check_fields(root, rel, folder, data, report)
        check_edges(rel, data, report)
    flag_phantoms(root, notes, report)
    check_status_and_owners(root, notes, report)
    check_duplicates(notes, report)
    report.issues.sort(key=lambda item: (item.path, item.message))
    return report


def render(report, root):
    if report.ok:
        return f"{root} looks consistent ({report.notes} notes, {report.links_seen} links)."
    lines = []
    current = None
    for issue in report.issues:
        if issue.path != current:
            if current is not None:
                lines.append("")
            current = issue.path
            lines.append(issue.path)
        lines.append(f"  {issue.message}")
        lines.append(f"  Fix: {issue.fix}")
    count = len(report.issues)
    noun = "problem" if count == 1 else "problems"
    lines.append("")
    lines.append(f"{count} {noun}. The vault check failed.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "vault", nargs="?",
        help="notes folder (default: DECISION_VAULT, or vault/ next to scripts/)",
    )
    args = parser.parse_args()
    if args.vault:
        root = Path(args.vault)
    elif os.environ.get("DECISION_VAULT"):
        root = Path(os.environ["DECISION_VAULT"])
    else:
        root = Path(__file__).resolve().parent.parent / "vault"
    report = check_vault(root)
    print(render(report, root))
    sys.exit(0 if report.ok else 1)


if __name__ == "__main__":
    main()
