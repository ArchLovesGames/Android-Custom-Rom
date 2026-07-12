from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).parent / "data"
DEVICES_FILE = DATA_DIR / "devices.csv"
ROMS_FILE = DATA_DIR / "roms.csv"
COMPATIBILITY_FILE = DATA_DIR / "compatibility.csv"

DEVICE_COLUMNS = {
    "device_id",
    "device_type",
    "brand",
    "device",
    "model",
    "android_version",
    "chipset",
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
    "device_id",
    "rom_id",
    "support_level",
    "notes",
    "last_verified",
}


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def find_missing_columns(
    frame: pd.DataFrame, required_columns: set[str], file_name: str
) -> list[str]:
    missing_columns = sorted(required_columns - set(frame.columns))
    return [f"{file_name}: {', '.join(missing_columns)}"] if missing_columns else []


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    devices = load_csv(DEVICES_FILE)
    roms = load_csv(ROMS_FILE)
    compatibility = load_csv(COMPATIBILITY_FILE)

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
    if not errors:
        if devices.empty:
            errors.append("devices.csv: at least one device row is required")
        if roms.empty:
            errors.append("roms.csv: at least one ROM row is required")

        unknown_devices = sorted(
            set(compatibility["device_id"]) - set(devices["device_id"])
        )
        unknown_roms = sorted(set(compatibility["rom_id"]) - set(roms["rom_id"]))

        if unknown_devices:
            errors.append(
                "compatibility.csv: unknown device_id value(s): "
                + ", ".join(unknown_devices)
            )
        if unknown_roms:
            errors.append(
                "compatibility.csv: unknown rom_id value(s): " + ", ".join(unknown_roms)
            )
    return errors


def build_catalog(
    devices: pd.DataFrame, roms: pd.DataFrame, compatibility: pd.DataFrame
) -> pd.DataFrame:
    catalog = compatibility.merge(devices, on="device_id", how="left").merge(
        roms,
        on="rom_id",
        how="left",
        suffixes=("_device", "_rom"),
    )
    return catalog.sort_values(
        ["device_type", "brand", "device", "model", "name"]
    ).reset_index(drop=True)


def device_label(row: pd.Series) -> str:
    return f"{row['device_type']} - {row['brand']} {row['device']} {row['model']}"


def rom_label(row: pd.Series) -> str:
    return f"{row['name']} {row['version']} - Android {row['android_version']}"


