# Acceptance checklist

Automated validation passed on 15 September 2026 for code commit `128d1ca5cae3e09558f0e6bf729f79034468050d`: [GitHub Actions run 34939937418](https://github.com/honeyamn10-source/auto-shift/actions/runs/34939937418). This verifies the checks below, not the manual release checklist.

The real-browser check validates the live document title, current URL, agent-visible text and actionable elements, and a Chromium screenshot. Browser Use 0.13.10's summary title reads cached target metadata and can retain the URL; it is not used as proof of the live document title.

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
