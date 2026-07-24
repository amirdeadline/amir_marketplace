#!/usr/bin/env bash
# Validate every plugin + the marketplace catalog (Claude Code CLI).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v claude >/dev/null 2>&1; then
  echo "claude CLI not on PATH" >&2
  exit 2
fi

echo "== marketplace =="
claude plugin validate "$ROOT"

fail=0
for dir in "$ROOT"/plugins/*; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  echo "== plugin: $name =="
  if ! claude plugin validate "$dir"; then
    echo "FAIL $name" >&2
    fail=1
  fi
done

if [ -f "$ROOT/scripts/verify-marketplace.js" ]; then
  echo "== verify-marketplace.js =="
  node "$ROOT/scripts/verify-marketplace.js" || fail=1
fi

if [ "$fail" -ne 0 ]; then
  echo "validate-all: FAILED" >&2
  exit 1
fi
echo "validate-all: OK"
