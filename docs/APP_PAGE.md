# App Page Documentation

## Purpose

`app.py` renders the Android Custom ROM Finder Streamlit page. It loads CSV data, validates schemas, and lets users search compatibility data by device or ROM.

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

## Lookup Modes

The app uses a segmented control with two modes:

- `Device to ROMs`: calls `device_lookup()`
- `ROM to devices`: calls `rom_lookup()`

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
