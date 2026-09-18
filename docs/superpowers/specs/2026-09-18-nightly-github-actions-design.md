# Nightly GitHub Actions Photobook Refresh Design

## Goal

Refresh and publish the current year's photobook every day at 21:00 Asia/Shanghai without exposing credentials or replacing a healthy public book with an incomplete build.

## Workflow

The source repository owns one workflow triggered by `schedule` at `0 13 * * *` (21:00 China Standard Time) and by `workflow_dispatch`. It checks out `main`, installs Python dependencies, restores the already-public photo assets from the current `gh-pages` branch into the ignored local photo cache, fetches fresh Strava activity summaries, builds the current year, validates the result, and force-updates `gh-pages` only after every gate passes. Concurrency is limited to one refresh; a newer manual or scheduled run cancels an older one.

## Credentials

Repository Actions secrets hold `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, and `STRAVA_REFRESH_TOKEN`. Strava rotates refresh tokens, so the fetch step immediately writes the latest token back to `STRAVA_REFRESH_TOKEN` using a fourth secret, `SECRETS_ADMIN_TOKEN`, before continuing. The built-in `GITHUB_TOKEN` receives only `contents: write` and pushes the generated static site; no GitHub personal token enters the generated book. Secrets are piped over standard input and never printed.

## Safety Gates

The workflow compares the new book against the previous public book. If the previous deployment has photos, the rebuilt book must contain at least the same number, up to the configured 40-photo cap. It must also contain the project marker, no blank endpapers, no broken asset references, a month timeline, and no internal folios. Any failure stops before the publish step and leaves the existing Pages site untouched.

## Publishing

Publishing uses a temporary `gh-pages` worktree and the workflow's built-in token. The generated `books/<current-year>/` directory replaces the branch root in one commit. GitHub Pages remains configured to serve `/` from `gh-pages`, preserving the existing public URL.

## Operations

The README documents required secrets, the UTC-to-China-time conversion, manual dispatch, log inspection, token rotation, and how to disable the schedule. A workflow contract test protects the cron, permissions, concurrency, validation-before-publish ordering, and secret names.
