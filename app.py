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
    "device_id",
    "rom_id",
    "support_level",
    "notes",
    "last_verified",
}
DIRECT_SEARCH_MIN_CHARS = 2
DIRECT_SEARCH_RESULT_LIMIT = 100
ROM_SEARCH_RESULT_LIMIT = 100
RESULT_DISPLAY_LIMIT = 50
NOTE_PREVIEW_CHARS = 180


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
    if not errors and not devices.empty and not roms.empty and not compatibility.empty:
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


def has_dataset_rows(
    devices: pd.DataFrame, roms: pd.DataFrame, compatibility: pd.DataFrame
) -> bool:
    return not devices.empty and not roms.empty and not compatibility.empty


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


def build_device_rom_results(
    roms: pd.DataFrame, compatibility: pd.DataFrame, selected_device_id: str
) -> pd.DataFrame:
    device_rows = compatibility[compatibility["device_id"] == selected_device_id]
    if device_rows.empty:
        return pd.DataFrame()

    return (
        device_rows.merge(roms, on="rom_id", how="left")
        .sort_values(["support_level", "name"])
        .reset_index(drop=True)
    )


def build_rom_device_results(
    devices: pd.DataFrame, compatibility: pd.DataFrame, selected_rom_id: str
) -> pd.DataFrame:
    rom_rows = compatibility[compatibility["rom_id"] == selected_rom_id]
    if rom_rows.empty:
        return pd.DataFrame()

    return (
        rom_rows.merge(devices, on="device_id", how="left")
        .sort_values(["device_type", "brand", "device", "model"])
        .reset_index(drop=True)
    )


def device_label(row: pd.Series) -> str:
    return (
        f"{row['device_type']} - {row['brand']} {row['device']} "
        f"{row['model']} [{row['device_id']}]"
    )


def rom_label(row: pd.Series) -> str:
    return f"{row['name']} {row['version']} - Android {row['android_version']}"


def truncate_text(value: str, limit: int = NOTE_PREVIEW_CHARS) -> str:
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."


def filter_device_options(devices: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return devices.iloc[0:0]

    searchable = devices[["device_type", "brand", "device", "model"]].agg(" ".join, axis=1)
    return devices[
        searchable.str.contains(query, case=False, na=False, regex=False)
    ].sort_values(["device_type", "brand", "device", "model"])


def filter_rom_options(roms: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return roms.iloc[0:0]

    searchable = roms[
        ["name", "version", "android_version", "maintainer", "status"]
    ].agg(" ".join, axis=1)
    return roms[
        searchable.str.contains(query, case=False, na=False, regex=False)
    ].sort_values(["name", "version"])


def show_limited_results(display: pd.DataFrame, total_rows: int) -> None:
    if total_rows > RESULT_DISPLAY_LIMIT:
        st.caption(
            f"Showing the first {RESULT_DISPLAY_LIMIT} of {total_rows} rows. "
            "Use a more specific search to narrow results."
        )

    for row in display.head(RESULT_DISPLAY_LIMIT).to_dict("records"):
        title_label, title_value = next(iter(row.items()))
        with st.container(border=True):
            st.markdown(f"**{title_label}:** {title_value}")
            for label, value in row.items():
                if label == title_label or label == "Notes":
                    continue
                st.caption(f"{label}: {value}")
            if row.get("Notes"):
                st.write(row["Notes"])


def show_rom_results(results: pd.DataFrame) -> None:
    if results.empty:
        st.warning("No compatible ROMs were found for the selected device.")
        return

    display = results[
        [
            "name",
            "version",
            "android_version",
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
            "android_version": "Android",
            "status": "Status",
            "maintainer": "Maintainer",
            "support_level": "Support",
            "notes": "Notes",
            "last_verified": "Last verified",
            "website": "Website",
        }
    )
    display["Notes"] = display["Notes"].map(truncate_text)
    show_limited_results(display, len(results))


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
            "support_level": "Support",
            "notes": "Notes",
            "last_verified": "Last verified",
        }
    )
    display["Notes"] = display["Notes"].map(truncate_text)
    show_limited_results(display, len(results))


