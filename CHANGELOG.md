# Changelog

All notable changes to this project will be documented in this file.

This project uses app versions to track user-facing Streamlit application changes.

## [Unreleased]

## [v1.0.0] - 2026-07-14

### Added

- Populated `data/roms.csv` with normalized ROM metadata from requested public sources.
- Enriched ROM metadata by checking available project websites and filling high-confidence maintainer, website, Android version, version, and status fields.
- Added production device, ROM, and compatibility lookup data.
- Added ROM activity filters and colored activity badges.
- Added compliance documentation, repository health files, CI configuration, and spec-kit scaffolding.
- Added `DATA_ADDITION_MANUAL.md` and in-app contribution wiki access for database updates.
- Added the Swecha logo asset under `assets/`.

### Changed

- Removed compatibility notes from the dataset schema.
- Removed duplicate `CONTRIBUTION.md` in favor of standard `CONTRIBUTING.md`.

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
