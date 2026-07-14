import csv
import html
from collections.abc import Iterable
from pathlib import Path

import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
ASSETS_DIR = Path(__file__).parent / "assets"
SWECHA_LOGO_FILE = ASSETS_DIR / "swecha-logo.svg"
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
    "last_verified",
}
DIRECT_SEARCH_MIN_CHARS = 2
DIRECT_SEARCH_RESULT_LIMIT = 100
ROM_SEARCH_RESULT_LIMIT = 100
RESULT_DISPLAY_LIMIT = 50
ROM_STATUS_FILTER_OPTIONS = ["All", "Active", "Inactive"]
ISSUES_URL = "https://code.swecha.org/mobile-freedom/custom-rom/-/issues"
DATA_ADDITION_MANUAL_URL = (
    "https://code.swecha.org/mobile-freedom/custom-rom/-/blob/compliance/"
    "DATA_ADDITION_MANUAL.md"
)
STATUS_BADGE_STYLES = {
    "active": ("#166534", "#dcfce7", "#86efac"),
    "inactive": ("#991b1b", "#fee2e2", "#fca5a5"),
}

Row = dict[str, str]
Rows = list[Row]


def sort_rows(rows: Iterable[Row], columns: list[str]) -> Rows:
    return sorted(
        rows, key=lambda row: tuple(row.get(column, "") for column in columns)
    )


@st.cache_data
def load_csv(path: Path, mtime_ns: int) -> tuple[str, ...]:
    del mtime_ns
    with path.open(newline="", encoding="utf-8-sig") as file:
        return tuple(file.read().splitlines())


def parse_csv_lines(lines: tuple[str, ...]) -> Rows:
    if not lines:
        return []

    reader = csv.DictReader(lines)
    rows: Rows = []
    for row in reader:
        rows.append({key.strip(): (value or "").strip() for key, value in row.items()})
    if rows:
        return rows
    return [{field.strip(): "" for field in reader.fieldnames or []}]


def load_table(path: Path) -> Rows:
    return parse_csv_lines(load_csv(path, path.stat().st_mtime_ns))


def columns_for(rows: Rows) -> set[str]:
    return set(rows[0]) if rows else set()


def find_missing_columns(
    rows: Rows, required_columns: set[str], file_name: str
) -> list[str]:
    missing_columns = sorted(required_columns - columns_for(rows))
    return [f"{file_name}: {', '.join(missing_columns)}"] if missing_columns else []


@st.cache_data
def load_data() -> tuple[Rows, Rows, Rows]:
    devices_path = DEVICES_FILE if DEVICES_FILE.exists() else DEVICES_FORMAT_FILE
    roms_path = ROMS_FILE if ROMS_FILE.exists() else ROMS_FORMAT_FILE
    compatibility_path = (
        COMPATIBILITY_FILE if COMPATIBILITY_FILE.exists() else COMPATIBILITY_FORMAT_FILE
    )
    return (
        load_table(devices_path),
        load_table(roms_path),
        load_table(compatibility_path),
    )


def validate_data(devices: Rows, roms: Rows, compatibility: Rows) -> list[str]:
    errors = []
    errors.extend(find_missing_columns(devices, DEVICE_COLUMNS, DEVICES_FILE.name))
    errors.extend(find_missing_columns(roms, ROM_COLUMNS, ROMS_FILE.name))
    errors.extend(
        find_missing_columns(
            compatibility, COMPATIBILITY_COLUMNS, COMPATIBILITY_FILE.name
        )
    )
    if not errors and devices and roms and compatibility:
        device_ids = {row["device_id"] for row in devices}
        rom_ids = {row["rom_id"] for row in roms}
        unknown_devices = sorted(
            {row["device_id"] for row in compatibility} - device_ids
        )
        unknown_roms = sorted({row["rom_id"] for row in compatibility} - rom_ids)

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


def has_dataset_rows(devices: Rows, roms: Rows, compatibility: Rows) -> bool:
    return all(
        any(any(value for value in row.values()) for row in rows)
        for rows in (devices, roms, compatibility)
    )


def build_catalog(devices: Rows, roms: Rows, compatibility: Rows) -> Rows:
    device_by_id = {row["device_id"]: row for row in devices}
    rom_by_id = {row["rom_id"]: row for row in roms}
    catalog = []
    for row in compatibility:
        catalog.append(
            {
                **row,
                **device_by_id.get(row["device_id"], {}),
                **rom_by_id.get(row["rom_id"], {}),
            }
        )
    return sort_rows(catalog, ["device_type", "brand", "device", "model", "name"])


