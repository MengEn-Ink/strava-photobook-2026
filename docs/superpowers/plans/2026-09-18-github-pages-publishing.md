# GitHub Pages Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add native GitHub Device Flow authorization and a single command that publishes a generated yearly photobook to a verified public GitHub Pages URL.

**Architecture:** A small GitHub package separates HTTP transport, OAuth polling, and publication orchestration. The CLI remains a thin adapter, while fake-server unit tests drive every remote behavior before implementation.

**Tech Stack:** Python 3.9 standard library, `requests`, GitHub REST API, `unittest`, Node test runner for the existing runtime contract.

---

## File map

- Create `strava_photobook/github/__init__.py`: public GitHub integration exports.
- Create `strava_photobook/github/client.py`: typed GitHub REST requests and sanitized API errors.
- Create `strava_photobook/github/oauth.py`: Device Flow authorization state machine.
- Create `strava_photobook/github/publisher.py`: repository, Git tree, Pages, deployment, and public-site orchestration.
- Create `tests/test_github_client.py`: client and repository API tests.
- Create `tests/test_github_oauth.py`: Device Flow tests.
- Create `tests/test_github_publisher.py`: publication and Pages state-machine tests.
- Create `tests/test_cli.py`: CLI parsing and dispatch tests.
- Modify `strava_photobook/config.py`: GitHub configuration and credential precedence.
- Modify `strava_photobook/cli.py`: `github-auth` and `publish` commands.
- Modify `.env.example`, `.gitignore`, and `README.md`: safe setup and usage documentation.

### Task 1: Configuration and credential policy

**Files:**
- Modify: `strava_photobook/config.py`
- Test: `tests/test_github_client.py`

- [ ] **Step 1: Write failing configuration tests**

Add tests that construct an isolated root and assert `GH_TOKEN` overrides `.env` `GITHUB_TOKEN`, the default API URL is `https://api.github.com`, and no token yields an empty credential.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_github_client -v`
Expected: FAIL because `GitHubConfig` and `Config.github` do not exist.

- [ ] **Step 3: Implement configuration**

Add `GitHubConfig(client_id, token, api_url, upload_limit_bytes)` and load it in `Config.load`. Keep `GH_TOKEN` first in precedence and do not expose secrets in `repr`.

- [ ] **Step 4: Verify GREEN**

Run the same test and expect PASS.

### Task 2: GitHub REST client

**Files:**
- Create: `strava_photobook/github/__init__.py`
- Create: `strava_photobook/github/client.py`
- Test: `tests/test_github_client.py`

- [ ] **Step 1: Write failing fake-server tests**

Cover JSON requests, empty successful responses, accepted status sets, GitHub error messages, authorization headers, and absence of token text in raised errors.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_github_client -v`
Expected: FAIL because `GitHubClient` is missing.

- [ ] **Step 3: Implement minimal client**

Implement `request(method, path, json_body=None, expected=(200,))`, consistent headers, timeouts, response JSON parsing, and `GitHubAPIError(status, method, path, message)`.

- [ ] **Step 4: Verify GREEN**

Run the client tests and expect PASS.

### Task 3: Device Flow

**Files:**
- Create: `strava_photobook/github/oauth.py`
- Test: `tests/test_github_oauth.py`

- [ ] **Step 1: Write failing state-machine tests**

Use a scripted fake client and fake clock to cover immediate success, `authorization_pending`, `slow_down`, `access_denied`, and `expired_token`. Assert the browser opener receives GitHub's verification URI.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_github_oauth -v`
Expected: FAIL because `authorize_device` is missing.

- [ ] **Step 3: Implement Device Flow**

POST `/login/device/code` with `client_id` and `scope=repo`, show the user code, open `verification_uri`, and poll `/login/oauth/access_token` using the server interval until a token or terminal error.

- [ ] **Step 4: Verify GREEN**

Run the OAuth tests and expect PASS.

### Task 4: Repository and atomic branch publication

**Files:**
- Create: `strava_photobook/github/publisher.py`
- Test: `tests/test_github_publisher.py`

- [ ] **Step 1: Write failing repository safety tests**

Cover repository creation, reuse with the marker, refusal without the marker, file path validation, oversized file rejection, and exclusion of anything outside the selected book directory.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_github_publisher -v`
Expected: FAIL because `Publisher` is missing.

- [ ] **Step 3: Implement repository resolution and tree assembly**

Resolve `/user`, GET or POST `/user/repos`, validate the marker, base64-encode each regular file as a blob, create a tree, create a commit with the existing `gh-pages` commit as parent when present, then create or force-update `refs/heads/gh-pages`.

- [ ] **Step 4: Verify GREEN**

Run the publisher tests and expect PASS.

### Task 5: Pages configuration and end-to-end verification

**Files:**
- Modify: `strava_photobook/github/publisher.py`
- Test: `tests/test_github_publisher.py`

- [ ] **Step 1: Write failing Pages tests**

Cover absent Pages creation, wrong-source correction, already-correct no-op, build success/failure/timeout, and final HTML marker success/mismatch.

- [ ] **Step 2: Verify RED**

Run the targeted tests and confirm the expected missing behavior.

- [ ] **Step 3: Implement Pages and verification states**

Use `/repos/{owner}/{repo}/pages` with source `gh-pages` and `/`, poll `/pages/builds/latest`, then poll the returned public URL for a 2xx response containing `data-strava-photobook`. Return a `PublishResult(repo_url, pages_url, commit_sha)`.

- [ ] **Step 4: Verify GREEN**

Run all publisher tests and expect PASS.

### Task 6: CLI integration and documentation

**Files:**
- Modify: `strava_photobook/cli.py`
- Modify: `.env.example`
- Modify: `README.md`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Assert `github-auth` requires a client ID, persists the returned token through `_update_env`, and `publish YEAR [--repo NAME]` validates the generated book before invoking the publisher.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_cli -v`
Expected: FAIL because the commands are not registered.

- [ ] **Step 3: Implement commands and docs**

Add the two subcommands, concise progress output, safe errors, `.env.example` keys, OAuth App setup, and the one-command publish flow. Add `data-strava-photobook` to generated HTML if the existing template lacks it.

- [ ] **Step 4: Verify GREEN**

Run the CLI tests and expect PASS.

### Task 7: Full local regression and real publication

**Files:**
- Verify all modified files and generated `books/2026/`.

- [ ] **Step 1: Run the complete local suite**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q strava_photobook
node --test runtime/html-contract.test.mjs
git diff --check
```

Expected: all tests pass and no whitespace errors.

- [ ] **Step 2: Authorize GitHub**

Run `python3 -m strava_photobook github-auth`. The user completes the browser Device Flow once. Confirm only `GITHUB_TOKEN` is added to ignored `.env`, with mode `0600`.

- [ ] **Step 3: Publish the real 2026 book**

Run `python3 -m strava_photobook publish 2026`. Expected: a public repository is created or safely reused, the `gh-pages` branch is updated, Pages reports success, and the URL passes marker verification.

- [ ] **Step 4: Independently verify the public URL**

Fetch the returned URL without authentication and confirm HTTP 2xx plus `data-strava-photobook`. Open it in a browser and verify the cover and page-turn runtime load.

- [ ] **Step 5: Commit and push project source**

Review `git status`, ensure `.env`, `data/`, and `books/` remain ignored, commit source/tests/docs, create or select the source repository, add `origin`, and push `main`. Report both source repository and published Pages URLs.
