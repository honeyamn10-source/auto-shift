# Open-source foundation

Reviewed for Auto Shift on 2026-09-14. These are specific design choices, not claims that one repository is best for every use case.

| Repository | License | Decision |
| --- | --- | --- |
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | MIT | Use its Python agent and browser session as a pinned dependency, version 0.13.10. |
| [microsoft/playwright-python](https://github.com/microsoft/playwright-python) | Apache-2.0 | Use its Chromium installer and executable discovery; also suitable for deterministic browser checks. |
| [browser-use/web-ui](https://github.com/browser-use/web-ui) | MIT | Reviewed as a ready-made UI alternative; not copied. Auto Shift uses a smaller original dashboard and a single-action approval gate. |

The new interface and service wrapper are original project code. Dependency source code is installed by the package manager rather than vendored. Package distributions retain their own licenses; see THIRD_PARTY_NOTICES.md.

## Why pin Browser Use

The approval mechanism depends on the order of its callbacks. In 0.13.10, `Agent.step()` awaits `_get_next_action()` before `_execute_actions()`; the former awaits `register_new_step_callback`. Auto Shift blocks that callback until the user decides.

The contract test checks this ordering. Review the gate before any dependency upgrade. Also keep `directly_open_url=False` and `max_actions_per_step=1`; automatically opening a task URL would bypass the first action review.

## Sources

- [Pinned release](https://github.com/browser-use/browser-use/releases/tag/0.13.10)
- [Agent callback implementation](https://github.com/browser-use/browser-use/blob/0.13.10/browser_use/agent/service.py)
- [Browser session implementation](https://github.com/browser-use/browser-use/blob/0.13.10/browser_use/browser/session.py)
- [OpenAI adapter](https://github.com/browser-use/browser-use/blob/0.13.10/browser_use/llm/openai/chat.py)
- [Ollama adapter](https://github.com/browser-use/browser-use/blob/0.13.10/browser_use/llm/ollama/chat.py)

## Reproducibility boundary

Browser Use, FastAPI, Uvicorn and Playwright are pinned; this project does not yet include a complete transitive lockfile. Platform-specific packages and model behavior still need validation for release.


The ephemeral GitHub Actions fixture disables Chromium's internal sandbox only in its smoke-test browser, which visits a local test page and has no user profile or model credentials. The desktop application's browser retains its default sandbox setting.
