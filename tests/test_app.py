import pandas as pd

from app import (
    COMPATIBILITY_COLUMNS,
    DEVICE_COLUMNS,
    ROM_COLUMNS,
    build_catalog,
    device_label,
    filter_device_options,
    load_data,
    validate_data,
)


def test_sample_data_matches_required_schema():
    devices, roms, compatibility = load_data()

    assert DEVICE_COLUMNS.issubset(devices.columns)
    assert ROM_COLUMNS.issubset(roms.columns)
    assert COMPATIBILITY_COLUMNS.issubset(compatibility.columns)
    assert validate_data(devices, roms, compatibility) == []


def test_validate_data_reports_missing_columns():
    devices, roms, compatibility = load_data()
    invalid_devices = devices.drop(columns=["codename", "chipset"])

    errors = validate_data(invalid_devices, roms, compatibility)

    assert errors == ["devices.csv: chipset, codename"]


def test_build_catalog_joins_devices_roms_and_compatibility():
    devices, roms, compatibility = load_data()

    catalog = build_catalog(devices, roms, compatibility)
    pixel_graphene = catalog[
        (catalog["device_id"] == "pixel_7")
        & (catalog["rom_id"] == "grapheneos_2024")
    ].iloc[0]

    assert len(catalog) == len(compatibility)
    assert pixel_graphene["brand"] == "Google"
    assert pixel_graphene["device"] == "Pixel 7"
    assert pixel_graphene["name"] == "GrapheneOS"
    assert pixel_graphene["support_level"] == "Stable"


def test_filter_device_options_searches_multiple_fields_case_insensitively():
    devices, _, _ = load_data()

    by_codename = filter_device_options(devices, "PANTHER")
    by_chipset = filter_device_options(devices, "snapdragon 870")
    by_brand = filter_device_options(devices, "nothing")

    assert by_codename["device_id"].tolist() == ["pixel_7"]
    assert by_chipset["device_id"].tolist() == ["poco_f3"]
    assert by_brand["device_id"].tolist() == ["nothing_phone_1"]


def test_filter_device_options_empty_query_returns_all_devices_sorted():
    devices, _, _ = load_data()

    results = filter_device_options(devices, "")
    labels = [device_label(row) for _, row in results.iterrows()]

    assert len(results) == len(devices)
    assert labels[0] == "Google Pixel 6a G1AZG (bluejay)"
    assert labels[-1] == "Xiaomi Redmi Note 10 Pro M2101K6G (sweet)"


def test_validate_data_accepts_minimal_valid_frames():
    devices = pd.DataFrame(columns=sorted(DEVICE_COLUMNS))
    roms = pd.DataFrame(columns=sorted(ROM_COLUMNS))
    compatibility = pd.DataFrame(columns=sorted(COMPATIBILITY_COLUMNS))

    assert validate_data(devices, roms, compatibility) == []
