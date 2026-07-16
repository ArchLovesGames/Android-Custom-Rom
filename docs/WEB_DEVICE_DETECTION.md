# Web Device Detection

The hosted Streamlit app uses browser Web APIs to collect privacy-limited device
signals and attempt a conservative match against `data/devices.csv`.

## APIs Used

- `navigator.userAgentData` and high-entropy client hints, including `model`,
  `platform`, `platformVersion`, `architecture`, and browser version details
- `navigator.userAgent` as a legacy fallback signal
- `navigator.hardwareConcurrency` for logical CPU thread hints
- `navigator.deviceMemory` for approximate memory hints, where supported
- `navigator.connection` for network class hints, where supported
- `window.screen`, `window.innerWidth`, `window.innerHeight`, and
  `window.devicePixelRatio` for display hints

The app does not use permission-gated hardware APIs such as WebUSB, WebHID, or
media device enumeration for this feature.

## Matching Behavior

Browser-side matching is intentionally strict. It only auto-selects a device
when the browser exposes a strong model, device, or codename signal that matches
the dataset. Broad hints such as `Android`, `Samsung`, or `Mobile` are not enough
to choose a device.

If the browser does not expose the exact model, the app shows the collected
signals and asks the user to continue with the manual selectors.

## Limitations

Modern browsers intentionally restrict unique hardware identifiers. Many mobile
browsers do not expose exact Android model names through Web APIs. This protects
privacy but means browser detection cannot be treated as a complete replacement
for manual device selection.

Use the manual selectors when browser APIs do not expose enough information for
a confident match.
