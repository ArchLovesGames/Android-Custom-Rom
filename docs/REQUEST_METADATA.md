# Request Metadata Diagnostics

The `detector` branch includes a collapsed **Request metadata** expander in the
app sidebar. Open it to inspect the metadata Streamlit exposes through
`st.context`.

## How to Compare

1. Deploy or open the app on Streamlit Cloud.
2. Open the sidebar.
3. Expand **Request metadata**.
4. Save the JSON shown there.
5. Run the app locally with `streamlit run app.py`.
6. Open the local sidebar and expand **Request metadata** again.
7. Compare the two JSON objects.

## Fields Captured

- `url`
- `ip_address`
- `locale`
- `timezone`
- `timezone_offset`
- `is_embedded`
- `theme`
- `headers`
- `cookies`
- selected header fields:
  - `user-agent`
  - `host`
  - `origin`
  - `referer`
  - `x-forwarded-for`
  - `x-forwarded-host`
  - `x-forwarded-proto`

## Expected Differences

Streamlit Cloud normally includes deployment/proxy-oriented host and forwarded
headers. Local runs usually show localhost host values and may not include
forwarded headers.

Exact device model detection is not guaranteed in either environment because
modern browsers often hide hardware model details from the user-agent string.
