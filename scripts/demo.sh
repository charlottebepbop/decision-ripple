#!/usr/bin/env bash
# Run the decision-ripple story on a throwaway copy of vault/.
# The committed notes and briefs/ are left as they are.
set -euo pipefail
cd "$(dirname "$0")/.."

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/vault" "$tmp/briefs"
cp -a vault/. "$tmp/vault/"
rm -rf "$tmp/vault/.cypherlite" "$tmp/vault"/.cypherlite.*
export DECISION_VAULT="$tmp/vault"
export DECISION_BRIEFS="$tmp/briefs"

echo "Using a copy of vault/. The committed notes stay as they are."
echo

relate query --snapshot-format markdown --markdown-body-properties text \
  --database "$DECISION_VAULT" < queries/0-setup.cypher >/dev/null

echo "=== What is already broken ==="
relate query --snapshot-format markdown --markdown-body-properties text \
  --database "$DECISION_VAULT" --mode table --max-rows 0 < queries/6-exposed.cypher
python3 - << 'PY'
import sys
sys.path.insert(0, "scripts")
from graph import query

expected = [
    ("Scan coverage was 88% of trips in October", "BREAKS", "Build the ops dashboard on scan data", "critical"),
    ("Scan coverage was 88% of trips in October", "BREAKS", "Build the route optimizer in house", "critical"),
    ("Scan coverage was 88% of trips in October", "BREAKS", "The optimizer trains on scan data only", "critical"),
    ("Scan coverage was 88% of trips in October", "BREAKS", "Run the weekly ops review from the dashboard", "supporting"),
    ("Supplier flags a 3-week slip on e-cargo bikes", "WEAKENS", "Lease half the e-cargo bikes, buy half", "critical"),
]
got = [(r["signal"], r["effect"], r["decision"], r["weight"]) for r in query("6-exposed")]
if got != expected:
    sys.exit(f"exposed query mismatch:\n{got}")
PY

echo
echo "=== One memo, two assumptions ==="
python3 scripts/add_signal.py q1-budget-holds BREAKS \
  "Finance cuts the Q1 budget and the bike supplier slips" \
  --and ebike-supplier-delivers-feb WEAKENS \
  --source "Board memo" --date 2026-12-04
diff -q "$DECISION_BRIEFS/2026-12-04-finance-cuts-the-q1-budget-and-the-bike-supplier-slips.md" \
  examples/briefs/2026-12-04-finance-cuts-the-q1-budget-and-the-bike-supplier-slips.md
echo "Brief matches examples/briefs/2026-12-04-finance-cuts-the-q1-budget-and-the-bike-supplier-slips.md"

echo
echo "=== The hub decision, replaced twice ==="
python3 scripts/add_decision.py "Open the Rotterdam South hub in Q2" \
  --project hub-2-rotterdam-south --by olu-adeyemi --by tomasz-wilk \
  --rests-on south-hub-lease-signed:critical --rests-on series-a-close-march \
  --supersedes 2026-07-29-open-south-hub-q1 \
  --rationale "The Q1 budget was cut by 20%." --date 2026-12-05
echo
python3 scripts/add_decision.py "Open the Rotterdam South hub in Q3" \
  --project hub-2-rotterdam-south --by olu-adeyemi --by tomasz-wilk \
  --rests-on south-hub-lease-signed:critical --rests-on series-a-close-march \
  --supersedes 2026-12-05-open-the-rotterdam-south-hub-in-q2 \
  --rationale "The Q2 opening slipped." --date 2026-12-10
python3 - << 'PY'
import sys
sys.path.insert(0, "scripts")
from graph import query

by = {r["decision"]: r for r in query("3-precheck", project="hub-2-rotterdam-south")}
q1 = by["Open the Rotterdam South hub in Q1"]
q2 = by["Open the Rotterdam South hub in Q2"]
q3 = by["Open the Rotterdam South hub in Q3"]
if q1["status"] != "superseded" or q1["replaced_by"] != ["Open the Rotterdam South hub in Q3"]:
    sys.exit(f"Q1 should point at the live Q3 decision, got {q1}")
if q2["status"] != "superseded" or q2["replaced_by"] != ["Open the Rotterdam South hub in Q3"]:
    sys.exit(f"Q2 should point at the live Q3 decision, got {q2}")
if q3["status"] != "live" or q3["replaced_by"] != []:
    sys.exit(f"Q3 should be the live decision, got {q3}")
PY

echo
echo "=== Why the mapping contract changed ==="
relate query --snapshot-format markdown --markdown-body-properties text \
  --database "$DECISION_VAULT" --mode table --max-rows 0 \
  --param term=mapping < queries/5-why.cypher
python3 - << 'PY'
import sys
sys.path.insert(0, "scripts")
from graph import query

rows = {r["decision"]: r for r in query("5-why", term="mapping")}
annual = rows["Sign an annual mapping API contract"]
if annual["status"] != "superseded" or annual["replaced_by"] != ["Pay the mapping API monthly until the optimizer ships"]:
    sys.exit(f"mapping search should follow SUPERSEDES to the live decision, got {annual}")
PY
