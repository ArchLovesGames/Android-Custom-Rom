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
    filter_roms_by_status,
    has_dataset_rows,
    load_data,
    validate_data,
)


def sample_frames():
    devices = [
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
    roms = [
        {
            "rom_id": "lineageos_21",
            "name": "LineageOS",
            "version": "21",
            "android_version": "14",
            "maintainer": "LineageOS Team",
            "status": "active",
            "website": "https://lineageos.org/",
        },
        {
            "rom_id": "grapheneos_2024",
            "name": "GrapheneOS",
            "version": "2024",
            "android_version": "14",
            "maintainer": "GrapheneOS Team",
            "status": "inactive",
            "website": "https://grapheneos.org/",
        },
    ]
    compatibility = [
        {
            "device_id": "pixel_7",
            "rom_id": "lineageos_21",
            "support_level": "Official",
            "last_verified": "2026-07-14",
        },
        {
            "device_id": "pixel_7",
            "rom_id": "grapheneos_2024",
            "support_level": "Official",
            "last_verified": "2026-07-14",
        },
        {
            "device_id": "poco_f3",
            "rom_id": "lineageos_21",
            "support_level": "Community",
            "last_verified": "2026-07-14",
        },
    ]
    return devices, roms, compatibility


def test_dataset_and_format_files_match_required_schema():
    devices, roms, compatibility = load_data()

    assert DEVICES_FILE.exists()
    assert COMPATIBILITY_FILE.exists()
    assert ROMS_FILE.exists()
    assert DEVICES_FORMAT_FILE.exists()
    assert ROMS_FORMAT_FILE.exists()
    assert COMPATIBILITY_FORMAT_FILE.exists()
    assert DEVICE_COLUMNS.issubset(devices[0])
    assert ROM_COLUMNS.issubset(roms[0])
    assert COMPATIBILITY_COLUMNS.issubset(compatibility[0])
    assert validate_data(devices, roms, compatibility) == []
    assert has_dataset_rows(devices, roms, compatibility)


def test_rom_dataset_is_populated_and_normalized():
    _, roms, _ = load_data()

    assert len(roms) >= 200
    assert len({row["rom_id"] for row in roms}) == len(roms)
    assert len({row["name"] for row in roms}) == len(roms)
    assert all(value for row in roms for value in row.values())
    assert "not found" in {row["version"] for row in roms}
    assert "discontinued" not in {row["status"] for row in roms}
    assert {"active", "inactive", "not found", "unverified"}.issuperset(
        {row["status"] for row in roms}
    )


def test_refined_datasets_drop_sparse_and_unverified_fields():
    devices, _, compatibility = load_data()

    assert {"android_version", "chipset"}.isdisjoint(devices[0])
    assert "unverified_device_scope" not in {row["device_id"] for row in compatibility}
    support_levels = {row["support_level"].lower() for row in compatibility}
    assert "unverified" not in support_levels
    assert "discontinued" not in support_levels
    assert all(value != "not found" for row in compatibility for value in row.values())


def test_validate_data_reports_missing_columns():
    devices, roms, compatibility = sample_frames()
    invalid_devices = [
        {key: value for key, value in row.items() if key not in {"device_type", "model"}}
        for row in devices
    ]

    errors = validate_data(invalid_devices, roms, compatibility)

    assert errors == ["devices.csv: device_type, model"]


def test_build_catalog_joins_devices_roms_and_compatibility():
    devices, roms, compatibility = sample_frames()

    catalog = build_catalog(devices, roms, compatibility)
    pixel_graphene = next(
        row
        for row in catalog
        if row["device_id"] == "pixel_7" and row["rom_id"] == "grapheneos_2024"
    )

    assert len(catalog) == len(compatibility)
    assert pixel_graphene["brand"] == "Google"
    assert pixel_graphene["device"] == "Pixel 7"
    assert pixel_graphene["name"] == "GrapheneOS"
    assert pixel_graphene["support_level"] == "Official"


def test_lazy_lookup_helpers_join_only_selected_rows():
    devices, roms, compatibility = sample_frames()

    device_results = build_device_rom_results(roms, compatibility, "pixel_7")
    rom_results = build_rom_device_results(devices, compatibility, "lineageos_21")

    assert [row["rom_id"] for row in device_results] == [
        "grapheneos_2024",
        "lineageos_21",
    ]
    assert [row["device_id"] for row in rom_results] == ["pixel_7", "poco_f3"]


def test_filter_device_options_searches_multiple_fields_case_insensitively():
    devices, _, _ = sample_frames()

    by_type = filter_device_options(devices, "PHONE")
    by_model = filter_device_options(devices, "M2012")
    by_brand = filter_device_options(devices, "nothing")

    assert len(by_type) == len(devices)
    assert [row["device_id"] for row in by_model] == ["poco_f3"]
    assert [row["device_id"] for row in by_brand] == ["nothing_phone_1"]


def test_filter_rom_options_searches_multiple_fields_case_insensitively():
    _, roms, _ = sample_frames()

    by_name = filter_rom_options(roms, "graphene")
    by_version = filter_rom_options(roms, "21")
    by_status = filter_rom_options(roms, "inactive")

    assert [row["rom_id"] for row in by_name] == ["grapheneos_2024"]
    assert [row["rom_id"] for row in by_version] == ["lineageos_21"]
    assert [row["rom_id"] for row in by_status] == ["grapheneos_2024"]


def test_filter_roms_by_status_returns_selected_activity_status():
    _, roms, _ = sample_frames()

    active_roms = filter_roms_by_status(roms, "Active")
    inactive_roms = filter_roms_by_status(roms, "Inactive")
    all_roms = filter_roms_by_status(roms, "All")

    assert [row["rom_id"] for row in active_roms] == ["lineageos_21"]
    assert [row["rom_id"] for row in inactive_roms] == ["grapheneos_2024"]
    assert all_roms == roms


def test_filter_device_options_treats_search_as_literal_text():
    devices, _, _ = sample_frames()

    results = filter_device_options(devices, "[")

    assert not results


def test_filter_device_options_empty_query_returns_no_rows():
    devices, _, _ = sample_frames()

    results = filter_device_options(devices, "")

    assert not results


def test_validate_data_accepts_header_only_format_frames():
    devices = [{column: "" for column in sorted(DEVICE_COLUMNS)}]
    roms = [{column: "" for column in sorted(ROM_COLUMNS)}]
    compatibility = [{column: "" for column in sorted(COMPATIBILITY_COLUMNS)}]

    assert validate_data(devices, roms, compatibility) == []
    assert not has_dataset_rows(devices, roms, compatibility)


def test_validate_data_reports_unknown_compatibility_references():
    devices, roms, compatibility = sample_frames()
    invalid_compatibility = compatibility + [
        {
            "device_id": "unknown_device",
            "rom_id": "unknown_rom",
            "support_level": "Official",
            "last_verified": "2026-07-14",
        }
    ]

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
