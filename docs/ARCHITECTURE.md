# Architecture

A single FastAPI process serves the static dashboard and owns one Browser Use session. No external dashboard service is required.

1. The launcher creates an in-memory API token and opens a localhost URL containing it in the fragment.
2. JavaScript removes the fragment and keeps the token in session storage.
3. The API opens a dedicated visible Chromium profile.
4. A task creates one Browser Use agent with the selected model.
5. The pre-action callback publishes a screenshot, next goal and action parameters.
6. An approval request must carry the current one-use approval ID. Rejection or expiry cancels the step.
7. Task results remain in memory until replaced or the process exits. The user can export them.

## Scope and controls

Host checks and a secret custom request header protect the local API against ordinary cross-site requests. Origin checks reject other website origins. They do not protect against malicious software running as the same operating-system user.

All proposed actions require approval, including navigation. Approval is a user decision, not an automated risk classifier. Browser Use has built-in tools, including page-script and file capabilities; this wrapper is not an isolation sandbox.

A single task is allowed at a time. Session and task lifecycle changes use an asyncio lock. Stop cancels the running task but retains the visible browser for manual use; close also kills the browser session. Approval does not roll back side effects.

The model-facing prompt asks for manual handoff for credentials, payments, agreements, permission changes and deletion. Treat that prompt as behavioral guidance, not an enforcement boundary.

## Local data

- `.runtime/browser-profile`: browser login state and browsing data.
- `.runtime/downloads`: browser downloads.
- `.runtime/agent-files`: agent working files.
- `.env`: optional locally supplied configuration.

No API endpoint serves those directories. The user must deliberately manage their local retention. Other dependency caches or diagnostics may be managed by their respective libraries.

## Operational limits

Use one local desktop user and one server process. There is no remote desktop streaming, account system, job persistence, multi-user isolation, billing integration, or production deployment configuration. A hosted version requires a separate security and tenancy design.