def show_selected_device_roms(
    devices: pd.DataFrame,
    roms: pd.DataFrame,
    compatibility: pd.DataFrame,
    selected_device_id: str,
) -> None:
    if not selected_device_id:
        st.info("Select a device to view compatible ROMs.")
        return

    selected = devices[devices["device_id"] == selected_device_id].iloc[0]
    st.caption(
        f"Selected: {selected['device_type']} - {selected['brand']} "
        f"{selected['device']} {selected['model']}"
    )

    results = build_device_rom_results(roms, compatibility, selected_device_id)
    show_rom_results(results)


def direct_device_lookup(
    devices: pd.DataFrame, roms: pd.DataFrame, compatibility: pd.DataFrame
) -> None:
    with st.form("device_search_form", border=False):
        search_value = st.text_input(
            "Search by type, brand, device, or model",
            placeholder="Example: Phone, Pixel 7, OnePlus",
            key="device_search_input",
        ).strip()
        submitted = st.form_submit_button("Search devices")

    if submitted:
        st.session_state["device_search_query"] = search_value

    search_query = st.session_state.get("device_search_query", "").strip()

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

    search_options = {
        device_label(row): row["device_id"] for _, row in visible_matches.iterrows()
    }
    selected_label = st.selectbox(
        "Matching devices",
        list(search_options.keys()),
        key=f"matching_device_{search_query}",
    )

    show_selected_device_roms(devices, roms, compatibility, search_options[selected_label])


def device_lookup(
    devices: pd.DataFrame, roms: pd.DataFrame, compatibility: pd.DataFrame
) -> None:
    st.subheader("Find compatible ROMs")
    direct_device_lookup(devices, roms, compatibility)


def rom_lookup(
    devices: pd.DataFrame, roms: pd.DataFrame, compatibility: pd.DataFrame
) -> None:
    st.subheader("Find compatible devices")

    with st.form("rom_search_form", border=False):
        search_value = st.text_input(
            "Search ROMs",
            placeholder="Example: LineageOS, Android 16, recovery",
            key="rom_search_input",
        ).strip()
        submitted = st.form_submit_button("Search ROMs")

    if submitted:
        st.session_state["rom_search_query"] = search_value

    search_query = st.session_state.get("rom_search_query", "").strip()

    if len(search_query) < DIRECT_SEARCH_MIN_CHARS:
        st.info(f"Enter at least {DIRECT_SEARCH_MIN_CHARS} characters to search ROMs.")
        return

    matching_roms = filter_rom_options(roms, search_query)
    if matching_roms.empty:
        st.warning("No ROMs match that search.")
        return

    visible_roms = matching_roms.head(ROM_SEARCH_RESULT_LIMIT)
    if len(matching_roms) > ROM_SEARCH_RESULT_LIMIT:
        st.caption(
            f"Showing the first {ROM_SEARCH_RESULT_LIMIT} of "
            f"{len(matching_roms)} matches. Refine the search to narrow results."
        )

    rom_options = {
        rom_label(row): row["rom_id"] for _, row in visible_roms.iterrows()
    }
    selected_label = st.selectbox(
        "ROM",
        list(rom_options.keys()),
        key=f"rom_{search_query}",
    )

    selected_rom_id = rom_options[selected_label]
    results = build_rom_device_results(devices, compatibility, selected_rom_id)
    show_device_results(results)


def main() -> None:
    st.set_page_config(
        page_title="Android Custom ROM Finder",
        layout="wide",
    )
    st.title("Android Custom ROM Finder")
    st.write(
        "Search compatibility data by device or ROM from the curated CSV datasets."
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

    metric_columns = st.columns(3)
    metric_columns[0].metric("Device types", devices["device_type"].nunique())
    metric_columns[1].metric("Devices", devices["device_id"].nunique())
    metric_columns[2].metric("ROMs", roms["rom_id"].nunique())

    lookup_mode = st.segmented_control(
        "Lookup mode",
        ["Device to ROMs", "ROM to devices"],
        default="Device to ROMs",
    )
    if lookup_mode == "Device to ROMs":
        device_lookup(devices, roms, compatibility)
    elif lookup_mode == "ROM to devices":
        rom_lookup(devices, roms, compatibility)


if __name__ == "__main__":
    main()