def filter_device_options(devices: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return devices.sort_values(["device_type", "brand", "device", "model"])

    searchable = devices[
        ["device_type", "brand", "device", "model", "chipset", "android_version"]
    ].agg(" ".join, axis=1)
    return devices[
        searchable.str.contains(query, case=False, na=False, regex=False)
    ].sort_values(["device_type", "brand", "device", "model"])


def show_rom_results(results: pd.DataFrame) -> None:
    if results.empty:
        st.warning("No compatible ROMs were found for the selected device.")
        return

    display = results[
        [
            "name",
            "version",
            "android_version_rom",
            "status",
            "maintainer",
            "support_level",
            "notes",
            "last_verified",
            "website",
        ]
    ].rename(
        columns={
            "name": "ROM",
            "version": "Version",
            "android_version_rom": "Android",
            "status": "Status",
            "maintainer": "Maintainer",
            "support_level": "Support",
            "notes": "Notes",
            "last_verified": "Last verified",
            "website": "Website",
        }
    )
    st.dataframe(display, use_container_width=True, hide_index=True)


def show_device_results(results: pd.DataFrame) -> None:
    if results.empty:
        st.warning("No compatible devices were found for the selected ROM.")
        return

    display = results[
        [
            "brand",
            "device_type",
            "device",
            "model",
            "android_version_device",
            "chipset",
            "support_level",
            "notes",
            "last_verified",
        ]
    ].rename(
        columns={
            "brand": "Brand",
            "device_type": "Type",
            "device": "Device",
            "model": "Model",
            "android_version_device": "Device Android",
            "chipset": "Chipset",
            "support_level": "Support",
            "notes": "Notes",
            "last_verified": "Last verified",
        }
    )
    st.dataframe(display, use_container_width=True, hide_index=True)


def device_lookup(devices: pd.DataFrame, catalog: pd.DataFrame) -> None:
    st.subheader("Find compatible ROMs")

    lookup_method = st.radio(
        "Device lookup method",
        ["Guided selection", "Direct search"],
        key="device_lookup_method",
    )

    selected_device_id = ""

    if lookup_method == "Guided selection":
        device_types = sorted(devices["device_type"].unique())
        if not device_types:
            st.warning("No device types are available.")
            return

        device_type = st.selectbox(
            "Device type", device_types, key="device_type"
        )
        type_devices = devices[devices["device_type"] == device_type]
        brands = sorted(type_devices["brand"].unique())
        if not brands:
            st.warning("No brands are available for the selected device type.")
            return

        brand = st.selectbox("Brand", brands, key="brand")
        brand_devices = type_devices[type_devices["brand"] == brand].sort_values(
            ["device", "model"]
        )
        device_names = sorted(brand_devices["device"].unique())
        if not device_names:
            st.warning("No devices are available for the selected brand.")
            return

        device = st.selectbox(
            "Device", device_names, key="device"
        )
        model_options = brand_devices[brand_devices["device"] == device].sort_values("model")
        if model_options.empty:
            st.warning("No models are available for the selected device.")
            return

        model_label_map = {
            f"{row['model']} [{row['device_id']}]": row["device_id"]
            for _, row in model_options.iterrows()
        }
        model = st.selectbox("Model", list(model_label_map.keys()), key="model")
        selected_device_id = model_label_map[model]
    else:
        search_query = st.text_input(
            "Search by type, brand, device, model, chipset, or Android version",
            placeholder="Example: Phone, Pixel 7, OnePlus, Snapdragon",
            key="device_search_query",
        ).strip()
        matching_devices = filter_device_options(devices, search_query)

        if matching_devices.empty:
            st.warning("No devices match that search.")
            return

        search_options = {
            device_label(row): row["device_id"] for _, row in matching_devices.iterrows()
        }
        selected_label = st.selectbox(
            "Matching devices",
            list(search_options.keys()),
            key="matching_device",
        )
        selected_device_id = search_options[selected_label]

    if not selected_device_id:
        st.info("Select a device to view compatible ROMs.")
        return

    selected = devices[devices["device_id"] == selected_device_id].iloc[0]
    st.caption(
        f"Selected: {selected['device_type']} - {selected['brand']} "
        f"{selected['device']} {selected['model']}"
    )

    results = catalog[catalog["device_id"] == selected_device_id].sort_values(
        ["support_level", "name"]
    )
    show_rom_results(results)


def rom_lookup(roms: pd.DataFrame, catalog: pd.DataFrame) -> None:
    st.subheader("Find compatible devices")

    rom_options = {
        rom_label(row): row["rom_id"] for _, row in roms.sort_values("name").iterrows()
    }
    if not rom_options:
        st.warning("No ROMs are available.")
        return

    selected_label = st.selectbox(
        "ROM",
        list(rom_options.keys()),
        key="rom",
    )

    selected_rom_id = rom_options[selected_label]
    results = catalog[catalog["rom_id"] == selected_rom_id].sort_values(
        ["device_type", "brand", "device", "model"]
    )
    show_device_results(results)


def main() -> None:
    st.set_page_config(
        page_title="Android Custom ROM Finder",
        layout="wide",
    )
    st.title("Android Custom ROM Finder")
    st.write(
        "Search sample compatibility data by device or ROM. Replace the CSV files "
        "in `data/` with the production datasets when they are ready."
    )

    devices, roms, compatibility = load_data()
    data_errors = validate_data(devices, roms, compatibility)
    if data_errors:
        st.error("Dataset schema validation failed.")
        for error in data_errors:
            st.write(f"- {error}")
        return

    catalog = build_catalog(devices, roms, compatibility)

    metric_columns = st.columns(3)
    metric_columns[0].metric("Device types", devices["device_type"].nunique())
    metric_columns[1].metric("Devices", devices["device_id"].nunique())
    metric_columns[2].metric("ROMs", roms["rom_id"].nunique())

    mode = st.radio(
        "Lookup type",
        ["Device to ROMs", "ROM to devices"],
        key="lookup_type",
    )

    if mode == "Device to ROMs":
        device_lookup(devices, catalog)
    else:
        rom_lookup(roms, catalog)


if __name__ == "__main__":
    main()
