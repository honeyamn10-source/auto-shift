# Acceptance checklist

The source was authored through the GitHub connection. Local execution and visual inspection were unavailable in the authoring session. Check the repository's CI run for actual results; do not treat the presence of this checklist as a passed test.

## Automated

- Dependency installation.
- Python compilation and browser JavaScript syntax.
- API token, origin and hostname rejection.
- Validation error redaction.
- One-use action approval, rejection and multi-action refusal.
- Compatibility with the pinned Browser Use callback.
- Real headless Chromium navigation to a local fixture and screenshot capture.

## Manual before release

- Install on a clean Windows, macOS and Linux desktop.
- Open the dashboard at desktop and narrow viewport widths; check focus, contrast and controls.
- Start a visible browser, close it, and reopen it.
- Complete a public-page task with a configured model.
- Confirm no planned click executes before approval.
- Reject an action and verify the target page did not change.
- Stop during model generation and during approval wait.
- Let an approval expire.
- Sign in manually to a non-sensitive test account, then start a fresh task.
- Confirm profile retention and that a different desktop user cannot read the profile.
- Exercise domain restrictions, redirects and required sign-in hosts.
- Verify API usage and costs with your selected provider.
- Review screenshots and action parameters for sensitive page data.
- Test the exact local Ollama model and vision setting you intend to support.

Model-driven success, face authentication, passkeys, real account mutations and production readiness are not established by the automated fixture tests.
