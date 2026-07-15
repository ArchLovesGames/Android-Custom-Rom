import shutil
import subprocess
from typing import NamedTuple

Row = dict[str, str]
Rows = list[Row]

ADB_PROPERTIES = {
    "manufacturer": "ro.product.manufacturer",
    "brand": "ro.product.brand",
    "model": "ro.product.model",
    "device": "ro.product.device",
    "product": "ro.product.name",
    "android_version": "ro.build.version.release",
    "fingerprint": "ro.build.fingerprint",
}


class LocalDeviceInfo(NamedTuple):
    manufacturer: str = ""
    brand: str = ""
    model: str = ""
    device: str = ""
    product: str = ""
    android_version: str = ""
    fingerprint: str = ""


class LocalDetectionResult(NamedTuple):
    ok: bool
    message: str
    info: LocalDeviceInfo = LocalDeviceInfo()


def normalize(value: str) -> str:
    return " ".join(value.casefold().replace("-", " ").replace("_", " ").split())


def run_adb(args: list[str], timeout: int = 5) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        ["adb", *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def parse_adb_devices(output: str) -> list[str]:
    devices = []
    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def getprop(serial: str, prop_name: str) -> str:
    result = run_adb(["-s", serial, "shell", "getprop", prop_name])
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def detect_local_android_device() -> LocalDetectionResult:
    if shutil.which("adb") is None:
        return LocalDetectionResult(
            ok=False,
            message="ADB is not installed or not available on PATH.",
        )

    devices_result = run_adb(["devices"])
    if devices_result.returncode != 0:
        return LocalDetectionResult(
            ok=False,
            message=(devices_result.stderr or "Unable to run adb devices.").strip(),
        )

    connected_devices = parse_adb_devices(devices_result.stdout)
    if not connected_devices:
        return LocalDetectionResult(
            ok=False,
            message="No authorized Android device found over ADB.",
        )

    serial = connected_devices[0]
    values = {
        field: getprop(serial, prop_name) for field, prop_name in ADB_PROPERTIES.items()
    }
    return LocalDetectionResult(
        ok=True,
        message=f"Detected ADB device {serial}.",
        info=LocalDeviceInfo(**values),
    )


def token_match(needle: str, haystack: str) -> bool:
    normalized_needle = normalize(needle)
    normalized_haystack = normalize(haystack)
    return bool(
        normalized_needle and f" {normalized_needle} " in f" {normalized_haystack} "
    )


def device_match_score(row: Row, info: LocalDeviceInfo) -> int:
    score = 0
    brand_values = {normalize(info.brand), normalize(info.manufacturer)}
    if normalize(row["brand"]) in brand_values:
        score += 3
    if normalize(row["model"]) in {normalize(info.device), normalize(info.product)}:
        score += 6
    if token_match(row["device"], info.model):
        score += 4
    if token_match(row["model"], info.model):
        score += 5
    if token_match(row["device_id"], info.fingerprint):
        score += 2
    return score


def match_local_device(devices: Rows, info: LocalDeviceInfo) -> Row | None:
    best_row: Row | None = None
    best_score = 0
    for row in devices:
        score = device_match_score(row, info)
        if score > best_score:
            best_row = row
            best_score = score
    return best_row if best_score >= 6 else None
