"""Real Chromium + Browser Use smoke test. No API key or external website."""
import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from playwright.async_api import async_playwright
from browser_use import Browser


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"<html><head><title>AutoShiftSmoke</title></head><body><h1>Browser ready</h1><button>Continue</button></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


async def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    async with async_playwright() as pw:
        executable = pw.chromium.executable_path
    browser = Browser(executable_path=executable, is_local=True, headless=True, chromium_sandbox=os.getenv("GITHUB_ACTIONS") != "true", allowed_domains=["127.0.0.1"])
    try:
        await browser.start()
        await browser.navigate_to(f"http://127.0.0.1:{server.server_port}")
        # Browser Use 0.13.10 reads title from cached target metadata, which can
        # retain the URL. Check the live document and agent-visible DOM instead.
        async with async_playwright() as pw:
            connection = await pw.chromium.connect_over_cdp(browser.cdp_url)
            page = connection.contexts[0].pages[-1]
            try:
                await page.wait_for_function("document.title === 'AutoShiftSmoke'", timeout=15000)
            except Exception:
                print("Fixture URL:", page.url)
                print("Fixture body:", (await page.locator("body").inner_text())[:1500])
                raise
            state = await browser.get_browser_state_summary(cached=False)
        assert state.url.rstrip("/") == f"http://127.0.0.1:{server.server_port}", state.url
        agent_dom = state.dom_state.llm_representation()
        assert "Browser ready" in agent_dom, agent_dom
        assert "Continue" in agent_dom, agent_dom
        assert state.dom_state.selector_map, "Expected an actionable browser element"
        assert state.screenshot, "Expected a real Chromium screenshot"
        print("Real Chromium navigation and screenshot passed.")
    finally:
        await browser.kill()
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    asyncio.run(main())
