"""Write a weekly briefing a business reader can finish in a couple of minutes.

    python3 scripts/weekly.py
    python3 scripts/weekly.py --since 2026-12-05 --as-of 2026-12-12
    python3 scripts/weekly.py --review-after 30

Reads DECISION_VAULT, or vault/ when that is unset. Writes
weekly-<as-of>.md to DECISION_BRIEFS, or to briefs/, and prints it.
Does not add or edit notes.

The window is the 7 days before --as-of, through --as-of, both included.
--since replaces that start. Assumptions with no signal in --review-after
days (default 90) are listed as worth a review. Signals dated after --as-of
are ignored. The six queries in queries/1-ripple.cypher through
queries/6-exposed.cypher are not used here and are not changed.
"""

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

from graph import ROOT, VAULT, query


BAD = ("BREAKS", "WEAKENS")
GOOD = ("CONFIRMS", "SUPPORTS")
PAST = {
    "BREAKS": "broke",
    "WEAKENS": "weakened",
    "SUPPORTS": "supported",
    "CONFIRMS": "confirmed",
}
VERB = {
    "BREAKS": "breaks",
    "WEAKENS": "weakens",
    "SUPPORTS": "supports",
    "CONFIRMS": "confirms",
}
EFFECT_RANK = {"BREAKS": 0, "WEAKENS": 1, "CONFIRMS": 2, "SUPPORTS": 3}
SERIOUS = ("BREAKS", "WEAKENS", "SUPPORTS", "CONFIRMS")


def briefs_dir():
    raw = os.environ.get("DECISION_BRIEFS")
    return Path(raw) if raw else ROOT / "briefs"


def show(path):
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def parse_date(ap, flag, value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""):
        ap.error(f"{flag} {value}: use YYYY-MM-DD")
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        ap.error(f"{flag} {value}: use YYYY-MM-DD")


def friendly(iso):
    day = dt.date.fromisoformat(iso)
    return f"{day.day} {day.strftime('%b')} {day.year}"


def n_things(n, singular, plural=None):
    word = singular if n == 1 else (plural or singular + "s")
    return f"{n} {word}"


def display_name(text, fallback):
    for line in (text or "").splitlines():
        if line.startswith("# "):
            name = line[2:].strip()
            if name:
                return name
    return fallback


def statement_of(row):
    text = (row.get("statement") or "").strip().rstrip(".").strip()
    return text or row["assumption"]


def prefer_effect(effects):
    for effect in SERIOUS:
        if effect in effects:
            return effect
    return None


def project_phrase(titles):
    clean = sorted({title for title in (titles or []) if title})
    if not clean:
        return ""
    return " (" + ", ".join(clean) + ")"


def decision_line(row):
    weight = row["weight"]
    label = f"**{weight}**" if weight == "critical" else weight
    confidence = row.get("confidence") or "unspecified"
    return f"- {label}, {confidence} — {row['decision']}{project_phrase(row['projects'])}"


def quote_signals(rows):
    bits = []
    for row in rows:
        bits.append(f"\"{row['signal']}\" ({friendly(row['date'])}) {VERB[row['effect']]} it")
    return "; ".join(bits)


def bad_sentence(rows):
    if not rows:
        return "Nothing broke or weakened."
    n_signals = len({(row["date"], row["signal"]) for row in rows})
    n_assumptions = len({row["assumption"] for row in rows})
    effects = {row["effect"] for row in rows}
    if effects == {"BREAKS"}:
        verb = "breaks" if n_signals == 1 else "break"
    elif effects == {"WEAKENS"}:
        verb = "weakens" if n_signals == 1 else "weaken"
    else:
        verb = "breaks or weakens" if n_signals == 1 else "break or weaken"
    if n_signals == 1 and n_assumptions == 1:
        return f"1 signal {verb} an assumption: \"{statement_of(rows[0])}.\""
    return f"{n_things(n_signals, 'signal')} {verb} {n_things(n_assumptions, 'assumption')}."


def risk_sentence(rows):
    by_title = {}
    for row in rows:
        by_title.setdefault(row["decision"], set()).add(row["weight"])
    n = len(by_title)
    critical = sum(1 for weights in by_title.values() if "critical" in weights)
    if n == 0:
        return "No live decision is at risk from this window."
    if n == 1 and critical == 1:
        return "1 live decision is at risk, critically."
    if n == 1:
        return "1 live decision is at risk."
    if critical == 0:
        return f"{n} live decisions are at risk."
    if critical == n:
        return f"{n} live decisions are at risk, all of them critically."
    return f"{n} live decisions are at risk, {critical} of them critically."


