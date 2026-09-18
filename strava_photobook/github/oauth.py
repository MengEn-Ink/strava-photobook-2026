from __future__ import annotations

import time
import webbrowser

from .client import GitHubClient


class DeviceAuthorizationError(RuntimeError):
    pass


def authorize_device(client_id: str, *, client=None, opener=webbrowser.open, sleeper=time.sleep, announce=print) -> str:
    if not client_id.strip():
        raise DeviceAuthorizationError("GITHUB_CLIENT_ID is required")
    client = client or GitHubClient(api_url="https://github.com")
    common = {"headers": {"Accept": "application/json"}, "expected": (200,)}
    device = client.request(
        "POST", "/login/device/code", data={"client_id": client_id, "scope": "repo"}, **common
    )
    announce(f"请在 {device['verification_uri']} 输入验证码：{device['user_code']}")
    opener(device["verification_uri"])
    interval = max(0, int(device.get("interval", 5)))
    while True:
        sleeper(interval)
        result = client.request(
            "POST", "/login/oauth/access_token",
            data={
                "client_id": client_id,
                "device_code": device["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            **common,
        )
        if result.get("access_token"):
            return result["access_token"]
        error = result.get("error")
        if error == "authorization_pending":
            continue
        if error == "slow_down":
            interval += 5
            continue
        raise DeviceAuthorizationError(result.get("error_description") or error or "GitHub authorization failed")

