#!/usr/bin/env bash
set -euo pipefail

set +e
output=$(.venv/bin/pip-audit --local 2>&1)
status=$?
set -e

if [[ $status -ne 0 && "$output" == *"Failed to resolve"* ]]; then
  printf '%s\n' "Dependency audit skipped: vulnerability service is unreachable."
  printf '%s\n' "$output"
  exit 0
fi

printf '%s\n' "$output"
exit "$status"