def tell_sentence(rows):
    n = len(rows)
    person = n_things(n, "person", "people")
    top = rows[0]
    if int(top["critical"]) <= 0:
        return f"Tell {person}."
    name = display_name(top.get("text"), top["person"])
    return f"Tell {person}, {name} first."


def good_sentence(rows, evidence):
    n_signals = len({(row["date"], row["signal"]) for row in rows})
    effects = {row["effect"] for row in rows}
    mixed = any(
        hit["effect"] in BAD
        for row in rows
        for hit in evidence.get(row["assumption"], [])
    )
    if effects == {"CONFIRMS"}:
        verb = "confirms" if n_signals == 1 else "confirm"
    elif effects == {"SUPPORTS"}:
        verb = "supports" if n_signals == 1 else "support"
    else:
        verb = "confirms or supports" if n_signals == 1 else "confirm or support"
    if n_signals == 1 and mixed:
        return f"1 signal {verb} an assumption that has also been broken or weakened."
    if n_signals == 1:
        return f"1 signal {verb} an assumption."
    sentence = f"{n_things(n_signals, 'signal')} {verb} assumptions."
    if mixed:
        return sentence + " At least one has also been broken or weakened."
    return sentence


def quiet_sentence(rows, days):
    n = len(rows)
    if n == 0:
        return f"Every assumption has a signal in the last {days} days."
    if n == 1:
        return f"1 assumption has no signal in the last {days} days."
    return f"{n} assumptions have no signal in the last {days} days."


def lead(window, risk_rows, tell_rows, evidence, quiet_rows, days):
    bad = [row for row in window if row["effect"] in BAD]
    good = [row for row in window if row["effect"] in GOOD]
    sentences = [bad_sentence(bad), risk_sentence(risk_rows)]
    if bad and not tell_rows:
        sentences.append("Nobody to tell.")
    elif tell_rows:
        sentences.append(tell_sentence(tell_rows))
    if good:
        sentences.append(good_sentence(good, evidence))
    sentences.append(quiet_sentence(quiet_rows, days))
    return " ".join(sentences)


def decision_phrase(rows):
    weights = {}
    for row in rows:
        if row["weight"] == "critical" or row["decision"] not in weights:
            weights[row["decision"]] = row["weight"]
    if not weights:
        return "No live decision rests on it."
    critical = sorted(title for title, weight in weights.items() if weight == "critical")
    supporting = sorted(title for title, weight in weights.items() if weight != "critical")
    bits = []
    if critical:
        bits.append(f"{len(critical)} critical: " + "; ".join(critical))
    if supporting:
        bits.append(f"{len(supporting)} supporting")
    return ". ".join(bits) + "."


def review_line(row):
    statement = statement_of(row)
    last = row.get("last_signal")
    if not last:
        return f"- {statement}."
    when = friendly(last)
    effect = prefer_effect(row.get("effects") or [])
    titles = [title for title in (row.get("titles") or []) if title]
    verb = PAST.get(effect)
    if verb and len(titles) == 1:
        return f"- {statement}. Last signal {when} {verb} it: \"{titles[0]}\"."
    if verb:
        return f"- {statement}. Last signal {when} {verb} it."
    return f"- {statement}. Last signal {when}."


def heading(since, as_of):
    if since == as_of:
        return f"# Weekly briefing, {friendly(as_of)}"
    return f"# Weekly briefing, {friendly(since)} to {friendly(as_of)}"


def broke_lines(window):
    rows = [row for row in window if row["effect"] in BAD]
    rows.sort(key=lambda row: (EFFECT_RANK[row["effect"]], row["date"], row["signal"]))
    if not rows:
        return ["Nothing broke or weakened in this window."]
    lines = []
    for row in rows:
        lines.append(
            f"- **{friendly(row['date'])}** — {row['signal']} ({row['source']}) "
            f"**{VERB[row['effect']]}** \"{statement_of(row)}.\""
        )
    return lines


