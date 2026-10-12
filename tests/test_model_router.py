import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from model_router import build_model_chain, call_with_model_fallback, should_try_fallback  # noqa: E402


class FakeApiError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class ModelRouterTests(unittest.TestCase):
    def test_model_chain_is_primary_first_and_deduplicated(self):
        self.assertEqual(
            build_model_chain("gemini-3.8-flash", "gemini-3.6-flash, gemini-3.8-flash, gemini-3.5-flash-lite"),
            ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"],
        )

    def test_503_triggers_fallback(self):
        self.assertTrue(should_try_fallback(FakeApiError(503, "UNAVAILABLE: high demand")))

    def test_429_rate_limit_triggers_fallback(self):
        self.assertTrue(should_try_fallback(FakeApiError(429, "RESOURCE_EXHAUSTED: rate limit")))

    def test_daily_quota_does_not_cycle_models(self):
        self.assertFalse(should_try_fallback(FakeApiError(429, "quota_exceeded: daily quota exhausted")))

    def test_authentication_error_does_not_cycle_models(self):
        self.assertFalse(should_try_fallback(FakeApiError(401, "invalid API key")))

    def test_primary_failure_returns_fallback_success_and_notes(self):
        calls = []

        def invoke(model):
            calls.append(model)
            if model == "primary":
                raise FakeApiError(503, "high demand")
            return "brief"

        result, model, notes = call_with_model_fallback(["primary", "fallback"], invoke)
        self.assertEqual(result, "brief")
        self.assertEqual(model, "fallback")
        self.assertEqual(calls, ["primary", "fallback"])
        self.assertTrue(any("Trying fallback model `fallback`" in note for note in notes))

    def test_non_retryable_error_is_raised_without_trying_fallback(self):
        calls = []

        def invoke(model):
            calls.append(model)
            raise FakeApiError(403, "permission denied")

        with self.assertRaisesRegex(RuntimeError, "non-retryable error"):
            call_with_model_fallback(["primary", "fallback"], invoke)
        self.assertEqual(calls, ["primary"])


if __name__ == "__main__":
    unittest.main()
