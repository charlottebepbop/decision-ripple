#!/bin/sh
# Start Relate's MCP server on the vault. The full-text index is not committed, and the
# read-only server cannot create it, so build it first. The first open also records that
# note bodies map to the `text` property.
# DECISION_VAULT selects a personal vault. Unset, this serves the sample in vault/.
set -e
ROOT=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
VAULT=${DECISION_VAULT:-$ROOT/vault}
relate query --snapshot-format markdown --markdown-body-properties text --database "$VAULT" \
  < "$ROOT/queries/0-setup.cypher" > /dev/null
exec relate serve --mcp stdio --database "$VAULT" --snapshot-format markdown --read-only=live
