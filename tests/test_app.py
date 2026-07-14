import pandas as pd
from streamlit.testing.v1 import AppTest

from app import (
    COMPATIBILITY_COLUMNS,
    COMPATIBILITY_FORMAT_FILE,
    COMPATIBILITY_FILE,
    DEVICE_COLUMNS,
    DEVICES_FORMAT_FILE,
    DEVICES_FILE,
    ROM_COLUMNS,
    ROMS_FORMAT_FILE,
    ROMS_FILE,
    build_catalog,
    build_device_rom_results,
    build_rom_device_results,
    device_label,
    filter_device_options,
    filter_rom_options,
    has_dataset_rows,
    load_data,
    validate_data,
)


def sample_frames():
    devices = pd.DataFrame(
        [
            {
                "device_id": "pixel_7",
                "device_type": "Phone",
                "brand": "Google",
                "device": "Pixel 7",
                "model": "GVU6C",
            },
            {
                "device_id": "poco_f3",
                "device_type": "Phone",
                "brand": "Xiaomi",
                "device": "POCO F3",
                "model": "M2012K11AG",
            },
            {
                "device_id": "nothing_phone_1",
                "device_type": "Phone",
                "brand": "Nothing",
                "device": "Phone 1",
                "model": "A063",
            },
        ]
    )
    roms = pd.DataFrame(
        [
            {
                "rom_id": "lineageos_21",
                "name": "LineageOS",
                "version": "21",
                "android_version": "14",
                "maintainer": "LineageOS Team",
                "status": "Official",
                "website": "https://lineageos.org/",
            },
            {
                "rom_id": "grapheneos_2024",
                "name": "GrapheneOS",
                "version": "2024",
                "android_version": "14",
                "maintainer": "GrapheneOS Team",
                "status": "Official",
                "website": "https://grapheneos.org/",
            },
        ]
    )
    compatibility = pd.DataFrame(
        [
            {
                "device_id": "pixel_7",
                "rom_id": "lineageos_21",
                "support_level": "Official",
                "notes": "Core hardware supported",
                "last_verified": "2026-07-14",
            },
            {
                "device_id": "pixel_7",
                "rom_id": "grapheneos_2024",
                "support_level": "Official",
                "notes": "Officially supported device family",
                "last_verified": "2026-07-14",
            },
            {
                "device_id": "poco_f3",
                "rom_id": "lineageos_21",
                "support_level": "Community",
                "notes": "Community build",
                "last_verified": "2026-07-14",
            },
        ]
    )
    return devices, roms, compatibility


def test_dataset_and_format_files_match_required_schema():
    devices, roms, compatibility = load_data()

    assert DEVICES_FILE.exists()
    assert COMPATIBILITY_FILE.exists()
    assert ROMS_FILE.exists()
    assert DEVICES_FORMAT_FILE.exists()
    assert ROMS_FORMAT_FILE.exists()
    assert COMPATIBILITY_FORMAT_FILE.exists()
    assert DEVICE_COLUMNS.issubset(devices.columns)
    assert ROM_COLUMNS.issubset(roms.columns)
    assert COMPATIBILITY_COLUMNS.issubset(compatibility.columns)
    assert validate_data(devices, roms, compatibility) == []
    assert has_dataset_rows(devices, roms, compatibility)


def test_rom_dataset_is_populated_and_normalized():
    _, roms, _ = load_data()

    assert len(roms) >= 200
    assert roms["rom_id"].is_unique
    assert roms["name"].is_unique
    assert not (roms == "").any().any()
    assert "not found" in set(roms["version"])
    assert "discontinued" not in set(roms["status"])
    assert {"active", "inactive", "not found", "unverified"}.issuperset(
        set(roms["status"])
    )


def test_refined_datasets_drop_sparse_and_unverified_fields():
    devices, _, compatibility = load_data()

    assert {"android_version", "chipset"}.isdisjoint(devices.columns)
    assert "unverified_device_scope" not in set(compatibility["device_id"])
    support_levels = {value.lower() for value in compatibility["support_level"]}
    assert "unverified" not in support_levels
    assert "discontinued" not in support_levels
    assert not (compatibility == "not found").any().any()


