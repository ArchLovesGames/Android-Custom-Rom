import csv
import html
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any, NamedTuple

import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
ASSETS_DIR = Path(__file__).parent / "assets"
SWECHA_LOGO_FILE = ASSETS_DIR / "swecha-logo.png"
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
ROM_STATUS_FILTER_OPTIONS = ["All", "Active", "Stale"]
ROM_STATUS_FILTER_VALUES = {
    "All": "All",
    "Active": "Active",
    "Stale": "Inactive",
}
ALL_SELECTOR_OPTION = "All"
ISSUES_URL = "https://code.swecha.org/mobile-freedom/custom-rom/-/issues"
LIVE_APP_URL = "https://custom-rom-android-finder.streamlit.app/"
DATA_ADDITION_MANUAL_URL = (
    "https://code.swecha.org/mobile-freedom/custom-rom/-/blob/compliance/"
    "DATA_ADDITION_MANUAL.md"
)
DEVICE_TYPE_ICONS = {
    "computer": "🖥️",
    "phone": "📱",
    "sbc": "🔌",
    "tablet": "▣",
    "tv": "📺",
}
STATUS_BADGE_STYLES = {
    "light": {
        "active": ("#166534", "#dcfce7", "#86efac"),
        "inactive": ("#991b1b", "#fee2e2", "#fca5a5"),
        "default": ("#374151", "#f3f4f6", "#d1d5db"),
    },
    "dark": {
        "active": ("#bbf7d0", "#14532d", "#22c55e"),
        "inactive": ("#fecaca", "#7f1d1d", "#ef4444"),
        "default": ("#f3f4f6", "#1f2937", "#4b5563"),
    },
}
STATUS_DISPLAY_LABELS = {
    "inactive": "Stale",
}

Row = dict[str, str]
Rows = list[Row]
Database = sqlite3.Connection
DataFileSignature = tuple[str, int]
Metadata = dict[str, Any]


class DeviceFilters(NamedTuple):
    """Selected device selector values for SQLite lookup queries."""

    device_type: str = ""
    brand: str = ""
    device: str = ""
    model: str = ""


def sort_rows(rows: Iterable[Row], columns: list[str]) -> Rows:
    return sorted(
        rows, key=lambda row: tuple(row.get(column, "") for column in columns)
    )


def safe_context_value(name: str) -> Any:
    try:
        return getattr(st.context, name)
    except RuntimeError:
        return None


def context_mapping(name: str) -> dict[str, str]:
    value = safe_context_value(name)
    if not value:
        return {}
    return {str(key): str(item) for key, item in dict(value).items()}


def collect_request_metadata() -> Metadata:
    headers = context_mapping("headers")
    cookies = context_mapping("cookies")
    theme = safe_context_value("theme")
    return {
        "url": safe_context_value("url"),
        "ip_address": safe_context_value("ip_address"),
        "locale": safe_context_value("locale"),
        "timezone": safe_context_value("timezone"),
        "timezone_offset": safe_context_value("timezone_offset"),
        "is_embedded": safe_context_value("is_embedded"),
        "theme": {
            "type": getattr(theme, "type", None),
            "primary_color": getattr(theme, "primaryColor", None),
            "background_color": getattr(theme, "backgroundColor", None),
            "secondary_background_color": getattr(
                theme, "secondaryBackgroundColor", None
            ),
            "text_color": getattr(theme, "textColor", None),
        },
        "headers": headers,
        "cookies": cookies,
        "selected_header_fields": {
            "user-agent": headers.get("user-agent", ""),
            "host": headers.get("host", ""),
            "origin": headers.get("origin", ""),
            "referer": headers.get("referer", ""),
            "x-forwarded-for": headers.get("x-forwarded-for", ""),
            "x-forwarded-host": headers.get("x-forwarded-host", ""),
            "x-forwarded-proto": headers.get("x-forwarded-proto", ""),
        },
    }


