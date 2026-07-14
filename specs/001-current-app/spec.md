# Android Custom ROM Finder

## Summary

The app lets users search a curated Android custom ROM compatibility dataset by device or ROM.

## User Scenarios

- As a user, I can search for a device and view compatible ROMs.
- As a user, I can search for a ROM and view compatible devices.
- As a user, I can filter ROM results by active or inactive status.

## Requirements

- The app must validate CSV schemas before rendering lookup results.
- Compatibility rows must reference known devices and ROMs.
- Device search must check type, brand, device name, and model.
- ROM search must check name, version, Android version, maintainer, and status.
- Active ROMs must display with a green status badge.
- Inactive ROMs must display with a red status badge.

## Acceptance Criteria

- Given valid CSV files, when the app starts, then lookup controls are available.
- Given an invalid compatibility reference, when the app starts, then validation errors are shown.
- Given a selected device, when the active filter is selected, then only active ROM results are shown.

## Test Plan

- Unit tests cover schema validation, search helpers, joins, and activity filtering.
- Streamlit app tests cover initial render behavior.
- Pre-commit runs lint, format, type, security, dependency audit, dead-code, syntax, and coverage checks.
