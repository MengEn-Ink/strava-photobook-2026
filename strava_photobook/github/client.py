from __future__ import annotations

from typing import Any, Iterable

import requests


class GitHubAPIError(RuntimeError):
    def __init__(self, status: int, method: str, path: str, message: str):
        self.status = status
        super().__init__(f"GitHub {method} {path} failed ({status}): {message}")


class GitHubClient:
    def __init__(self, token: str = "", api_url: str = "https://api.github.com", session=None):
        self.token = token
        self.api_url = api_url.rstrip("/")
        self.session = session or requests.Session()

    def request(
        self, method: str, path: str, *, json_body: Any = None,
        data: Any = None, expected: Iterable[int] = (200,), headers: dict[str, str] | None = None,
    ) -> Any:
        request_headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "strava-photobook",
        }
        if self.token:
            request_headers["Authorization"] = f"Bearer {self.token}"
        if headers:
            request_headers.update(headers)
        url = path if path.startswith("http") else self.api_url + path
        response = self.session.request(
            method=method, url=url, headers=request_headers, json=json_body, data=data, timeout=30
        )
        if response.status_code not in tuple(expected):
            try:
                message = response.json().get("message", "request failed")
            except Exception:
                message = "request failed"
            raise GitHubAPIError(response.status_code, method, path, str(message))
        if response.status_code == 204 or not response.text:
            try:
                return response.json()
            except Exception:
                return None
        return response.json()

