# Contributing

Thank you for helping improve Android Custom ROM. This project is a Streamlit app backed by CSV datasets for devices, ROMs, and compatibility relationships.

Live app: https://custom-rom-android-finder.streamlit.app/

## Getting Started

1. Fork the repository.
2. Create a feature branch from the latest target branch.
3. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

5. Install the pre-commit hook:

```bash
pre-commit install
```

## Running Locally

Start the app with:

```bash
streamlit run app.py
```

Run tests with:

```bash
.venv/bin/pytest
```

Run all pre-commit checks manually with:

```bash
pre-commit run --all-files
```

## Dataset Contributions

Dataset changes should be accurate, verifiable, and consistent with the CSV format templates in `data/`.

For the detailed database contribution workflow, read `DATA_ADDITION_MANUAL.md`.

Required columns:

- `data/devices.csv`: `device_id`, `device_type`, `brand`, `device`, `model`
- `data/roms.csv`: `rom_id`, `name`, `version`, `android_version`, `maintainer`, `status`, `website`
- `data/compatibility.csv`: `device_id`, `rom_id`, `support_level`, `last_verified`

Use stable IDs and keep references valid:

- Every `compatibility.csv` `device_id` must exist in `devices.csv`.
- Every `compatibility.csv` `rom_id` must exist in `roms.csv`.
- Use `active`, `inactive`, or `unverified` for ROM `status`.
- Use `not found` only when a source field is unavailable.
- Include enough source detail in the merge request for maintainers to verify dataset updates.

## Code Contributions

Keep changes scoped to the issue being solved. Follow the existing Streamlit and test patterns in the repository, and add or update tests when behavior changes.

Before opening a merge request, verify:

```bash
python -m py_compile app.py tests/test_app.py
.venv/bin/pytest
```

## Merge Requests

Use `feature/rom-compatibility-advisor` as the integration branch for project merge requests. Push validated work there even when the work started on another local branch.

Open a merge request with:

- A concise summary of the change.
- The issue number, if applicable.
- The validation commands you ran.
- Notes about dataset sources for any data changes.
- Confirmation that `DATA_ADDITION_MANUAL.md` was followed for database updates.

## Reporting Bugs

Open an issue at:

https://code.swecha.org/mobile-freedom/custom-rom/-/issues

Include reproduction steps, expected behavior, actual behavior, and relevant environment details.
