#!/usr/bin/env bash
set -euo pipefail

if [[ ! -x .venv/bin/semgrep ]]; then
  printf '%s\n' "Semgrep skipped: install semgrep or use the GitLab CI job."
  exit 0
fi

set +e
output=$(
  SEMGREP_SEND_METRICS=off SEMGREP_ENABLE_VERSION_CHECK=0 \
    .venv/bin/semgrep --config .semgrep.yml --error --metrics off \
    --disable-version-check 2>&1
)
status=$?
set -e

if [[ $status -ne 0 && "$output" == *"empty trust anchors"* ]]; then
  printf '%s\n' "Semgrep skipped: local CA trust store is unavailable."
  printf '%s\n' "$output"
  exit 0
fi

if [[ $status -ne 0 && "$output" == *"Operation not permitted"*".semgrep"* ]]; then
  printf '%s\n' "Semgrep skipped: local Semgrep cache directory is unavailable."
  printf '%s\n' "$output"
  exit 0
fi

printf '%s\n' "$output"
exit "$status"
