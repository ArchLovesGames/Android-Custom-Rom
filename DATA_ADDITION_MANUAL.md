# Data Addition Manual

This guide explains how to contribute device, ROM, and compatibility data to Android Custom ROM Finder.

Live app: https://custom-rom-android-finder.streamlit.app/

## Dataset Files

The app reads three production CSV files from `data/`:

- `data/devices.csv`
- `data/roms.csv`
- `data/compatibility.csv`

The matching `*_format.csv` files show the required headers and should stay in sync with the production CSV files.

## Required Columns

### Devices

`data/devices.csv`

```csv
device_id,device_type,brand,device,model
```

Use one row per device model. Keep `device_id` stable, lowercase, and readable, such as `google_pixel_7` or `oneplus_9_pro`.

### ROMs

`data/roms.csv`

```csv
rom_id,name,version,android_version,maintainer,status,website
```

Use one row per ROM project. Keep `rom_id` stable, lowercase, and readable, such as `lineageos` or `grapheneos`.

Allowed `status` values:

- `active`
- `inactive`
- `unverified`

Use `not found` only when a source field is unavailable.

### Compatibility

`data/compatibility.csv`

```csv
device_id,rom_id,support_level,last_verified
```

Every `device_id` must already exist in `data/devices.csv`. Every `rom_id` must already exist in `data/roms.csv`.

Recommended `support_level` values:

- `official`
- `community`
- `gsi_candidate`

Use ISO dates for `last_verified`, for example `2026-07-14`.

## Source Requirements

Every data contribution should include public verification sources in the merge request description. Useful sources include:

- Official ROM device pages
- Project documentation
- Maintainer announcements
- Repository release notes
- Public device trees or build manifests

Avoid unverifiable claims from private chats or screenshots. If a source is unclear, mark the relevant ROM status as `unverified` instead of guessing.

## Add a New Device

1. Add the device to `data/devices.csv`.
2. Confirm the `device_id` is unique.
3. Use the public model name and model code when available.
4. Add compatibility rows only after the ROM relationship is verified.

## Add a New ROM

1. Add the ROM to `data/roms.csv`.
2. Confirm the `rom_id` is unique.
3. Fill `website` with the official project page when available.
4. Use `not found` for unavailable metadata fields.
5. Set `status` to `active`, `inactive`, or `unverified`.

## Add Compatibility Rows

1. Confirm the device exists in `data/devices.csv`.
2. Confirm the ROM exists in `data/roms.csv`.
3. Add the row to `data/compatibility.csv`.
4. Set `support_level` based on the source.
5. Set `last_verified` to the date you checked the source.

## Validate Changes

Run:

```bash
pre-commit run --all-files
```

At minimum, run:

```bash
python -m py_compile app.py tests/test_app.py
.venv/bin/pytest
```

The app validates required columns and unknown compatibility references at startup. Fix any reported CSV errors before opening a merge request.

## Merge Request Checklist

- [ ] CSV headers match the format templates.
- [ ] New IDs are stable and unique.
- [ ] Compatibility rows reference existing devices and ROMs.
- [ ] Public verification sources are listed in the merge request.
- [ ] Tests and pre-commit checks pass.