def group_rows(risk_rows):
    groups = {}
    for row in risk_rows:
        groups.setdefault(row["assumption"], []).append(row)
    ordered = sorted(
        groups.items(),
        key=lambda item: (
            -sum(1 for row in item[1] if row["weight"] == "critical"),
            statement_of(item[1][0]),
        ),
    )
    return ordered


def evidence_lines(assumption, window, evidence, since, as_of):
    week = [row for row in window if row["assumption"] == assumption]
    bad = [row for row in week if row["effect"] in BAD]
    good = [row for row in week if row["effect"] in GOOD]
    bad.sort(key=lambda row: (row["date"], EFFECT_RANK[row["effect"]], row["signal"]))
    good.sort(key=lambda row: (row["date"], row["signal"]))
    lines = []
    for row in bad:
        word = "Broken" if row["effect"] == "BREAKS" else "Weakened"
        lines.append(f"{word} by \"{row['signal']}\" ({friendly(row['date'])}, {row['source']}).")
    if good:
        lines.append("Also this week: " + quote_signals(good) + ".")
    earlier = [
        row for row in evidence.get(assumption, [])
        if row["effect"] in GOOD and row["date"] < since
    ]
    earlier.sort(key=lambda row: (row["date"], row["signal"]))
    if earlier:
        shown = earlier[:3]
        extra = len(earlier) - len(shown)
        text = "Earlier: " + quote_signals(shown) + "."
        if extra:
            text += f" And {extra} more."
        lines.append(text)
    return lines


def at_risk_lines(window, risk_rows, evidence, since, as_of):
    if not risk_rows:
        return ["No live decision rests on what broke or weakened in this window."]
    lines = ["Grouped by assumption. Critical first.", ""]
    for assumption, rows in group_rows(risk_rows):
        rows = sorted(rows, key=lambda row: (0 if row["weight"] == "critical" else 1, row["decision"]))
        lines.append(f"### {statement_of(rows[0])}")
        lines.append("")
        for note in evidence_lines(assumption, window, evidence, since, as_of):
            lines.append(note)
            lines.append("")
        for row in rows:
            lines.append(decision_line(row))
        lines.append("")
    return lines


def doubled_critical(risk_rows):
    counts = {}
    for row in risk_rows:
        if row["weight"] == "critical":
            counts[row["decision"]] = counts.get(row["decision"], 0) + 1
    return [title for title, count in sorted(counts.items()) if count > 1]


def tell_lines(rows, risk_rows):
    if not rows:
        return ["Nobody to tell."]
    lines = ["Most exposed first. A decision that is critical under two assumptions counts once.", ""]
    for row in rows:
        name = display_name(row.get("text"), row["person"])
        decisions = sorted(row.get("critical_decisions") or []) + sorted(row.get("other_decisions") or [])
        lines.append(
            f"- **{name}** ({row['role']}, {int(row['critical'])} critical): {'; '.join(decisions)}"
        )
    doubled = doubled_critical(risk_rows)
    if len(doubled) == 1:
        lines += ["", f"{doubled[0]} is critical under more than one assumption and is counted once."]
    elif doubled:
        lines += ["", "Counted once, each is critical under more than one assumption: " + "; ".join(doubled) + "."]
    return lines


def mixed_clause(row, evidence, since, as_of, decisions):
    bad = [hit for hit in evidence.get(row["assumption"], []) if hit["effect"] in BAD]
    if not bad:
        return ""
    in_window = [hit for hit in bad if since <= hit["date"] <= as_of]
    older = [hit for hit in bad if hit["date"] < since]
    in_window.sort(key=lambda hit: (hit["date"], EFFECT_RANK[hit["effect"]], hit["signal"]))
    older.sort(key=lambda hit: (hit["date"], EFFECT_RANK[hit["effect"]], hit["signal"]))
    parts = []
    if in_window:
        parts.append("Mixed: " + quote_signals(in_window) + " this week. See Live decisions at risk.")
    if older:
        parts.append("Mixed: " + quote_signals(older) + ". " + decision_phrase(decisions.get(row["assumption"], [])))
    if not parts:
        return ""
    return " " + " ".join(parts)


def good_lines(window, evidence, since, as_of, decisions):
    rows = [row for row in window if row["effect"] in GOOD]
    rows.sort(key=lambda row: (row["date"], EFFECT_RANK[row["effect"]], row["signal"]))
    if not rows:
        return ["Nothing was confirmed or supported in this window."]
    lines = []
    for row in rows:
        lines.append(
            f"- **{friendly(row['date'])}** — {row['signal']} ({row['source']}) "
            f"**{VERB[row['effect']]}** \"{statement_of(row)}.\""
            + mixed_clause(row, evidence, since, as_of, decisions)
        )
    return lines


