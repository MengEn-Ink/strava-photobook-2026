"""一次性本地 OAuth，获取 Strava refresh token。

在 localhost 上起一个临时 HTTP 服务，打开 Strava 授权页，捕获回调里的 `code`，
再换成 refresh token。用户只需一个 Strava API 应用的 client id + secret
（在 https://www.strava.com/settings/api 创建一次，回调域填 `localhost`）。
"""
from __future__ import annotations

import http.server
import socket
import threading
import urllib.parse
import webbrowser

import requests

from .client import AUTH_URL

# Scopes: read activities (incl. private), profile — enough for photos + PRs.
SCOPE = "read,activity:read_all,profile:read_all"


def _free_port(preferred: int = 8721) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


class _Handler(http.server.BaseHTTPRequestHandler):
    code: str | None = None

    def do_GET(self):  # noqa: N802
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _Handler.code = (params.get("code") or [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        ok = _Handler.code is not None
        msg = "授权成功，可以关闭此页面返回终端。" if ok else "未收到授权码，请重试。"
        self.wfile.write(f"<html><body style='font:16px sans-serif;padding:3em'>{msg}</body></html>".encode())

    def log_message(self, *args):  # silence
        pass


def authorize(client_id: str, client_secret: str, timeout: int = 180) -> dict:
    """Interactive browser authorization. Returns the token JSON from Strava."""
    port = _free_port()
    redirect = f"http://localhost:{port}"
    auth_link = (
        "https://www.strava.com/oauth/authorize?"
        + urllib.parse.urlencode(
            {
                "client_id": client_id,
                "redirect_uri": redirect,
                "response_type": "code",
                "approval_prompt": "auto",
                "scope": SCOPE,
            }
        )
    )

    server = http.server.HTTPServer(("127.0.0.1", port), _Handler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    print(f"打开浏览器授权（若未自动打开，请手动访问）：\n{auth_link}\n")
    try:
        webbrowser.open(auth_link)
    except Exception:  # noqa: BLE001
        pass

    thread.join(timeout=timeout)
    server.server_close()
    code = _Handler.code
    if not code:
        raise RuntimeError("未获得授权码（超时或被拒绝）")

    resp = requests.post(
        AUTH_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()
