# Android Custom ROM

[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-in%20development-blue)](https://code.swecha.org/mobile-freedom/custom-rom)

Android Custom ROM is a Streamlit web app that helps users discover custom Android ROMs for their devices. Users can either select a device to view compatible ROMs or select a ROM to find supported devices.

The project is for Android enthusiasts, contributors, and maintainers who need a simple way to explore ROM compatibility from a structured dataset.

## Features

- Search custom ROMs by Android device
- Search compatible devices by custom ROM
- Dataset-driven results
- Streamlit-based web interface
- Simple filtering workflow for ROM and device compatibility

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
pytest
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

Current sample data lives in:

- `data/devices.csv`
- `data/roms.csv`
- `data/compatibility.csv`

Expected columns:

- `devices.csv`: `device_id`, `device_type`, `brand`, `device`, `model`, `android_version`, `chipset`
- `roms.csv`: `rom_id`, `name`, `version`, `android_version`, `maintainer`, `status`, `website`
- `compatibility.csv`: `device_id`, `rom_id`, `support_level`, `notes`, `last_verified`

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

- Replace sample data with the production ROM compatibility dataset
- Add screenshots of the app
- Add filtering improvements for device brand, model, Android version, and ROM name
- Add tests for dataset parsing and filtering logic

## Screenshots

Screenshots will be added after the Streamlit UI is available.

## FAQ

### How do I find ROMs for my device?

Select or search for your device in the app. The app will display ROMs marked as compatible with that device in the dataset.

### How do I find devices supported by a ROM?

Select or search for a ROM in the app. The app will display devices marked as compatible with that ROM in the dataset.

### Can I add a new device or ROM?

Yes. Contributions should update the compatibility dataset and include enough detail for maintainers to verify the entry.

## Contributing

Contributions are welcome.

To get started:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test the Streamlit app locally.
5. Open a merge request with a clear description of the change.

Please keep dataset updates accurate and verifiable. If a `CONTRIBUTING.md` or code of conduct is added later, follow the process documented there.

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

No license file is currently present in this repository. Add a license before publishing or distributing the project as open source.
