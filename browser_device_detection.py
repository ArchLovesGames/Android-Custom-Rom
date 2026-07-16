import re
from collections.abc import Iterable, Mapping
from typing import Any

Row = dict[str, str]
Rows = list[Row]

BROWSER_DEVICE_PROFILE_HTML = """
<div id="browser-device-profile" style="
  color: var(--st-text-color);
  font-size: 0.875rem;
  line-height: 1.35;
">
  Browser device signals are being collected.
</div>
"""

BROWSER_DEVICE_PROFILE_JS = """
export default async function (component) {
  const { parentElement, setStateValue } = component
  const status = parentElement.querySelector("#browser-device-profile")

  const uaData = navigator.userAgentData || null
  let highEntropy = {}
  if (uaData && typeof uaData.getHighEntropyValues === "function") {
    try {
      highEntropy = await uaData.getHighEntropyValues([
        "architecture",
        "bitness",
        "formFactors",
        "fullVersionList",
        "model",
        "platform",
        "platformVersion",
        "uaFullVersion",
        "wow64",
      ])
    } catch (error) {
      highEntropy = { error: String(error) }
    }
  }

  const connection =
    navigator.connection || navigator.mozConnection || navigator.webkitConnection
  const profile = {
    userAgent: navigator.userAgent || "",
    platform: navigator.platform || "",
    vendor: navigator.vendor || "",
    language: navigator.language || "",
    languages: Array.from(navigator.languages || []),
    maxTouchPoints: navigator.maxTouchPoints || 0,
    hardwareConcurrency: navigator.hardwareConcurrency || null,
    deviceMemory: navigator.deviceMemory || null,
    userAgentData: uaData
      ? {
          mobile: Boolean(uaData.mobile),
          platform: uaData.platform || "",
          brands: Array.from(uaData.brands || []),
        }
      : null,
    highEntropy,
    connection: connection
      ? {
          effectiveType: connection.effectiveType || "",
          type: connection.type || "",
          downlink: connection.downlink || null,
          rtt: connection.rtt || null,
          saveData: Boolean(connection.saveData),
        }
      : null,
    screen: {
      width: window.screen ? window.screen.width : null,
      height: window.screen ? window.screen.height : null,
      availWidth: window.screen ? window.screen.availWidth : null,
      availHeight: window.screen ? window.screen.availHeight : null,
      colorDepth: window.screen ? window.screen.colorDepth : null,
      pixelDepth: window.screen ? window.screen.pixelDepth : null,
      devicePixelRatio: window.devicePixelRatio || null,
      viewportWidth: window.innerWidth || null,
      viewportHeight: window.innerHeight || null,
    },
    collectedAt: new Date().toISOString(),
  }

  setStateValue("profile", profile)
  if (status) status.textContent = "Browser device signals collected."
}
"""

BRAND_ALIASES = {
    "google": {"google", "pixel"},
    "htc": {"htc"},
    "motorola": {"motorola", "moto"},
    "nothing": {"nothing"},
    "oneplus": {"oneplus", "one plus"},
    "oppo": {"oppo"},
    "samsung": {"samsung", "galaxy"},
    "sony": {"sony", "xperia"},
    "xiaomi": {"xiaomi", "redmi", "poco", "mi"},
}


def normalize(value: object) -> str:
    text = str(value or "").casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def normalized_variants(value: str) -> set[str]:
    normalized = normalize(value)
    if not normalized:
        return set()
    return {
        normalized,
        normalized.replace(" ", ""),
    }


def mapping_value(data: Mapping[str, Any], key: str) -> Any:
    value = data.get(key, "")
    return value if value is not None else ""


def nested_mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key, {})
    return value if isinstance(value, Mapping) else {}


def list_text(values: Iterable[Any]) -> str:
    return " ".join(str(value) for value in values if value)


def browser_signal_text(profile: Mapping[str, Any]) -> str:
    ua_data = nested_mapping(profile, "userAgentData")
    high_entropy = nested_mapping(profile, "highEntropy")
    signals = [
        mapping_value(profile, "userAgent"),
        mapping_value(profile, "platform"),
        mapping_value(profile, "vendor"),
        mapping_value(ua_data, "platform"),
        mapping_value(high_entropy, "platform"),
        mapping_value(high_entropy, "model"),
        mapping_value(high_entropy, "formFactors"),
    ]
    brands = ua_data.get("brands", [])
    if isinstance(brands, list):
        signals.append(
            list_text(
                brand.get("brand", "") for brand in brands if isinstance(brand, Mapping)
            )
        )
    return normalize(list_text(signals))


