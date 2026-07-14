#!/usr/bin/env bash
set -euo pipefail

git ls-files -z | xargs -0 .venv/bin/detect-secrets scan
