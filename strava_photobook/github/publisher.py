from __future__ import annotations

import base64
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from .client import GitHubAPIError


MARKER = "[strava-photobook]"
HTML_MARKER = "data-strava-photobook"


class PublishError(RuntimeError):
    pass


@dataclass
class PublishResult:
    repo_url: str
    pages_url: str
    commit_sha: str


class Publisher:
    def __init__(self, client, *, upload_limit_bytes=50 * 1024 * 1024, sleeper=time.sleep, public_fetch=None):
        self.client = client
        self.upload_limit_bytes = upload_limit_bytes
        self.sleeper = sleeper
        self.public_fetch = public_fetch or self._public_fetch

    def publish(self, book_dir: Path, repo_name: str) -> PublishResult:
        book_dir = Path(book_dir)
        index = book_dir / "index.html"
        if not index.is_file() or HTML_MARKER not in index.read_text("utf-8"):
            raise PublishError(f"invalid photobook: {index} is missing {HTML_MARKER}")
        files = sorted(path for path in book_dir.rglob("*") if path.is_file())
        for path in files:
            if len(path.read_bytes()) > self.upload_limit_bytes:
                raise PublishError(f"file exceeds upload limit: {path.relative_to(book_dir)}")
        login = self.client.request("GET", "/user")["login"]
        repo_path = f"/repos/{login}/{repo_name}"
        try:
            repo = self.client.request("GET", repo_path)
        except GitHubAPIError as error:
            if error.status != 404:
                raise
            repo = None
        if repo is None:
            repo = self.client.request(
                "POST", "/user/repos",
                json_body={"name": repo_name, "description": f"{MARKER} Public cycling photobook", "private": False},
                expected=(201,),
            )
        elif repo.get("owner", {}).get("login") != login or MARKER not in (repo.get("description") or ""):
            raise PublishError(f"refusing to overwrite unowned or unmarked repository {login}/{repo_name}")
        commit_sha = self._publish_branch(book_dir, files, login, repo_name)
        pages_url = self._ensure_pages(login, repo_name)
        self._wait_for_pages(login, repo_name)
        self._verify_public(pages_url)
        return PublishResult(repo.get("html_url", f"https://github.com/{login}/{repo_name}"), pages_url, commit_sha)

    def _publish_branch(self, root: Path, files: list[Path], owner: str, repo: str) -> str:
        prefix = f"/repos/{owner}/{repo}"
        parent_sha = None
        try:
            ref = self.client.request("GET", prefix + "/git/ref/heads/gh-pages")
            if ref:
                parent_sha = ref["object"]["sha"]
        except GitHubAPIError as error:
            if error.status not in (404, 409):
                raise
            ref = None
            if error.status == 409:
                self.client.request(
                    "PUT", prefix + "/contents/.strava-photobook",
                    json_body={
                        "message": "Initialize repository for Pages publishing",
                        "content": base64.b64encode(MARKER.encode()).decode("ascii"),
                    },
                    expected=(201,),
                )
                parent_sha = self.client.request("GET", prefix + "/git/ref/heads/main")["object"]["sha"]
        tree = []
        for path in files:
            raw = path.read_bytes()
            blob = self.client.request(
                "POST", prefix + "/git/blobs",
                json_body={"content": base64.b64encode(raw).decode("ascii"), "encoding": "base64"}, expected=(201,),
            )
            tree.append({"path": path.relative_to(root).as_posix(), "mode": "100644", "type": "blob", "sha": blob["sha"]})
        tree_sha = self.client.request("POST", prefix + "/git/trees", json_body={"tree": tree}, expected=(201,))["sha"]
        body = {"message": "Publish Strava photobook", "tree": tree_sha}
        if parent_sha:
            body["parents"] = [parent_sha]
        commit = self.client.request("POST", prefix + "/git/commits", json_body=body, expected=(201,))
        if ref:
            self.client.request("PATCH", prefix + "/git/refs/heads/gh-pages", json_body={"sha": commit["sha"], "force": True}, expected=(200,))
        else:
            self.client.request("POST", prefix + "/git/refs", json_body={"ref": "refs/heads/gh-pages", "sha": commit["sha"]}, expected=(201,))
        return commit["sha"]

    def _ensure_pages(self, owner: str, repo: str) -> str:
        path = f"/repos/{owner}/{repo}/pages"
        desired = {"branch": "gh-pages", "path": "/"}
        try:
            pages = self.client.request("GET", path)
        except GitHubAPIError as error:
            if error.status != 404:
                raise
            pages = None
        if pages is None:
            try:
                pages = self.client.request("POST", path, json_body={"source": desired}, expected=(201,)) or {}
            except GitHubAPIError as error:
                if error.status != 409:
                    raise
                pages = self.client.request("GET", path)
                if pages.get("source") != desired:
                    self.client.request("PUT", path, json_body={"source": desired}, expected=(204,))
                    pages = self.client.request("GET", path)
        elif pages.get("source") != desired:
            self.client.request("PUT", path, json_body={"source": desired}, expected=(204,))
            pages = self.client.request("GET", path)
        return pages.get("html_url") or f"https://{owner}.github.io/{repo}/"

    def _wait_for_pages(self, owner: str, repo: str, attempts: int = 30) -> None:
        path = f"/repos/{owner}/{repo}/pages/builds/latest"
        for attempt in range(attempts):
            build = self.client.request("GET", path)
            status = build.get("status")
            if status in ("built", "success"):
                return
            if status in ("errored", "error", "failed"):
                raise PublishError(f"GitHub Pages build failed: {status}")
            self.sleeper(min(2 ** attempt, 15))
        raise PublishError("timed out waiting for GitHub Pages build")

    def _verify_public(self, url: str, attempts: int = 20) -> None:
        for attempt in range(attempts):
            try:
                if HTML_MARKER in self.public_fetch(url):
                    return
            except requests.RequestException:
                pass
            self.sleeper(min(2 ** attempt, 15))
        raise PublishError(f"published page did not become ready: {url}")

    @staticmethod
    def _public_fetch(url: str) -> str:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.text
