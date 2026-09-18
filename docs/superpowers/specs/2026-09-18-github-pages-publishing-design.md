# GitHub Pages Publishing Design

## Goal

Add one friendly, resumable path from a locally generated yearly Strava photobook to a verified public GitHub Pages site:

```text
github-auth -> publish YEAR -> create/reuse repository -> upload book
            -> enable Pages -> wait for deployment -> verify public HTML
```

The command is successful only when the published URL responds successfully and contains the expected photobook marker.

## User Experience

GitHub Device Flow is the primary interactive authorization method because it does not require a localhost callback or a client secret. The user configures the public OAuth App client ID once, runs `python3 -m strava_photobook github-auth`, confirms a short code in the browser, and the resulting token is stored in `.env` with mode `0600`.

Automation may provide `GH_TOKEN`. Credential precedence is:

1. `GH_TOKEN` environment variable
2. `GITHUB_TOKEN` environment variable or `.env`
3. A clear instruction to run `github-auth`

Publishing uses:

```bash
python3 -m strava_photobook publish 2026
```

The default repository name is `strava-photobook-2026`. `--repo` may override it. The command prints progress without printing credentials, then prints the repository and Pages URLs.

## Architecture

`strava_photobook/github/client.py` owns authenticated GitHub REST calls and error normalization. It has no CLI or filesystem policy.

`strava_photobook/github/oauth.py` owns Device Flow: request a device code, open the verification page, poll for the access token, and respect GitHub's interval and expiry responses.

`strava_photobook/github/publisher.py` owns publishing orchestration. It validates the generated book, resolves the current GitHub user, creates or verifies the repository, creates a Git tree and commit for the static book, updates `refs/heads/gh-pages`, configures Pages, polls deployment, and verifies the public document.

`strava_photobook/cli.py` only parses `github-auth` and `publish` arguments, loads configuration, and presents progress/results.

## Repository Ownership and Idempotency

New public repositories are created with a deterministic description marker:

```text
[strava-photobook] Published by the local Strava Photobook tool.
```

An existing repository is reusable only when all of these match:

- its owner is the authenticated GitHub user;
- its name exactly matches the requested name;
- its description contains the marker.

Otherwise publishing stops before changing repository content. This prevents accidental takeover of an unrelated same-name repository.

The published branch is isolated from source code. The tool writes only the generated `books/<year>/` contents to `gh-pages`. It uses the Git Data API to create blobs, one tree, and one commit, then atomically creates or updates the branch ref. A repeat run replaces the published tree without creating per-file commits. Secrets, `data/`, source files, and local configuration are never included.

## Pages Configuration

Pages uses branch publishing with source `{branch: gh-pages, path: /}`. The publisher handles three states:

- Pages absent: create it with the required source.
- Pages present with a different source: update it.
- Pages already correct: leave it unchanged.

After configuration, the publisher polls the latest Pages build until success, failure, or timeout. It then requests the reported Pages URL until it receives a 2xx HTML response containing `data-strava-photobook`. The build and HTTP checks use bounded exponential backoff and honor cancellation.

## Failure Behavior

All operations are safe to rerun. If repository creation succeeds but a later step fails, the repository is preserved for recovery; the tool does not automatically delete external resources. Errors identify the failed phase and include safe repository or Pages URLs when available. Tokens and authenticated request headers are never included in logs or exceptions.

Device Flow handles `authorization_pending`, `slow_down`, expiration, denial, and network failures explicitly. Publishing distinguishes repository conflicts, permission failures, Pages plan/visibility restrictions, deployment failures, and public verification timeouts.

## Configuration

The following values are added:

- `GITHUB_CLIENT_ID`: public OAuth App client ID used by Device Flow.
- `GITHUB_TOKEN`: persisted Device Flow token.
- `GH_TOKEN`: non-persisted automation override.
- `GITHUB_API_URL`: optional API base for tests or GitHub Enterprise; defaults to `https://api.github.com`.
- `GITHUB_UPLOAD_LIMIT_BYTES`: defensive per-file limit, defaulting above the current generated asset size but below GitHub's hard blob limit.

The OAuth App must have Device Flow enabled. The requested classic OAuth scope is `repo`, which covers public/private repository content and Pages administration. The default publish path creates a public repository.

## Tests

Tests use the standard library `unittest` and a local fake HTTP server; no real GitHub writes occur in the automated suite. Test-first coverage includes:

- Device Flow success, pending, slow-down, denial, and expiry;
- credential precedence and secure `.env` persistence;
- new repository creation and safe existing-repository reuse/refusal;
- blob/tree/commit/ref creation and repeat publication;
- Pages create, source correction, already-correct state, deployment failure, and timeout;
- final URL verification, including marker mismatch;
- CLI argument routing and actionable errors.

The existing Python compile check and Node runtime contract suite remain green. Final acceptance performs one real Device Flow authorization, publishes `books/2026` to a public GitHub repository, waits for deployment, and opens the returned Pages URL successfully.

## Explicit Non-goals

- No hosted backend or web dashboard.
- No GitHub App installation flow.
- No upload of Strava tokens, raw activity cache, or project source.
- No destructive cleanup of repositories created during partial failures.
- No support for arbitrary Pages workflows in this iteration.
