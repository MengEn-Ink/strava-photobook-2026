import unittest

from strava_photobook.github.oauth import DeviceAuthorizationError, authorize_device


class FakeClient:
    def __init__(self, replies):
        self.replies = iter(replies)

    def request(self, *args, **kwargs):
        return next(self.replies)


class DeviceFlowTests(unittest.TestCase):
    def test_pending_then_success(self):
        client = FakeClient([
            {"device_code": "d", "user_code": "ABCD", "verification_uri": "https://github.com/login/device", "interval": 0, "expires_in": 60},
            {"error": "authorization_pending"},
            {"access_token": "token", "token_type": "bearer"},
        ])
        opened = []
        result = authorize_device("client", client=client, opener=opened.append, sleeper=lambda _: None)
        self.assertEqual(result, "token")
        self.assertEqual(opened, ["https://github.com/login/device"])

    def test_denial_is_terminal(self):
        client = FakeClient([
            {"device_code": "d", "user_code": "ABCD", "verification_uri": "https://github.com/login/device", "interval": 0, "expires_in": 60},
            {"error": "access_denied"},
        ])
        with self.assertRaises(DeviceAuthorizationError):
            authorize_device("client", client=client, opener=lambda _: None, sleeper=lambda _: None)
