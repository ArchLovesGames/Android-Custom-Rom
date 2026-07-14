# Agent Guide

This repository may be edited by automated coding agents. Agents should follow these project rules.

## Project Shape

- Application entry point: `app.py`
- Tests: `tests/test_app.py`
- Data files: `data/*.csv`
- Runtime dependencies: `requirements.txt`
- Development dependencies: `requirements-dev.txt`

## Required Checks

Run these before committing code or dataset changes:

```bash
python -m py_compile app.py tests/test_app.py
.venv/bin/pytest
pre-commit run --all-files
```

When tooling dependencies change, install development dependencies first:

```bash
pip install -r requirements-dev.txt
```

## Editing Guidelines

- Keep changes scoped to the requested issue.
- Do not rewrite CSV data unless the issue requires it.
- Preserve required CSV headers documented in `README.md` and `CONTRIBUTING.md`.
- Follow `DATA_ADDITION_MANUAL.md` for database updates.
- Do not commit `.streamlit/secrets.toml`, `.env`, credentials, tokens, or private maintainer data.
- Prefer small, reviewable commits with clear messages.

## Dataset Rules

- `compatibility.csv` rows must reference existing `device_id` and `rom_id` values.
- ROM `status` should be `active`, `inactive`, or `unverified`.
- Use `not found` only for unavailable source fields.
- Include source context in merge requests for dataset updates.
