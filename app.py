from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).parent / "data"
DEVICES_FILE = DATA_DIR / "devices.csv"
ROMS_FILE = DATA_DIR / "roms.csv"
COMPATIBILITY_FILE = DATA_DIR / "compatibility.csv"

DEVICE_COLUMNS = {
    "device_id",
    "brand",
    "device",
    "model",
    "codename",
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


st.set_page_config(
    page_title="Android Custom ROM Finder",
    layout="wide",
)


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def require_columns(frame: pd.DataFrame, required_columns: set[str], file_name: str) -> None:
    missing_columns = sorted(required_columns - set(frame.columns))
    if missing_columns:
        missing = ", ".join(missing_columns)
        st.error(f"{file_name} is missing required column(s): {missing}")
        st.stop()


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    devices = load_csv(DEVICES_FILE)
    roms = load_csv(ROMS_FILE)
    compatibility = load_csv(COMPATIBILITY_FILE)

    require_columns(devices, DEVICE_COLUMNS, DEVICES_FILE.name)
    require_columns(roms, ROM_COLUMNS, ROMS_FILE.name)
    require_columns(compatibility, COMPATIBILITY_COLUMNS, COMPATIBILITY_FILE.name)

    return devices, roms, compatibility


def build_catalog(
    devices: pd.DataFrame, roms: pd.DataFrame, compatibility: pd.DataFrame
) -> pd.DataFrame:
    catalog = compatibility.merge(devices, on="device_id", how="left").merge(
        roms,
        on="rom_id",
        how="left",
        suffixes=("_device", "_rom"),
    )
    return catalog.sort_values(["brand", "device", "model", "name"]).reset_index(drop=True)


def device_label(row: pd.Series) -> str:
    return f"{row['brand']} {row['device']} {row['model']} ({row['codename']})"


def rom_label(row: pd.Series) -> str:
    return f"{row['name']} {row['version']} - Android {row['android_version']}"


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
            "device",
            "model",
            "codename",
            "android_version_device",
            "chipset",
            "support_level",
            "notes",
            "last_verified",
        ]
    ].rename(
        columns={
            "brand": "Brand",
            "device": "Device",
            "model": "Model",
            "codename": "Codename",
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
        horizontal=True,
    )

    selected_device_id = ""

    if lookup_method == "Guided selection":
        brand = st.selectbox("Brand", sorted(devices["brand"].unique()))
        brand_devices = devices[devices["brand"] == brand].sort_values(["device", "model"])

        device = st.selectbox("Device", sorted(brand_devices["device"].unique()))
        model_options = brand_devices[brand_devices["device"] == device].sort_values("model")

        model_label_map = {
            f"{row['model']} ({row['codename']})": row["device_id"]
            for _, row in model_options.iterrows()
        }
        model = st.selectbox("Model", list(model_label_map.keys()))
        selected_device_id = model_label_map[model]
    else:
        search_options = {
            device_label(row): row["device_id"] for _, row in devices.sort_values("brand").iterrows()
        }
        selected_label = st.selectbox(
            "Search by brand, device, model, or codename",
            list(search_options.keys()),
            index=None,
            placeholder="Start typing a device name",
        )
        if selected_label:
            selected_device_id = search_options[selected_label]

    if not selected_device_id:
        st.info("Select a device to view compatible ROMs.")
        return

    selected = devices[devices["device_id"] == selected_device_id].iloc[0]
    st.caption(
        f"Selected: {selected['brand']} {selected['device']} {selected['model']} "
        f"({selected['codename']})"
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
    selected_label = st.selectbox(
        "ROM",
        list(rom_options.keys()),
        index=None,
        placeholder="Start typing a ROM name",
    )

    if not selected_label:
        st.info("Select a ROM to view compatible devices.")
        return

    selected_rom_id = rom_options[selected_label]
    results = catalog[catalog["rom_id"] == selected_rom_id].sort_values(
        ["brand", "device", "model"]
    )
    show_device_results(results)


def main() -> None:
    st.title("Android Custom ROM Finder")
    st.write(
        "Search sample compatibility data by device or ROM. Replace the CSV files "
        "in `data/` with the production datasets when they are ready."
    )

    devices, roms, compatibility = load_data()
    catalog = build_catalog(devices, roms, compatibility)

    metric_columns = st.columns(3)
    metric_columns[0].metric("Brands", devices["brand"].nunique())
    metric_columns[1].metric("Devices", devices["device_id"].nunique())
    metric_columns[2].metric("ROMs", roms["rom_id"].nunique())

    mode = st.radio(
        "Lookup type",
        ["Device to ROMs", "ROM to devices"],
        horizontal=True,
    )

    if mode == "Device to ROMs":
        device_lookup(devices, catalog)
    else:
        rom_lookup(roms, catalog)


if __name__ == "__main__":
    main()
