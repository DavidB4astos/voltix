import json
import os
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import Mock, patch

import voltix.voltix as app

HEALTH_URL = "https://example.test/integration/health"
EXPECTED = {
    "status": "ok",
    "service": "voltix-xano",
    "integration": "available",
}


class FakeResponse:
    def __init__(self, payload, status=200):
        self.status = status
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class HealthContractTests(unittest.TestCase):
    def test_expected_contract_is_returned(self):
        with patch.object(app.urllib.request, "urlopen",
                          return_value=FakeResponse(EXPECTED)) as urlopen:
            self.assertEqual(app._request_xano_health(HEALTH_URL), EXPECTED)

        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.get_header("Accept"), "application/json")
        self.assertIsNone(request.get_header("Authorization"))
        self.assertIsNone(request.data)

    def test_unexpected_status_is_rejected(self):
        with patch.object(app.urllib.request, "urlopen",
                          return_value=FakeResponse(EXPECTED, status=500)):
            with self.assertRaises(ValueError):
                app._request_xano_health(HEALTH_URL)

    def test_non_object_payload_is_rejected(self):
        with patch.object(app.urllib.request, "urlopen",
                          return_value=FakeResponse([EXPECTED])):
            with self.assertRaises(ValueError):
                app._request_xano_health(HEALTH_URL)

    def test_diverging_contract_is_rejected(self):
        for payload in [{}, {"status": "ok"}, {**EXPECTED, "extra": True},
                        {**EXPECTED, "service": "outro"}]:
            with patch.object(app.urllib.request, "urlopen",
                              return_value=FakeResponse(payload)):
                with self.assertRaises(ValueError):
                    app._request_xano_health(HEALTH_URL)


class IntegrationHandlerTests(unittest.IsolatedAsyncioTestCase):
    def state(self):
        return app.State(_reflex_internal_init=True)

    def environment(self, value=HEALTH_URL):
        return patch.dict(os.environ, {app.XANO_HEALTH_URL_ENV: value})

    async def test_success_reports_available_and_keeps_only_technical_payload(self):
        state = self.state()
        with self.environment(), \
                patch.object(app, "_request_xano_health", return_value=EXPECTED) as request:
            await app.State.check_integration.fn(state)

        request.assert_called_once_with(HEALTH_URL)
        self.assertEqual(state.integration_status, "success")
        self.assertFalse(state.integration_loading)
        self.assertEqual(state.integration_message,
                         "Reflex-Xano integration is available.")
        self.assertEqual(state.integration_payload,
                         json.dumps(EXPECTED, sort_keys=True))

    async def test_missing_configuration_fails_without_request(self):
        state = self.state()
        with self.environment("   "), \
                patch.object(app, "_request_xano_health") as request:
            await app.State.check_integration.fn(state)

        request.assert_not_called()
        self.assertEqual(state.integration_status, "error")
        self.assertFalse(state.integration_loading)
        self.assertIn(app.XANO_HEALTH_URL_ENV, state.integration_message)
        self.assertEqual(state.integration_payload, "")

    async def test_http_failure_is_reported(self):
        state = self.state()
        error = urllib.error.HTTPError(HEALTH_URL, 503, "unavailable", {}, None)
        with self.environment(), \
                patch.object(app, "_request_xano_health", side_effect=error):
            await app.State.check_integration.fn(state)

        self.assertEqual(state.integration_status, "error")
        self.assertIn("503", state.integration_message)
        self.assertEqual(state.integration_payload, "")
        error.close()

    async def test_network_failure_is_reported(self):
        state = self.state()
        error = urllib.error.URLError("offline")
        with self.environment(), \
                patch.object(app, "_request_xano_health", side_effect=error):
            await app.State.check_integration.fn(state)

        self.assertEqual(state.integration_status, "error")
        self.assertIn("offline", state.integration_message)

    async def test_invalid_contract_is_reported(self):
        state = self.state()
        with self.environment(), \
                patch.object(app, "_request_xano_health", side_effect=ValueError("bad contract")):
            await app.State.check_integration.fn(state)

        self.assertEqual(state.integration_status, "error")
        self.assertIn("bad contract", state.integration_message)
        self.assertEqual(state.integration_payload, "")

    async def test_previous_success_payload_is_not_retained_after_failure(self):
        state = self.state()
        with self.environment(), \
                patch.object(app, "_request_xano_health", return_value=EXPECTED):
            await app.State.check_integration.fn(state)
        self.assertNotEqual(state.integration_payload, "")

        with self.environment(), \
                patch.object(app, "_request_xano_health",
                             side_effect=urllib.error.URLError("offline")):
            await app.State.check_integration.fn(state)

        self.assertEqual(state.integration_status, "error")
        self.assertEqual(state.integration_payload, "")

    async def test_retry_after_failure_can_succeed(self):
        state = self.state()
        with self.environment(), \
                patch.object(app, "_request_xano_health",
                             side_effect=[urllib.error.URLError("offline"), EXPECTED]):
            await app.State.check_integration.fn(state)
            self.assertEqual(state.integration_status, "error")
            await app.State.check_integration.fn(state)

        self.assertEqual(state.integration_status, "success")
        self.assertEqual(state.integration_payload,
                         json.dumps(EXPECTED, sort_keys=True))


class IntegrationHealthContractTests(unittest.TestCase):
    def test_backend_health_definition_is_domain_free(self):
        health = Path("xano/api/integration/health_GET.xs").read_text(encoding="utf-8")
        self.assertIn('status: "ok"', health)
        self.assertIn('service: "voltix-xano"', health)
        self.assertIn('integration: "available"', health)
        self.assertNotIn("auth =", health)
        self.assertNotIn("db.", health)
        self.assertNotIn("table", health)

    def test_health_request_carries_no_domain_data(self):
        with patch.object(app.urllib.request, "urlopen",
                          return_value=FakeResponse(EXPECTED)) as urlopen:
            app._request_xano_health(HEALTH_URL)
        request = urlopen.call_args.args[0]
        self.assertIsNone(request.data)
        self.assertIsNone(request.get_header("Authorization"))
        self.assertIsNone(request.get_header("Cookie"))


if __name__ == "__main__":
    unittest.main()
