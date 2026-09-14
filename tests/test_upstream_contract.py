"""Guard the upstream hook ordering our approval gate depends on."""
import inspect
import unittest

from browser_use import Agent, Browser, ChatOpenAI
from browser_use.llm.ollama.chat import ChatOllama


class UpstreamContractTests(unittest.TestCase):
    def test_supported_agent_settings(self):
        parameters = inspect.signature(Agent.__init__).parameters
        for name in ["register_new_step_callback", "directly_open_url", "enable_signal_handler", "max_actions_per_step"]:
            self.assertIn(name, parameters)

    def test_callback_precedes_action_execution(self):
        step = inspect.getsource(Agent.step)
        self.assertLess(step.index("await self._get_next_action("), step.index("await self._execute_actions("))
        planning = inspect.getsource(Agent._get_next_action)
        self.assertIn("await self._handle_post_llm_processing(", planning)
        callback = inspect.getsource(Agent._handle_post_llm_processing)
        self.assertIn("await self.register_new_step_callback(", callback)

    def test_adapters_and_browser_methods_exist(self):
        self.assertTrue(callable(ChatOpenAI))
        self.assertTrue(callable(ChatOllama))
        for name in ["start", "kill", "navigate_to", "get_browser_state_summary"]:
            self.assertTrue(callable(getattr(Browser, name)))


if __name__ == "__main__":
    unittest.main()
