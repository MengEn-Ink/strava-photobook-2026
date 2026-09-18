"""自带的 Strava API 客户端（OAuth refresh-token 流程）。

除 `requests` 外无第三方依赖。自动刷新 access token（Strava 会轮换 refresh token，
故用一个本地缓存），并暴露所需接口：活动概要、活动详情（赛段/PR）、
以及返回原图 URL 的活动照片接口。
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterator

import requests

AUTH_URL = "https://www.strava.com/oauth/token"
API_BASE = "https://www.strava.com/api/v3"


class StravaError(RuntimeError):
    pass


class StravaClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        token_cache: str | Path | None = None,
    ) -> None:
        self.client_id = str(client_id)
        self.client_secret = str(client_secret)
        self.refresh_token = str(refresh_token)
        self.token_cache = Path(token_cache) if token_cache else None
        self._access_token = ""
        self._expires_at = 0.0
        self._load_cache()

    @property
    def ready(self) -> bool:
        return bool(self.client_id and self.client_secret and self.refresh_token)

    # ---- token handling ----
    def _load_cache(self) -> None:
        if not self.token_cache or not self.token_cache.is_file():
            return
        try:
            cached = json.loads(self.token_cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if str(cached.get("client_id")) != self.client_id:
            return
        self.refresh_token = str(cached.get("refresh_token") or self.refresh_token)
        self._access_token = str(cached.get("access_token") or "")
        self._expires_at = float(cached.get("expires_at") or 0)

    def _write_cache(self) -> None:
        if not self.token_cache:
            return
        self.token_cache.parent.mkdir(parents=True, exist_ok=True)
        self.token_cache.write_text(
            json.dumps(
                {
                    "client_id": self.client_id,
                    "access_token": self._access_token,
                    "refresh_token": self.refresh_token,
                    "expires_at": self._expires_at,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        try:
            self.token_cache.chmod(0o600)
        except OSError:
            pass

    def _token(self) -> str:
        if self._access_token and time.time() < self._expires_at - 60:
            return self._access_token
        resp = requests.post(
            AUTH_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=20,
        )
        if resp.status_code != 200:
            raise StravaError(
                f"token refresh failed ({resp.status_code}): {resp.text[:200]}"
            )
        body = resp.json()
        self._access_token = body["access_token"]
        self.refresh_token = str(body.get("refresh_token") or self.refresh_token)
        self._expires_at = float(body.get("expires_at", time.time() + 3600))
        self._write_cache()
        return self._access_token

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        resp = requests.get(
            f"{API_BASE}{path}",
            headers={"Authorization": f"Bearer {self._token()}"},
            params=params or {},
            timeout=30,
        )
        if resp.status_code == 429:
            raise StravaError("rate limited (429): wait 15 min or reduce scope")
        if resp.status_code != 200:
            raise StravaError(f"GET {path} -> {resp.status_code}: {resp.text[:200]}")
        return resp.json()

    # ---- endpoints ----
    def athlete(self) -> dict[str, Any]:
        return self._get("/athlete")

    def iter_activities(
        self, per_page: int = 200, pause: float = 1.0, *, after: int | None = None,
        before: int | None = None,
    ) -> Iterator[dict]:
        """Yield every activity summary, page by page (cheap: 1 req / 200 acts)."""
        page = 1
        while True:
            params = {"per_page": per_page, "page": page}
            if after is not None:
                params["after"] = after
            if before is not None:
                params["before"] = before
            batch = self._get("/athlete/activities", params=params)
            if not batch:
                return
            yield from batch
            page += 1
            time.sleep(pause)

    def activity_detail(self, activity_id: int | str) -> dict[str, Any]:
        return self._get(
            f"/activities/{activity_id}", params={"include_all_efforts": "true"}
        )

    def activity_photos(self, activity_id: int | str, size: int = 2000) -> list[dict]:
        """Full-size photo objects for an activity (urls, caption, timestamps)."""
        return self._get(
            f"/activities/{activity_id}/photos",
            params={"size": size, "photo_sources": "true"},
        )

    @staticmethod
    def download(url: str, dest: Path) -> bool:
        """Download a public CDN photo URL to dest. Returns success."""
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                return False
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(resp.content)
            return True
        except requests.RequestException:
            return False
