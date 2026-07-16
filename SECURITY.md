# Security Policy

## Supported Versions

This project is in active development. Security fixes are handled on the active development branches and released through the repository's normal merge process.

## Reporting a Vulnerability

Do not open a public issue for sensitive security reports. If private security reporting is enabled on the repository, use that channel. If it is not available, contact a project maintainer directly through the project hosting platform and share only the minimum details needed to establish contact.

After a private channel is established, include:

- A description of the vulnerability.
- Steps to reproduce it.
- Impact and affected files or features.
- Any proof of concept, logs, or screenshots that help verify the report.
- Suggested mitigation, if known.

## Scope

Security reports may include:

- Exposure of secrets, tokens, or private configuration.
- Unsafe handling of user input.
- Dependency vulnerabilities that affect the running Streamlit app.
- Data validation gaps that could break app behavior or expose unintended content.
- Deployment or configuration issues that could expose private data.

## Out of Scope

The following are usually not security vulnerabilities:

- Incorrect ROM compatibility data without a security impact.
- Missing metadata in public CSV files.
- General feature requests or UI improvements.
- Reports that require access to private systems without authorization.

## Secrets and Private Data

Do not commit secrets. `.streamlit/secrets.toml` is ignored by Git and should be used only for local private configuration if future integrations require it.

Dataset contributions should use public, verifiable information. Do not add private device identifiers, private maintainer contact details, access tokens, or unpublished vulnerability details to CSV files.

## Dependency Hygiene

When adding dependencies:

- Prefer well-maintained packages.
- Keep dependency changes minimal and justified.
- Update `requirements.txt` or `requirements-dev.txt` intentionally.
- Run the test suite before opening a merge request.

## License

This project is licensed under the GNU Affero General Public License v3.0. Security fixes and related contributions are accepted under the same license.