def test_validate_data_reports_missing_columns():
    devices, roms, compatibility = sample_frames()
    invalid_devices = devices.drop(columns=["device_type", "model"])

    errors = validate_data(invalid_devices, roms, compatibility)

    assert errors == ["devices.csv: device_type, model"]


def test_build_catalog_joins_devices_roms_and_compatibility():
    devices, roms, compatibility = sample_frames()

    catalog = build_catalog(devices, roms, compatibility)
    pixel_graphene = catalog[
        (catalog["device_id"] == "pixel_7")
        & (catalog["rom_id"] == "grapheneos_2024")
    ].iloc[0]

    assert len(catalog) == len(compatibility)
    assert pixel_graphene["brand"] == "Google"
    assert pixel_graphene["device"] == "Pixel 7"
    assert pixel_graphene["name"] == "GrapheneOS"
    assert pixel_graphene["support_level"] == "Official"


def test_lazy_lookup_helpers_join_only_selected_rows():
    devices, roms, compatibility = sample_frames()

    device_results = build_device_rom_results(roms, compatibility, "pixel_7")
    rom_results = build_rom_device_results(devices, compatibility, "lineageos_21")

    assert device_results["rom_id"].tolist() == [
        "grapheneos_2024",
        "lineageos_21",
    ]
    assert rom_results["device_id"].tolist() == ["pixel_7", "poco_f3"]


def test_filter_device_options_searches_multiple_fields_case_insensitively():
    devices, _, _ = sample_frames()

    by_type = filter_device_options(devices, "PHONE")
    by_model = filter_device_options(devices, "M2012")
    by_brand = filter_device_options(devices, "nothing")

    assert len(by_type) == len(devices)
    assert by_model["device_id"].tolist() == ["poco_f3"]
    assert by_brand["device_id"].tolist() == ["nothing_phone_1"]


def test_filter_rom_options_searches_multiple_fields_case_insensitively():
    _, roms, _ = sample_frames()

    by_name = filter_rom_options(roms, "graphene")
    by_version = filter_rom_options(roms, "21")
    by_status = filter_rom_options(roms, "official")

    assert by_name["rom_id"].tolist() == ["grapheneos_2024"]
    assert by_version["rom_id"].tolist() == ["lineageos_21"]
    assert len(by_status) == len(roms)


def test_filter_device_options_treats_search_as_literal_text():
    devices, _, _ = sample_frames()

    results = filter_device_options(devices, "[")

    assert results.empty


def test_filter_device_options_empty_query_returns_no_rows():
    devices, _, _ = sample_frames()

    results = filter_device_options(devices, "")

    assert results.empty


def test_validate_data_accepts_header_only_format_frames():
    devices = pd.DataFrame(columns=sorted(DEVICE_COLUMNS))
    roms = pd.DataFrame(columns=sorted(ROM_COLUMNS))
    compatibility = pd.DataFrame(columns=sorted(COMPATIBILITY_COLUMNS))

    assert validate_data(devices, roms, compatibility) == []
    assert not has_dataset_rows(devices, roms, compatibility)


def test_validate_data_reports_unknown_compatibility_references():
    devices, roms, compatibility = sample_frames()
    invalid_compatibility = pd.concat(
        [
            compatibility,
            pd.DataFrame(
                [
                    {
                        "device_id": "unknown_device",
                        "rom_id": "unknown_rom",
                        "support_level": "Official",
                        "notes": "Unknown row",
                        "last_verified": "2026-07-14",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    assert validate_data(devices, roms, invalid_compatibility) == [
        "compatibility.csv: unknown device_id value(s): unknown_device",
        "compatibility.csv: unknown rom_id value(s): unknown_rom",
    ]


def test_app_handles_format_only_dataset_without_crashing():
    app = AppTest.from_file("app.py")

    app.run()

    assert not app.exception
    assert app.info


def test_direct_lookup_search_does_not_render_all_devices_by_default():
    app = AppTest.from_file("app.py")

    app.run()

    assert not app.exception
    assert all(selectbox.label != "Matching devices" for selectbox in app.selectbox)
    assert all(selectbox.label != "ROM" for selectbox in app.selectbox)