def quiet_lines(rows, days):
    rows = sorted(rows, key=lambda row: (row.get("last_signal") is not None, row.get("last_signal") or "", statement_of(row)))
    if not rows:
        return [f"Every assumption has a signal in the last {days} days."]
    lines = [quiet_sentence(rows, days), ""]
    for row in rows:
        lines.append(review_line(row))
    return lines


def render(since, as_of, review_days, window, risk_rows, tell_rows, quiet_rows, evidence, decisions):
    lines = [
        heading(since, as_of),
        "",
        lead(window, risk_rows, tell_rows, evidence, quiet_rows, review_days),
        "",
        "## Broke or weakened",
        "",
        *broke_lines(window),
        "",
        "## Live decisions at risk",
        "",
        *at_risk_lines(window, risk_rows, evidence, since, as_of),
        "",
        "## Who to tell",
        "",
        *tell_lines(tell_rows, risk_rows),
        "",
        "## Confirmed or supported",
        "",
        *good_lines(window, evidence, since, as_of, decisions),
        "",
        "## Worth a review",
        "",
        *quiet_lines(quiet_rows, review_days),
        "",
    ]
    text = "\n".join(lines)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    if not text.endswith("\n"):
        text += "\n"
    return text


def names_of(rows):
    found = []
    for row in rows:
        if row["assumption"] not in found:
            found.append(row["assumption"])
    return found


def has_bad(evidence, assumption):
    return any(hit["effect"] in BAD for hit in evidence.get(assumption, []))


def index_evidence(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["assumption"], []).append(row)
    return grouped


def index_decisions(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["assumption"], []).append(row)
    return grouped


def load(since, as_of, horizon):
    window = query("7-window", since=since, as_of=as_of)
    mentioned = names_of(window)
    evidence_rows = query("11-evidence", assumptions=mentioned, as_of=as_of) if mentioned else []
    evidence = index_evidence(evidence_rows)
    bad_names = names_of([row for row in window if row["effect"] in BAD])
    good_names = names_of([row for row in window if row["effect"] in GOOD])
    extra = [name for name in good_names if name not in bad_names and has_bad(evidence, name)]
    wanted = bad_names + [name for name in extra if name not in bad_names]
    decision_rows = query("8-at-risk", assumptions=wanted) if wanted else []
    risk_rows = [row for row in decision_rows if row["assumption"] in bad_names]
    tell_rows = query("9-weekly-tell", assumptions=bad_names) if bad_names else []
    quiet_rows = query("10-quiet", since=horizon, as_of=as_of)
    return window, risk_rows, tell_rows, quiet_rows, evidence, index_decisions(decision_rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", help="First day of the window, YYYY-MM-DD. Default is 7 days before --as-of.")
    ap.add_argument("--as-of", help="Last day of the window, YYYY-MM-DD. Default is today.")
    ap.add_argument("--review-after", type=int, default=90,
                    help="Flag an assumption with no signal in this many days (default 90).")
    args = ap.parse_args()
    if args.review_after < 0:
        ap.error("--review-after must be 0 or more")

    as_of = parse_date(ap, "--as-of", args.as_of) if args.as_of else dt.date.today()
    since = parse_date(ap, "--since", args.since) if args.since else as_of - dt.timedelta(days=7)
    if since > as_of:
        ap.error(f"--since {since.isoformat()} is after --as-of {as_of.isoformat()}")
    horizon = as_of - dt.timedelta(days=args.review_after)

    window, risk_rows, tell_rows, quiet_rows, evidence, decisions = load(
        since.isoformat(), as_of.isoformat(), horizon.isoformat(),
    )
    text = render(
        since.isoformat(), as_of.isoformat(), args.review_after,
        window, risk_rows, tell_rows, quiet_rows, evidence, decisions,
    )
    folder = briefs_dir()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"weekly-{as_of.isoformat()}.md"
    path.write_text(text)
    print(f"Vault: {VAULT}")
    print()
    sys.stdout.write(text)
    if not text.endswith("\n"):
        print()
    print(f"Brief: {show(path)}")


if __name__ == "__main__":
    main()
