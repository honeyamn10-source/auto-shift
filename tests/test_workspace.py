import asyncio
import unittest
from types import SimpleNamespace

from fastapi.testclient import TestClient
from autoshift.app import TOKEN, app
from autoshift.engine import Decision, SessionConfig, Workspace


class ApiSecurityTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app, base_url="http://127.0.0.1:8765")
        self.headers = {"x-autoshift-token": TOKEN}

    def test_private_state_requires_token(self):
        self.assertEqual(self.client.get("/api/state").status_code, 401)
        self.assertEqual(self.client.get("/api/state", headers=self.headers).status_code, 200)

    def test_cross_origin_mutation_is_rejected(self):
        response = self.client.post("/api/stop", json={}, headers={**self.headers, "origin": "https://evil.example"})
        self.assertEqual(response.status_code, 403)

    def test_host_rebinding_is_rejected(self):
        response = self.client.get("/api/state", headers={**self.headers, "host": "evil.example"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_secret_input_is_not_reflected(self):
        response = self.client.post("/api/tasks", headers=self.headers, json={
            "task": "test task", "provider": "invalid", "model": "example", "api_key": "PRIVATE_TEST_SENTINEL"
        })
        self.assertEqual(response.status_code, 422)
        self.assertNotIn("PRIVATE_TEST_SENTINEL", response.text)

    def test_no_browser_task_is_rejected(self):
        response = self.client.post("/api/tasks", headers=self.headers, json={"task": "read a public page", "model": "example"})
        self.assertEqual(response.status_code, 409)

    def test_home_has_security_headers(self):
        response = self.client.get("/")
        self.assertIn("frame-ancestors 'none'", response.headers["content-security-policy"])
        self.assertEqual(response.headers["cache-control"], "no-store")


class ApprovalTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.workspace = Workspace()
        self.state = SimpleNamespace(screenshot=None, url="https://example.com")
        action = SimpleNamespace(model_dump=lambda **kwargs: {"click": {"index": 3}})
        self.output = SimpleNamespace(action=[action], next_goal="Open the selected result")

    async def test_action_waits_for_matching_approval(self):
        waiting = asyncio.create_task(self.workspace.review_step(self.state, self.output, 1))
        await asyncio.sleep(0)
        self.assertFalse(waiting.done())
        with self.assertRaises(ValueError):
            self.workspace.decide(Decision(approval_id="wrong-id", approve=True))
        approval_id = self.workspace.pending["id"]
        self.workspace.decide(Decision(approval_id=approval_id, approve=True))
        with self.assertRaises(ValueError):
            self.workspace.decide(Decision(approval_id=approval_id, approve=True))
        await waiting
        self.assertEqual(self.workspace.status, "running")

    async def test_rejection_cancels_before_action(self):
        waiting = asyncio.create_task(self.workspace.review_step(self.state, self.output, 1))
        await asyncio.sleep(0)
        self.workspace.decide(Decision(approval_id=self.workspace.pending["id"], approve=False))
        with self.assertRaises(asyncio.CancelledError):
            await waiting

    async def test_multiple_actions_fail_closed(self):
        self.output.action *= 2
        with self.assertRaises(asyncio.CancelledError):
            await self.workspace.review_step(self.state, self.output, 1)

    def test_domain_rules_are_exact(self):
        self.assertEqual(SessionConfig(domains=["GitHub.com"]).domains, ["github.com"])
        for domain in ["https://github.com", "*.github.com", "github.com/path"]:
            with self.assertRaises(ValueError):
                SessionConfig(domains=[domain])


if __name__ == "__main__":
    unittest.main()
