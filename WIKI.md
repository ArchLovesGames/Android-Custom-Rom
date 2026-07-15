# Android Custom ROM Finder Wiki

## Page Overview

The Streamlit page helps users explore a curated compatibility database for Android custom ROMs.

Live app: https://custom-rom-android-finder.streamlit.app/

The page has three main areas:

- Header and dataset metrics
- Lookup controls
- Sidebar contribution wiki

## Branding

The sidebar displays the Swecha logo from `assets/swecha-logo.png`.

## Dataset Metrics

The top of the page shows:

- Number of device types
- Number of devices
- Number of ROMs

Below the metrics, the page shows device-type icons used by the app:

- 📱 Phone
- ▣ Tablet
- 🔌 SBC
- 📺 TV
- 🖥️ Computer

## Device to ROMs

Use this mode to find ROMs for a device.

1. Select `Device to ROMs`.
2. Review browser device detection. If the browser exposes a confident model
   hint, the app shows matching ROMs automatically.
3. If running locally with ADB, use local device detection for exact Android
   properties.
4. If automatic detection does not match, search by type, brand, or device.
5. Select a matching device.
6. Filter ROM results by activity status if needed.
7. Review ROM metadata, support level, verification date, and website.

## ROM to Devices

Use this mode to find compatible devices for a ROM.

1. Select `ROM to devices`.
2. Search by ROM name, version, Android version, maintainer, or status.
3. Filter ROM search results by activity status if needed.
4. Select a matching ROM.
5. Review compatible devices.

## ROM Activity Badges

ROM status values are displayed as badges:

- Green: active
- Red: stale, meaning no recent updates or announcements
- Gray: other preserved statuses

## Contribute Data

The sidebar includes a `Contribute data` section with:

- Quick database contribution steps
- Link to `DATA_ADDITION_MANUAL.md`
- Link to the issue tracker
- Link to the live Streamlit deployment

Use this section before editing the CSV database.
