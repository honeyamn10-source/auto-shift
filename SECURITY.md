# Security

Auto Shift is a local supervised prototype, not a production isolation boundary. Keep it bound to localhost and use a dedicated browser profile. Never add real credentials to repository files, issues, screenshots, or test fixtures.

If a credential is committed, revoke or rotate it at the provider; deleting a file does not revoke the credential or remove Git history.

For a security report, avoid including credentials or private browser data in a public issue. Use GitHub's private vulnerability reporting if the repository owner has enabled it. No private reporting channel or response-time guarantee is configured by this document.

See docs/ARCHITECTURE.md for controls and limitations.
