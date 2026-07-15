# App Page Documentation

## Purpose

`app.py` renders the Android Custom ROM Finder Streamlit page. It loads CSV data, validates schemas, and lets users search compatibility data by device or ROM.

Live deployment: https://custom-rom-android-finder.streamlit.app/

The deployed Streamlit app tracks GitHub `main` from:

https://github.com/ArchLovesGames/Android-Custom-Rom

## Container Deployment

The app can run on Coolify through the checked-in `Dockerfile`.

Container runtime details:

- Startup script: `scripts/start-streamlit.sh`
- Default port: `8501`
- Dynamic port support: `PORT`
- Bind address: `0.0.0.0`
- Health endpoint: `/_stcore/health`

Use Coolify's Dockerfile build pack and set the exposed application port to
`8501`, unless the environment injects a different `PORT` value.

## Assets

- `assets/swecha-logo.png`: sidebar branding image
- `assets/README.md`: asset attribution and usage notes

## Device-Type Icons

Device-type icons are configured in `DEVICE_TYPE_ICONS` in `app.py`.

Current mappings:

- `phone`: 📱
- `tablet`: ▣
- `sbc`: 🔌
- `tv`: 📺
- `computer`: 🖥️

Unknown device types use the fallback icon `◆`.

## Sidebar Wiki

`show_data_contribution_wiki()` renders the sidebar contribution area. It includes the Swecha logo, a short database contribution checklist, a link to `DATA_ADDITION_MANUAL.md`, and the issue tracker link.

The sidebar also links back to the live Streamlit deployment.

## Lookup Modes

The app uses a segmented control with two modes:

- `Device to ROMs`: calls `device_lookup()`
- `ROM to devices`: calls `rom_lookup()`

## Browser Device Detection

The `Device to ROMs` mode first renders a browser-side detection panel. It uses
an inline Streamlit Custom Component v2 bridge to collect Web API signals from
the visitor's browser and pass them back to Python.

Collected signals include user-agent client hints, legacy user-agent text,
screen dimensions, approximate memory, logical CPU threads, and network class
when the browser supports them. The matcher is conservative: it requires a
strong model, device, or codename match before selecting a dataset device.

See `docs/WEB_DEVICE_DETECTION.md` for the detailed API list and limitations.

## Local Device Detection

Exact Android model detection is local-only. When the app runs locally, the
**Detect connected Android device** button uses ADB on the host machine to read
Android `getprop` values from an authorized connected device.

If the detected properties match `data/devices.csv`, the app renders compatible
ROMs for that device. Otherwise, users should continue with the manual selector
flow.

## Validation

Startup validation checks:

- Required columns in devices, ROMs, and compatibility CSV files
- Unknown `device_id` references in compatibility rows
- Unknown `rom_id` references in compatibility rows

Validation errors stop the app before lookup controls render.

## Tests

Relevant test coverage lives in `tests/test_app.py`:

- Dataset schema validation
- Search helpers
- Join helpers
- Activity status filtering
- Device-type icon labels
- Initial Streamlit render behavior
