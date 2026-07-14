# Android Custom ROM

[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-in%20development-blue)](https://code.swecha.org/mobile-freedom/custom-rom)

Android Custom ROM is a Streamlit web app that helps users discover custom Android ROMs for their devices. Users can either select a device to view compatible ROMs or select a ROM to find supported devices.

The project is for Android enthusiasts, contributors, and maintainers who need a simple way to explore ROM compatibility from a structured dataset.

## Features

- Search custom ROMs by Android device using direct device search
- Search compatible devices by custom ROM
- Filter ROM results by activity status
- Color-coded ROM activity badges: green for active, red for inactive
- Dataset-driven compatibility results
- Streamlit-based web interface
- Guardrails for large datasets, including minimum search length and result limits

## Tech Stack

- Python
- Streamlit
- Dataset-backed ROM compatibility data

## Installation

Create a virtual environment and install the project dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Locally

Clone the project:

```bash
git clone https://code.swecha.org/mobile-freedom/custom-rom.git
cd custom-rom
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Streamlit app:

```bash
streamlit run app.py
```

## Testing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
.venv/bin/pytest
```

Run pre-commit checks manually:

```bash
pre-commit run --all-files
```

Install the Git hook:

```bash
pre-commit install
```

## Deployment

The app is intended to be hosted on Streamlit. After the app files and dependency list are available, deploy it through Streamlit Community Cloud or another Streamlit-compatible hosting environment.

Typical Streamlit deployment settings:

- Repository: `https://code.swecha.org/mobile-freedom/custom-rom`
- Branch: `main`
- Main file path: `app.py`

## Dataset

The app uses a dataset containing Android devices, custom ROMs, and compatibility relationships. Keep the dataset structured and versioned with the project so the filters can reliably map:

- Device to compatible ROMs
- ROM to compatible devices

CSV format templates live in:

- `data/devices_format.csv`
- `data/roms_format.csv`
- `data/compatibility_format.csv`

Expected columns:

- `devices.csv`: `device_id`, `device_type`, `brand`, `device`, `model`
- `roms.csv`: `rom_id`, `name`, `version`, `android_version`, `maintainer`, `status`, `website`
- `compatibility.csv`: `device_id`, `rom_id`, `support_level`, `last_verified`

The checked-in `*_format.csv` files mirror the production CSV headers. The app trims whitespace from CSV column names and values when loading data. Direct device search requires at least two characters and limits visible results to avoid rendering very large dropdowns.

ROM `status` values currently used by the dataset are `active`, `inactive`, and `unverified`; `not found` is reserved for unavailable source fields. The app exposes `active` and `inactive` as filter options because those are the user-facing activity states. Unknown or unverified status values remain searchable but are not included in the activity filter choices.

The ROM dataset is populated in `data/roms.csv`. It combines available ROM metadata from:

- `devadigax/awesome-android-custom-rom`
- Wikipedia's list of custom Android distributions
- The requested Reddit discussion where ROM names were visible

Fields that were unavailable in the sources are set to `not found`.

Compatibility rows should only reference `device_id` values from `data/devices.csv` and `rom_id` values from `data/roms.csv`. The app validates these relationships at startup and reports unknown references before rendering lookup results.

## Environment Variables

No environment variables are currently required.

If future dataset sources, APIs, or private configuration are added, document the required variables here and keep secrets out of Git.

## Documentation

Project documentation should include:

- Dataset format and required columns
- Steps to update ROM/device compatibility data
- Streamlit deployment notes
- Contribution workflow

## Roadmap

- Add screenshots of the app
- Add documented data-refresh workflow for ROM and compatibility sources
- Add more validation for dataset normalization and source attribution

## Screenshots

Screenshots will be added after the current Streamlit lookup flow is finalized.

## FAQ

### How do I find ROMs for my device?

Select or search for your device in the app. The app will display ROMs marked as compatible with that device in the dataset.

### How do I find devices supported by a ROM?

Select or search for a ROM in the app. The app will display devices marked as compatible with that ROM in the dataset.

### Can I add a new device or ROM?

Yes. Contributions should update the compatibility dataset and include enough detail for maintainers to verify the entry.

### Why does activity filtering only show active and inactive?

The dataset also preserves unverified status values for transparency, but the activity filter is intentionally limited to confirmed active and inactive ROMs.

## Contributing

Contributions are welcome.

To get started:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test the Streamlit app locally.
5. Open a merge request with a clear description of the change.

Please keep dataset updates accurate and verifiable. Follow `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` for the full contribution process and community expectations.

## Authors

- [@archishasingh](https://code.swecha.org/archishasingh)

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Shields.io](https://shields.io/)
- [Awesome README](https://github.com/matiassingers/awesome-readme)
- [Awesome README Templates](https://github.com/Louis3797/awesome-readme-template)
- [How to Write a Good README](https://www.freecodecamp.org/news/how-to-write-a-good-readme-file/)

## Support and Feedback

For bugs, feature requests, or feedback, open an issue in this repository:

https://code.swecha.org/mobile-freedom/custom-rom/-/issues

## License

This project is licensed under the GNU Affero General Public License v3.0. See `LICENSE` for details.