def show_request_metadata_diagnostics() -> None:
    with st.sidebar.expander("Request metadata", expanded=False):
        st.caption(
            "Open this on Streamlit Cloud and locally to compare what the app "
            "receives from each environment."
        )
        st.json(collect_request_metadata())


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


def active_data_paths() -> tuple[Path, Path, Path]:
    devices_path = DEVICES_FILE if DEVICES_FILE.exists() else DEVICES_FORMAT_FILE
    roms_path = ROMS_FILE if ROMS_FILE.exists() else ROMS_FORMAT_FILE
    compatibility_path = (
        COMPATIBILITY_FILE if COMPATIBILITY_FILE.exists() else COMPATIBILITY_FORMAT_FILE
    )
    return devices_path, roms_path, compatibility_path


def columns_for(rows: Rows) -> set[str]:
    return set(rows[0]) if rows else set()


def find_missing_columns(
    rows: Rows, required_columns: set[str], file_name: str
) -> list[str]:
    missing_columns = sorted(required_columns - columns_for(rows))
    return [f"{file_name}: {', '.join(missing_columns)}"] if missing_columns else []


@st.cache_data
def load_data() -> tuple[Rows, Rows, Rows]:
    devices_path, roms_path, compatibility_path = active_data_paths()
    return (
        load_table(devices_path),
        load_table(roms_path),
        load_table(compatibility_path),
    )


