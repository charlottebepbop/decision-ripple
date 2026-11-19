#!/bin/sh
# Start Relate's MCP server on the vault. The full-text index is not committed, and the
# read-only server cannot create it, so build it first. The first open also records that
# note bodies map to the `text` property.
set -e
cd "$(dirname "$0")/../vault"
relate query --snapshot-format markdown --markdown-body-properties text --database . \
  < ../queries/0-setup.cypher > /dev/null
exec relate serve --mcp stdio --database . --snapshot-format markdown --read-only=live
