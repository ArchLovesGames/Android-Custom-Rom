# User Manual

## Overview

Android Custom ROM Finder helps users search a curated compatibility dataset by device or by ROM. It is intended for Android enthusiasts, maintainers, and contributors who need a quick way to inspect ROM support.

Live app: https://custom-rom-android-finder.streamlit.app/

## Start the App

Use the live app or run it locally. To run locally, install dependencies and run:

```bash
streamlit run app.py
```

The app opens in a browser and displays dataset counts for device types, devices, and ROMs.

The sidebar includes a **Contribute data** section with a link to the database contribution guide and issue tracker.

## Find ROMs for a Device

1. Select `Device to ROMs` in the lookup mode control.
2. Review the browser device detection panel. If the browser exposes a confident
   model hint, compatible ROMs appear automatically.
3. If no automatic match is found, adjust the type, brand, or device selectors.
4. Choose a matching device from the results.
5. Use the ROM activity status filter to show all ROMs, active ROMs, or stale ROMs.

ROM activity is shown with colored badges:

- Green: active
- Red: stale, meaning no recent updates or announcements
- Gray: any other status preserved in the dataset

## Find Devices for a ROM

1. Select `ROM to devices` in the lookup mode control.
2. Enter at least two characters in the ROM search box.
3. Use the activity status filter if needed.
4. Select a ROM from the matching results.
5. Review compatible devices.

## Search Behavior

The hosted app uses browser Web APIs for device hints. These can include
user-agent client hints, screen details, approximate memory, CPU thread count,
and network class. Browsers may hide the exact Android model, so the app only
auto-selects a device when the match is confident.

Manual selectors remain available when browser detection cannot confidently
identify a device.

Selector filtering is case-insensitive at the dataset level. The app limits very
large result sets. Refine the selectors when only the first set of matches is
shown.

## Dataset Validation

At startup, the app validates required CSV columns and checks that compatibility rows reference known devices and ROMs. If validation fails, the app displays the schema or reference errors before rendering lookup results.

## Contribute Data

Open the **Contribute data** sidebar section in the app and read `DATA_ADDITION_MANUAL.md` before editing CSV files. Every data update should include public verification sources.

## Troubleshooting

- If the app reports missing columns, compare the CSV headers with the templates in `data/*_format.csv`.
- If a device or ROM does not appear, check whether it exists in the dataset and whether the search term has at least two characters.
- If compatibility results look wrong, verify that `data/compatibility.csv` uses valid `device_id` and `rom_id` values.
