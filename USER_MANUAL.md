# User Manual

## Overview

Android Custom ROM Finder helps users search a curated compatibility dataset by device or by ROM. It is intended for Android enthusiasts, maintainers, and contributors who need a quick way to inspect ROM support.

## Start the App

Install dependencies and run:

```bash
streamlit run app.py
```

The app opens in a browser and displays dataset counts for device types, devices, and ROMs.

## Find ROMs for a Device

1. Select `Device to ROMs` in the lookup mode control.
2. Enter at least two characters in the device search box.
3. Choose a matching device from the results.
4. Review compatible ROMs.
5. Use the ROM activity status filter to show all ROMs, active ROMs, or inactive ROMs.

ROM activity is shown with colored badges:

- Green: active
- Red: inactive
- Gray: any other status preserved in the dataset

## Find Devices for a ROM

1. Select `ROM to devices` in the lookup mode control.
2. Enter at least two characters in the ROM search box.
3. Use the activity status filter if needed.
4. Select a ROM from the matching results.
5. Review compatible devices.

## Search Behavior

Search is case-insensitive. Device search checks type, brand, device name, and model. ROM search checks ROM name, version, Android version, maintainer, and status.

The app limits very large result sets. Refine the search text when only the first set of matches is shown.

## Dataset Validation

At startup, the app validates required CSV columns and checks that compatibility rows reference known devices and ROMs. If validation fails, the app displays the schema or reference errors before rendering lookup results.

## Troubleshooting

- If the app reports missing columns, compare the CSV headers with the templates in `data/*_format.csv`.
- If a device or ROM does not appear, check whether it exists in the dataset and whether the search term has at least two characters.
- If compatibility results look wrong, verify that `data/compatibility.csv` uses valid `device_id` and `rom_id` values.
