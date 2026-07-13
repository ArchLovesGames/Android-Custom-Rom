from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).parent / "data"
DEVICES_FILE = DATA_DIR / "devices.csv"
ROMS_FILE = DATA_DIR / "roms.csv"
COMPATIBILITY_FILE = DATA_DIR / "compatibility.csv"
DEVICES_FORMAT_FILE = DATA_DIR / "devices_format.csv"
ROMS_FORMAT_FILE = DATA_DIR / "roms_format.csv"
COMPATIBILITY_FORMAT_FILE = DATA_DIR / "compatibility_format.csv"

DEVICE_COLUMNS = {
    "device_id",
    "device_type",
    "brand",
    "device",
    "model",
}
ROM_COLUMNS = {
    "rom_id",
    "name",
    "version",
    "android_version",
    "maintainer",
    "status",
    "website",
}
COMPATIBILITY_COLUMNS = {
    "rom_id",
    "rom_name",
    "coverage_level",
    "exact_rows",
    "generic_rows",
    "project_website",
}
DIRECT_SEARCH_MIN_CHARS = 2
DIRECT_SEARCH_RESULT_LIMIT = 100


@st.cache_data
def load_csv(path: Path, mtime_ns: int) -> pd.DataFrame:
    del mtime_ns
    frame = pd.read_csv(path, dtype=str).fillna("")
    frame.columns = frame.columns.str.strip()

    for column in frame.columns:
        frame[column] = frame[column].str.strip()

    return frame


def find_missing_columns(
    frame: pd.DataFrame, required_columns: set[str], file_name: str
) -> list[str]:
    missing_columns = sorted(required_columns - set(frame.columns))
    return [f"{file_name}: {', '.join(missing_columns)}"] if missing_columns else []


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    devices_path = DEVICES_FILE if DEVICES_FILE.exists() else DEVICES_FORMAT_FILE
    roms_path = ROMS_FILE if ROMS_FILE.exists() else ROMS_FORMAT_FILE
    compatibility_path = (
        COMPATIBILITY_FILE if COMPATIBILITY_FILE.exists() else COMPATIBILITY_FORMAT_FILE
    )
    devices = load_csv(devices_path, devices_path.stat().st_mtime_ns)
    roms = load_csv(roms_path, roms_path.stat().st_mtime_ns)
    compatibility = load_csv(
        compatibility_path, compatibility_path.stat().st_mtime_ns
    )

    return devices, roms, compatibility


def validate_data(
    devices: pd.DataFrame, roms: pd.DataFrame, compatibility: pd.DataFrame
) -> list[str]:
    errors = []
    errors.extend(find_missing_columns(devices, DEVICE_COLUMNS, DEVICES_FILE.name))
    errors.extend(find_missing_columns(roms, ROM_COLUMNS, ROMS_FILE.name))
    errors.extend(
        find_missing_columns(
            compatibility, COMPATIBILITY_COLUMNS, COMPATIBILITY_FILE.name
        )
    )
    if not errors and not roms.empty and not compatibility.empty:
        unknown_roms = sorted(set(compatibility["rom_id"]) - set(roms["rom_id"]))

        if unknown_roms:
            errors.append(
                "compatibility.csv: unknown rom_id value(s): " + ", ".join(unknown_roms)
            )
    return errors


def has_dataset_rows(
    devices: pd.DataFrame, roms: pd.DataFrame, compatibility: pd.DataFrame
) -> bool:
    return not devices.empty and not roms.empty and not compatibility.empty


def build_catalog(
    devices: pd.DataFrame, roms: pd.DataFrame, compatibility: pd.DataFrame
) -> pd.DataFrame:
    del devices
    catalog = compatibility.merge(
        roms,
        on="rom_id",
        how="left",
        suffixes=("_coverage", ""),
    )
    return catalog.sort_values(["coverage_level", "name"]).reset_index(drop=True)


def device_label(row: pd.Series) -> str:
    return (
        f"{row['device_type']} - {row['brand']} {row['device']} "
        f"{row['model']} [{row['device_id']}]"
    )


def rom_label(row: pd.Series) -> str:
    return f"{row['name']} {row['version']} - Android {row['android_version']}"