def create_lookup_database(devices: Rows, roms: Rows, compatibility: Rows) -> Database:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE devices (
            device_id TEXT PRIMARY KEY,
            device_type TEXT NOT NULL,
            brand TEXT NOT NULL,
            device TEXT NOT NULL,
            model TEXT NOT NULL
        );
        CREATE TABLE roms (
            rom_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            android_version TEXT NOT NULL,
            maintainer TEXT NOT NULL,
            status TEXT NOT NULL,
            website TEXT NOT NULL
        );
        CREATE TABLE compatibility (
            device_id TEXT NOT NULL,
            rom_id TEXT NOT NULL,
            support_level TEXT NOT NULL,
            last_verified TEXT NOT NULL
        );
        CREATE INDEX idx_devices_type_brand_device_model
            ON devices (device_type, brand, device, model);
        CREATE INDEX idx_roms_name_status ON roms (name, status);
        CREATE INDEX idx_compatibility_device_id ON compatibility (device_id);
        CREATE INDEX idx_compatibility_rom_id ON compatibility (rom_id);
        """
    )
    conn.executemany(
        """
        INSERT INTO devices (device_id, device_type, brand, device, model)
        VALUES (:device_id, :device_type, :brand, :device, :model)
        """,
        devices,
    )
    conn.executemany(
        """
        INSERT INTO roms
            (rom_id, name, version, android_version, maintainer, status, website)
        VALUES
            (:rom_id, :name, :version, :android_version, :maintainer, :status, :website)
        """,
        roms,
    )
    conn.executemany(
        """
        INSERT INTO compatibility (device_id, rom_id, support_level, last_verified)
        VALUES (:device_id, :rom_id, :support_level, :last_verified)
        """,
        compatibility,
    )
    return conn


@st.cache_resource(max_entries=2)
def load_lookup_database(
    devices_signature: DataFileSignature,
    roms_signature: DataFileSignature,
    compatibility_signature: DataFileSignature,
) -> Database:
    return create_lookup_database(
        load_table(Path(devices_signature[0])),
        load_table(Path(roms_signature[0])),
        load_table(Path(compatibility_signature[0])),
    )


def get_lookup_database() -> Database:
    devices_path, roms_path, compatibility_path = active_data_paths()
    return load_lookup_database(
        (str(devices_path), devices_path.stat().st_mtime_ns),
        (str(roms_path), roms_path.stat().st_mtime_ns),
        (str(compatibility_path), compatibility_path.stat().st_mtime_ns),
    )


def rows_from_cursor(cursor: sqlite3.Cursor) -> Rows:
    return [dict(row) for row in cursor.fetchall()]


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
        f"{device_type_label(row['device_type'])} - {row['brand']} {row['device']} "
        f"{row['model']} [{row['device_id']}]"
    )


def rom_label(row: Row) -> str:
    return f"{row['name']} {row['version']} - Android {row['android_version']}"


def device_type_label(device_type: str) -> str:
    icon = DEVICE_TYPE_ICONS.get(device_type.casefold(), "◆")
    return f"{icon}: {device_type.title()}"


def filter_roms_by_status(roms: Rows, selected_status: str) -> Rows:
    status_value = ROM_STATUS_FILTER_VALUES.get(selected_status, selected_status)
    if status_value == "All":
        return roms
    status = status_value.casefold()
    return [row for row in roms if row["status"].casefold() == status]


def selector_options(values: list[str]) -> list[str]:
    return [ALL_SELECTOR_OPTION, *values]


def selected_filter(value: str) -> str:
    return "" if value == ALL_SELECTOR_OPTION else value


def query_device_types(conn: Database) -> list[str]:
    cursor = conn.execute(
        "SELECT DISTINCT device_type FROM devices ORDER BY device_type"
    )
    return [row["device_type"] for row in cursor.fetchall()]


def query_device_brands(conn: Database, device_type: str = "") -> list[str]:
    cursor = conn.execute(
        """
        SELECT DISTINCT brand
        FROM devices
        WHERE (? = '' OR device_type = ?)
        ORDER BY brand
        """,
        (device_type, device_type),
    )
    return [row["brand"] for row in cursor.fetchall()]


def query_device_names(
    conn: Database, device_type: str = "", brand: str = ""
) -> list[str]:
    cursor = conn.execute(
        """
        SELECT DISTINCT device
        FROM devices
        WHERE (? = '' OR device_type = ?)
            AND (? = '' OR brand = ?)
        ORDER BY device
        """,
        (device_type, device_type, brand, brand),
    )
    return [row["device"] for row in cursor.fetchall()]


def query_device_models(
    conn: Database, device_type: str = "", brand: str = "", device: str = ""
) -> list[str]:
    cursor = conn.execute(
        """
        SELECT DISTINCT model
        FROM devices
        WHERE (? = '' OR device_type = ?)
            AND (? = '' OR brand = ?)
            AND (? = '' OR device = ?)
        ORDER BY model
        """,
        (device_type, device_type, brand, brand, device, device),
    )
    return [row["model"] for row in cursor.fetchall()]


def query_devices(
    conn: Database,
    filters: DeviceFilters,
    limit: int = DIRECT_SEARCH_RESULT_LIMIT,
) -> Rows:
    return rows_from_cursor(
        conn.execute(
            """
            SELECT device_id, device_type, brand, device, model
            FROM devices
            WHERE (? = '' OR device_type = ?)
                AND (? = '' OR brand = ?)
                AND (? = '' OR device = ?)
                AND (? = '' OR model = ?)
            ORDER BY device_type, brand, device, model
            LIMIT ?
            """,
            (
                filters.device_type,
                filters.device_type,
                filters.brand,
                filters.brand,
                filters.device,
                filters.device,
                filters.model,
                filters.model,
                limit,
            ),
        )
    )


def count_devices(conn: Database, filters: DeviceFilters) -> int:
    cursor = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM devices
        WHERE (? = '' OR device_type = ?)
            AND (? = '' OR brand = ?)
            AND (? = '' OR device = ?)
            AND (? = '' OR model = ?)
        """,
        (
            filters.device_type,
            filters.device_type,
            filters.brand,
            filters.brand,
            filters.device,
            filters.device,
            filters.model,
            filters.model,
        ),
    )
    return int(cursor.fetchone()["total"])


def query_rom_names(conn: Database, status: str = "") -> list[str]:
    status_normalized = status.casefold()
    cursor = conn.execute(
        """
        SELECT name
        FROM roms
        WHERE (? = '' OR lower(status) = ?)
        ORDER BY name
        """,
        (status_normalized, status_normalized),
    )
    return [row["name"] for row in cursor.fetchall()]


