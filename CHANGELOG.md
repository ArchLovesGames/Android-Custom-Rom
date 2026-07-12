# Changelog

All notable changes to this project will be documented in this file.

This project uses app versions to track user-facing Streamlit application changes. The MVP is versioned as `v0.0.1`; the app should move to `v1.0.0` after the production dataset is ready and the app is deployed.

## [Unreleased]

### Added

- Populated `data/roms.csv` with normalized ROM metadata from requested public sources.

## [v0.0.1] - 2026-07-12

### Added

- Built the base Streamlit MVP for Android custom ROM compatibility lookup.
- Added device-to-ROM lookup.
- Added ROM-to-device reverse lookup.
- Added guided device selection by device type, brand, device, and model.
- Added direct device search with a minimum query length and limited visible results for larger datasets.
- Added CSV format templates for devices, ROMs, and compatibility mappings.
- Added dataset schema validation and user-facing messages for missing production data.
- Added pytest coverage and local pre-commit checks.