def exact_signal_values(profile: Mapping[str, Any]) -> set[str]:
    high_entropy = nested_mapping(profile, "highEntropy")
    values = {
        normalize(mapping_value(high_entropy, "model")),
        normalize(mapping_value(profile, "platform")),
    }
    values.discard("")
    return values


def brand_conflicts(row: Row, signal_text: str) -> bool:
    row_brand = normalize(row.get("brand", ""))
    if not row_brand:
        return False
    row_aliases = BRAND_ALIASES.get(row_brand, {row_brand})
    mentioned_aliases = {
        brand
        for brand, aliases in BRAND_ALIASES.items()
        if any(f" {alias} " in f" {signal_text} " for alias in aliases)
    }
    return bool(
        mentioned_aliases
        and row_brand not in mentioned_aliases
        and not row_aliases.intersection(mentioned_aliases)
    )


def token_in_signal(needle: str, signal_text: str) -> bool:
    return any(
        variant and f" {variant} " in f" {signal_text} "
        for variant in normalized_variants(needle)
    )


def browser_device_match_score(row: Row, profile: Mapping[str, Any]) -> int:
    signal_text = browser_signal_text(profile)
    if not signal_text or brand_conflicts(row, signal_text):
        return 0

    score = 0
    exact_values = exact_signal_values(profile)
    row_model = normalize(row.get("model", ""))
    row_device = normalize(row.get("device", ""))
    row_device_id = normalize(row.get("device_id", ""))
    row_brand = normalize(row.get("brand", ""))

    if row_model and row_model in exact_values:
        score += 8
    if row_device and row_device in exact_values:
        score += 8
    if token_in_signal(row_model, signal_text):
        score += 5
    if token_in_signal(row_device, signal_text):
        score += 4
    if token_in_signal(row_device_id, signal_text):
        score += 3
    if row_brand and token_in_signal(row_brand, signal_text):
        score += 1
    return score


def match_browser_device(devices: Rows, profile: Mapping[str, Any]) -> Row | None:
    best_row: Row | None = None
    best_score = 0
    for row in devices:
        score = browser_device_match_score(row, profile)
        if score > best_score:
            best_row = row
            best_score = score
    return best_row if best_score >= 7 else None


def browser_device_profile_component(
    component_renderer: Any, session_state: Any
) -> dict[str, object]:
    component_key = "browser_device_profile"
    result = component_renderer(
        key=component_key,
        data={},
        on_profile_change=lambda: None,
    )
    profile = getattr(result, "profile", None)
    if isinstance(profile, dict):
        return profile

    state = session_state.get(component_key, {})
    if isinstance(state, dict) and isinstance(state.get("profile"), dict):
        return state["profile"]
    return {}


def browser_profile_summary(profile: Mapping[str, Any]) -> list[str]:
    ua_data = nested_mapping(profile, "userAgentData")
    high_entropy = nested_mapping(profile, "highEntropy")
    screen = nested_mapping(profile, "screen")
    connection = nested_mapping(profile, "connection")
    summary = []

    platform = mapping_value(high_entropy, "platform") or mapping_value(
        ua_data, "platform"
    )
    model = mapping_value(high_entropy, "model")
    if platform:
        summary.append(f"Platform: {platform}")
    if model:
        summary.append(f"Model hint: {model}")
    if "mobile" in ua_data:
        summary.append(f"Mobile hint: {bool(ua_data['mobile'])}")
    if mapping_value(profile, "deviceMemory"):
        summary.append(f"Memory hint: {mapping_value(profile, 'deviceMemory')} GB")
    if mapping_value(profile, "hardwareConcurrency"):
        summary.append(
            f"CPU threads hint: {mapping_value(profile, 'hardwareConcurrency')}"
        )
    if mapping_value(connection, "effectiveType"):
        summary.append(f"Network hint: {mapping_value(connection, 'effectiveType')}")
    if mapping_value(screen, "width") and mapping_value(screen, "height"):
        summary.append(
            f"Screen hint: {mapping_value(screen, 'width')} x "
            f"{mapping_value(screen, 'height')}"
        )
    return summary