def query_rom_by_name(conn: Database, name: str) -> Row | None:
    cursor = conn.execute(
        """
        SELECT rom_id, name, version, android_version, maintainer, status, website
        FROM roms
        WHERE name = ?
        """,
        (name,),
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def query_device_rom_results(
    conn: Database, selected_device_id: str, selected_status: str = "All"
) -> Rows:
    selected_status_normalized = selected_status.casefold()
    return rows_from_cursor(
        conn.execute(
            """
            SELECT
                compatibility.device_id,
                compatibility.rom_id,
                compatibility.support_level,
                compatibility.last_verified,
                roms.name,
                roms.version,
                roms.android_version,
                roms.maintainer,
                roms.status,
                roms.website
            FROM compatibility
            JOIN roms ON roms.rom_id = compatibility.rom_id
            WHERE compatibility.device_id = ?
                AND (? = 'all' OR lower(roms.status) = ?)
            ORDER BY compatibility.support_level, roms.name
            """,
            (
                selected_device_id,
                selected_status_normalized,
                selected_status_normalized,
            ),
        )
    )


def query_rom_device_results(conn: Database, selected_rom_id: str) -> Rows:
    return rows_from_cursor(
        conn.execute(
            """
            SELECT
                compatibility.device_id,
                compatibility.rom_id,
                compatibility.support_level,
                compatibility.last_verified,
                devices.device_type,
                devices.brand,
                devices.device,
                devices.model
            FROM compatibility
            JOIN devices ON devices.device_id = compatibility.device_id
            WHERE compatibility.rom_id = ?
            ORDER BY devices.device_type, devices.brand, devices.device, devices.model
            """,
            (selected_rom_id,),
        )
    )


def status_badge_html(status: str) -> str:
    normalized_status = status.casefold()
    theme_type = getattr(st.context.theme, "type", "light") or "light"
    theme_styles = STATUS_BADGE_STYLES.get(theme_type, STATUS_BADGE_STYLES["light"])
    color, background, border = theme_styles.get(
        normalized_status, theme_styles["default"]
    )
    display_status = STATUS_DISPLAY_LABELS.get(normalized_status, status.title())
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
        f"{html.escape(display_status)}"
        "</span>"
    )


def selected_status_value(selected_status: str) -> str:
    return ROM_STATUS_FILTER_VALUES.get(selected_status, selected_status)


def show_data_contribution_wiki() -> None:
    if SWECHA_LOGO_FILE.exists():
        st.sidebar.image(str(SWECHA_LOGO_FILE), width=150)

    show_request_metadata_diagnostics()

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
        st.markdown(f"- Open the [live app]({LIVE_APP_URL})")
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
                "Type": device_type_label(row["device_type"]),
                "Device": row["device"],
                "Model": row["model"],
                "Support": row["support_level"],
                "Last verified": row["last_verified"],
            }
        )
    show_limited_results(display, len(results))


def show_selected_device_roms(
    conn: Database,
    selected_device_id: str,
    selected_device: Row,
) -> None:
    if not selected_device_id:
        st.info("Select a device to view compatible ROMs.")
        return

    st.caption(
        f"Selected: {device_type_label(selected_device['device_type'])} - "
        f"{selected_device['brand']} {selected_device['device']} "
        f"{selected_device['model']}"
    )

    status_filter = st.segmented_control(
        "ROM activity status",
        ROM_STATUS_FILTER_OPTIONS,
        default="All",
        key=f"device_rom_status_{selected_device_id}",
    )
    st.caption("*Stale means no recent updates or announcements.")
    results = query_device_rom_results(
        conn,
        selected_device_id,
        selected_status_value(status_filter or "All"),
    )
    show_rom_results(results)