def filter_device_options(devices: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return devices.sort_values(["device_type", "brand", "device", "model"])

    searchable = devices[["device_type", "brand", "device", "model"]].agg(" ".join, axis=1)
    return devices[
        searchable.str.contains(query, case=False, na=False, regex=False)
    ].sort_values(["device_type", "brand", "device", "model"])


def show_devices(devices: pd.DataFrame) -> None:
    display = devices[["device_type", "brand", "device", "model", "device_id"]].rename(
        columns={
            "device_type": "Type",
            "brand": "Brand",
            "device": "Device",
            "model": "Model",
            "device_id": "Device ID",
        }
    )
    st.dataframe(display, width="stretch", hide_index=True)


def guided_device_lookup(devices: pd.DataFrame) -> None:
    device_types = sorted(devices["device_type"].unique())
    if not device_types:
        st.warning("No device types are available.")
        return

    device_type = st.selectbox("Device type", device_types, key="device_type")
    type_devices = devices[devices["device_type"] == device_type]
    brands = sorted(type_devices["brand"].unique())
    if not brands:
        st.warning("No brands are available for the selected device type.")
        return

    brand = st.selectbox("Brand", brands, key=f"brand_{device_type}")
    brand_devices = type_devices[type_devices["brand"] == brand].sort_values(
        ["device", "model"]
    )
    device_names = sorted(brand_devices["device"].unique())
    if not device_names:
        st.warning("No devices are available for the selected brand.")
        return

    device = st.selectbox("Device", device_names, key=f"device_{device_type}_{brand}")
    model_options = brand_devices[brand_devices["device"] == device].sort_values("model")
    if model_options.empty:
        st.warning("No models are available for the selected device.")
        return

    model_label_map = {
        f"{row['model']} [{row['device_id']}]": row["device_id"]
        for _, row in model_options.iterrows()
    }
    model = st.selectbox(
        "Model",
        list(model_label_map.keys()),
        key=f"model_{device_type}_{brand}_{device}",
    )

    selected_device_id = model_label_map[model]
    show_devices(devices[devices["device_id"] == selected_device_id])


def direct_device_lookup(devices: pd.DataFrame) -> None:
    search_query = st.text_input(
        "Search by type, brand, device, or model",
        placeholder="Example: Phone, Pixel 7, OnePlus",
        key="device_search_query",
    ).strip()

    if len(search_query) < DIRECT_SEARCH_MIN_CHARS:
        st.info(f"Enter at least {DIRECT_SEARCH_MIN_CHARS} characters to search devices.")
        return

    matching_devices = filter_device_options(devices, search_query)
    if matching_devices.empty:
        st.warning("No devices match that search.")
        return

    visible_matches = matching_devices.head(DIRECT_SEARCH_RESULT_LIMIT)
    if len(matching_devices) > DIRECT_SEARCH_RESULT_LIMIT:
        st.caption(
            f"Showing the first {DIRECT_SEARCH_RESULT_LIMIT} of "
            f"{len(matching_devices)} matches. Refine the search to narrow results."
        )

    show_devices(visible_matches)


def device_lookup(devices: pd.DataFrame) -> None:
    st.subheader("Device directory")

    guided_tab, direct_tab = st.tabs(["Guided selection", "Direct search"])

    with guided_tab:
        guided_device_lookup(devices)

    with direct_tab:
        direct_device_lookup(devices)


def rom_lookup(roms: pd.DataFrame, catalog: pd.DataFrame) -> None:
    del roms
    st.subheader("ROM compatibility coverage")

    if catalog.empty:
        st.warning("No ROM coverage rows are available.")
        return

    coverage_levels = ["All"] + sorted(catalog["coverage_level"].unique())
    selected_level = st.selectbox("Coverage level", coverage_levels, key="coverage_level")
    results = catalog
    if selected_level != "All":
        results = catalog[catalog["coverage_level"] == selected_level]

    display = results[
        [
            "name",
            "version",
            "android_version",
            "status",
            "coverage_level",
            "exact_rows",
            "generic_rows",
            "project_website",
        ]
    ].rename(
        columns={
            "name": "ROM",
            "version": "Version",
            "android_version": "Android",
            "status": "Status",
            "coverage_level": "Coverage",
            "exact_rows": "Exact rows",
            "generic_rows": "Generic rows",
            "project_website": "Project website",
        }
    )
    st.dataframe(display, width="stretch", hide_index=True)


def main() -> None:
    st.set_page_config(
        page_title="Android Custom ROM Finder",
        layout="wide",
    )
    st.title("Android Custom ROM Finder")
    st.write(
        "Search the device directory and review ROM compatibility coverage from "
        "the curated CSV datasets."
    )

    devices, roms, compatibility = load_data()
    data_errors = validate_data(devices, roms, compatibility)
    if data_errors:
        st.error("Dataset schema validation failed.")
        for error in data_errors:
            st.write(f"- {error}")
        return

    if not has_dataset_rows(devices, roms, compatibility):
        st.info(
            "Only CSV format files are present. Add production rows to "
            "`data/devices.csv`, `data/roms.csv`, and `data/compatibility.csv` "
            "to use the lookup app."
        )
        return

    catalog = build_catalog(devices, roms, compatibility)

    metric_columns = st.columns(3)
    metric_columns[0].metric("Device types", devices["device_type"].nunique())
    metric_columns[1].metric("Devices", devices["device_id"].nunique())
    metric_columns[2].metric("ROMs", roms["rom_id"].nunique())

    device_tab, rom_tab = st.tabs(["Devices", "ROM coverage"])

    with device_tab:
        device_lookup(devices)

    with rom_tab:
        rom_lookup(roms, catalog)


if __name__ == "__main__":
    main()