def build_device_rom_results(
    roms: Rows, compatibility: Rows, selected_device_id: str
) -> Rows:
    rom_by_id = {row["rom_id"]: row for row in roms}
    results = []
    for row in compatibility:
        if row["device_id"] == selected_device_id:
            results.append({**row, **rom_by_id.get(row["rom_id"], {})})
    return sort_rows(results, ["support_level", "name"])


def build_rom_device_results(
    devices: Rows, compatibility: Rows, selected_rom_id: str
) -> Rows:
    device_by_id = {row["device_id"]: row for row in devices}
    results = []
    for row in compatibility:
        if row["rom_id"] == selected_rom_id:
            results.append({**row, **device_by_id.get(row["device_id"], {})})
    return sort_rows(results, ["device_type", "brand", "device", "model"])


def device_label(row: Row) -> str:
    return (
        f"{row['device_type']} - {row['brand']} {row['device']} "
        f"{row['model']} [{row['device_id']}]"
    )


def rom_label(row: Row) -> str:
    return f"{row['name']} {row['version']} - Android {row['android_version']}"


def filter_roms_by_status(roms: Rows, selected_status: str) -> Rows:
    if selected_status == "All":
        return roms
    status = selected_status.casefold()
    return [row for row in roms if row["status"].casefold() == status]


def status_badge_html(status: str) -> str:
    normalized_status = status.casefold()
    color, background, border = STATUS_BADGE_STYLES.get(
        normalized_status, ("#374151", "#f3f4f6", "#d1d5db")
    )
    return (
        '<span style="'
        "display:inline-block;"
        "padding:0.125rem 0.5rem;"
        "border-radius:0.25rem;"
        f"border:1px solid {border};"
        f"background:{background};"
        f"color:{color};"
        "font-size:0.875rem;"
        "font-weight:600;"
        "line-height:1.25rem;"
        '">'
        f"{html.escape(status.title())}"
        "</span>"
    )


def show_data_contribution_wiki() -> None:
    if SWECHA_LOGO_FILE.exists():
        st.sidebar.image(str(SWECHA_LOGO_FILE), width=150)

    with st.sidebar.expander("Contribute data", expanded=False):
        st.markdown(
            "Help improve the compatibility database by adding verified devices, "
            "ROMs, and compatibility rows."
        )
        st.markdown("**Database wiki**")
        st.markdown("- Add devices in `data/devices.csv`.")
        st.markdown("- Add ROM projects in `data/roms.csv`.")
        st.markdown("- Add verified support in `data/compatibility.csv`.")
        st.markdown(f"- Read the [data addition manual]({DATA_ADDITION_MANUAL_URL})")
        st.markdown(f"- Open a [data issue]({ISSUES_URL})")
        st.caption("Include public sources for every dataset change.")


def filter_device_options(devices: Rows, query: str) -> Rows:
    if not query:
        return []

    query_lower = query.casefold()
    matches = [
        row
        for row in devices
        if query_lower
        in " ".join(
            [row["device_type"], row["brand"], row["device"], row["model"]]
        ).casefold()
    ]
    return sort_rows(matches, ["device_type", "brand", "device", "model"])


def filter_rom_options(roms: Rows, query: str) -> Rows:
    if not query:
        return []

    query_lower = query.casefold()
    matches = [
        row
        for row in roms
        if query_lower
        in " ".join(
            [
                row["name"],
                row["version"],
                row["android_version"],
                row["maintainer"],
                row["status"],
            ]
        ).casefold()
    ]
    return sort_rows(matches, ["name", "version"])


def show_limited_results(display: Rows, total_rows: int) -> None:
    if total_rows > RESULT_DISPLAY_LIMIT:
        st.caption(
            f"Showing the first {RESULT_DISPLAY_LIMIT} of {total_rows} rows. "
            "Use a more specific search to narrow results."
        )

    for row in display[:RESULT_DISPLAY_LIMIT]:
        title_label, title_value = next(iter(row.items()))
        with st.container(border=True):
            st.markdown(f"**{title_label}:** {title_value}")
            for label, value in row.items():
                if label == title_label:
                    continue
                if label == "Status":
                    st.markdown(
                        f"<div>Status: {status_badge_html(value)}</div>",
                        unsafe_allow_html=True,
                    )
                    continue
                st.caption(f"{label}: {value}")