def direct_device_lookup(conn: Database) -> None:
    selector_columns = st.columns(3)
    selected_type_label = selector_columns[0].selectbox(
        "Type",
        selector_options(query_device_types(conn)),
        key="device_type_selector",
    )
    selected_type = selected_filter(selected_type_label)
    selected_brand_label = selector_columns[1].selectbox(
        "Brand",
        selector_options(query_device_brands(conn, selected_type)),
        key=f"device_brand_selector_{selected_type_label}",
    )
    selected_brand = selected_filter(selected_brand_label)
    selected_device_label = selector_columns[2].selectbox(
        "Device",
        selector_options(query_device_names(conn, selected_type, selected_brand)),
        key=f"device_name_selector_{selected_type_label}_{selected_brand_label}",
    )
    selected_device_name = selected_filter(selected_device_label)
    matching_models = query_device_models(
        conn, selected_type, selected_brand, selected_device_name
    )
    selected_model = (
        matching_models[0] if selected_device_name and matching_models else ""
    )

    filters = DeviceFilters(
        selected_type, selected_brand, selected_device_name, selected_model
    )
    matching_devices = query_devices(conn, filters)
    total_matches = count_devices(conn, filters)
    if not matching_devices:
        st.warning("No devices match that search.")
        return

    if total_matches > DIRECT_SEARCH_RESULT_LIMIT:
        st.caption(
            f"Showing the first {DIRECT_SEARCH_RESULT_LIMIT} of "
            f"{total_matches} matches. Refine the selectors to narrow results."
        )

    device_options = {device_label(row): row for row in matching_devices}
    selected_label = st.selectbox(
        "Matching devices",
        list(device_options.keys()),
        key=(
            "matching_device_"
            f"{selected_type_label}_{selected_brand_label}_"
            f"{selected_device_label}_{selected_model or ALL_SELECTOR_OPTION}"
        ),
    )

    show_selected_device_roms(
        conn,
        device_options[selected_label]["device_id"],
        device_options[selected_label],
    )


def device_lookup(conn: Database) -> None:
    st.subheader("Find compatible ROMs")
    direct_device_lookup(conn)


def rom_lookup(conn: Database) -> None:
    st.subheader("Find compatible devices")

    status_filter = st.segmented_control(
        "ROM activity status",
        ROM_STATUS_FILTER_OPTIONS,
        default="All",
        key="rom_selector_status",
    )
    selected_status = status_filter or "All"
    st.caption("*Stale means no recent updates or announcements.")
    rom_names = query_rom_names(
        conn,
        "" if selected_status == "All" else selected_status_value(selected_status),
    )
    if not rom_names:
        st.warning("No ROMs match that activity status.")
        return

    selected_name = st.selectbox("ROM OS name", rom_names, key="rom_name_selector")
    selected_rom = query_rom_by_name(conn, selected_name)
    if selected_rom is None:
        st.warning("Select a ROM to view compatible devices.")
        return

    st.caption(f"Selected: {rom_label(selected_rom)}")

    results = query_rom_device_results(conn, selected_rom["rom_id"])
    show_device_results(results)


def main() -> None:
    st.set_page_config(
        page_title="Android Custom ROM Finder",
        layout="wide",
    )
    st.title("Android Custom ROM Finder")
    st.warning(
        "Temporary notice: data entry and verification are still in progress. "
        "Displayed compatibility data may be incomplete or inaccurate."
    )
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

    lookup_db = get_lookup_database()

    st.caption(
        "Device type icons: "
        + " | ".join(
            device_type_label(device_type)
            for device_type in sorted({row["device_type"] for row in devices})
        )
    )

    lookup_mode = st.segmented_control(
        "Lookup mode",
        ["Device to ROMs", "ROM to devices"],
        default="Device to ROMs",
    )
    if lookup_mode == "Device to ROMs":
        device_lookup(lookup_db)
    elif lookup_mode == "ROM to devices":
        rom_lookup(lookup_db)


if __name__ == "__main__":
    main()
