# Local Device Detection

Device detection is local-only.

The hosted Streamlit web app cannot inspect a visitor's Android hardware. A
browser does not expose reliable ROM, build fingerprint, device codename, or
exact model details to the server.

When the app is run locally, it can detect an Android device connected to the
same computer through ADB.

## Requirements

- Android Platform Tools installed
- `adb` available on `PATH`
- USB debugging enabled on the Android device
- The computer authorized from the Android device prompt

## Usage

1. Connect the Android device with USB.
2. Confirm it appears in:

   ```bash
   adb devices
   ```

3. Start the app locally:

   ```bash
   streamlit run app.py
   ```

4. In `Device to ROMs`, click **Detect connected Android device**.

The app reads these Android properties:

- `ro.product.manufacturer`
- `ro.product.brand`
- `ro.product.model`
- `ro.product.device`
- `ro.product.name`
- `ro.build.version.release`
- `ro.build.fingerprint`

If those values match a row in `data/devices.csv`, compatible ROMs are shown.
If no exact dataset match is found, use the manual selectors.