def show_rom_results(results: Rows) -> None:
    if not results:
        st.warning("No compatible ROMs were found for the selected device.")
        return

    display = []
    for row in results:
        display.append(
            {
                "ROM": row["name"],
                "Version": row["version"],
                "Android": row["android_version"],
                "Status": row["status"],
                "Maintainer": row["maintainer"],
                "Support": row["support_level"],
                "Last verified": row["last_verified"],
                "Website": row["website"],
            }
        )
    show_limited_results(display, len(results))


def show_device_results(results: Rows) -> None:
    if not results:
        st.warning("No compatible devices were found for the selected ROM.")
        return

    display = []
    for row in results:
        display.append(
            {
                "Brand": row["brand"],
                "Type": row["device_type"],
                "Device": row["device"],
                "Model": row["model"],
                "Support": row["support_level"],
                "Last verified": row["last_verified"],
            }
        )
    show_limited_results(display, len(results))


def show_selected_device_roms(
    devices: Rows,
    roms: Rows,
    compatibility: Rows,
    selected_device_id: str,
) -> None:
    if not selected_device_id:
        st.info("Select a device to view compatible ROMs.")
        return

    selected = next(row for row in devices if row["device_id"] == selected_device_id)
    st.caption(
        f"Selected: {selected['device_type']} - {selected['brand']} "
        f"{selected['device']} {selected['model']}"
    )

    results = build_device_rom_results(roms, compatibility, selected_device_id)
    status_filter = st.segmented_control(
        "ROM activity status",
        ROM_STATUS_FILTER_OPTIONS,
        default="All",
        key=f"device_rom_status_{selected_device_id}",
    )
    results = filter_roms_by_status(results, status_filter or "All")
    show_rom_results(results)


def direct_device_lookup(devices: Rows, roms: Rows, compatibility: Rows) -> None:
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
        st.info(
            f"Enter at least {DIRECT_SEARCH_MIN_CHARS} characters to search devices."
        )
        return

    matching_devices = filter_device_options(devices, search_query)
    if not matching_devices:
        st.warning("No devices match that search.")
        return

    visible_matches = matching_devices[:DIRECT_SEARCH_RESULT_LIMIT]
    if len(matching_devices) > DIRECT_SEARCH_RESULT_LIMIT:
        st.caption(
            f"Showing the first {DIRECT_SEARCH_RESULT_LIMIT} of "
            f"{len(matching_devices)} matches. Refine the search to narrow results."
        )

    search_options = {device_label(row): row["device_id"] for row in visible_matches}
    selected_label = st.selectbox(
        "Matching devices",
        list(search_options.keys()),
        key=f"matching_device_{search_query}",
    )

    show_selected_device_roms(
        devices, roms, compatibility, search_options[selected_label]
    )


def device_lookup(devices: Rows, roms: Rows, compatibility: Rows) -> None:
    st.subheader("Find compatible ROMs")
    direct_device_lookup(devices, roms, compatibility)


def rom_lookup(devices: Rows, roms: Rows, compatibility: Rows) -> None:
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
    if not matching_roms:
        st.warning("No ROMs match that search.")
        return

    status_filter = st.segmented_control(
        "ROM activity status",
        ROM_STATUS_FILTER_OPTIONS,
        default="All",
        key=f"rom_search_status_{search_query}",
    )
    matching_roms = filter_roms_by_status(matching_roms, status_filter or "All")
    if not matching_roms:
        st.warning("No ROMs match that activity status.")
        return

    visible_roms = matching_roms[:ROM_SEARCH_RESULT_LIMIT]
    if len(matching_roms) > ROM_SEARCH_RESULT_LIMIT:
        st.caption(
            f"Showing the first {ROM_SEARCH_RESULT_LIMIT} of "
            f"{len(matching_roms)} matches. Refine the search to narrow results."
        )

    rom_options = {rom_label(row): row["rom_id"] for row in visible_roms}
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
    show_data_contribution_wiki()

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
    metric_columns[0].metric(
        "Device types", len({row["device_type"] for row in devices})
    )
    metric_columns[1].metric("Devices", len({row["device_id"] for row in devices}))
    metric_columns[2].metric("ROMs", len({row["rom_id"] for row in roms}))

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
