# Nightly GitHub Actions Photobook Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Safely rebuild and publish the current-year photobook every night at 21:00 Asia/Shanghai.

**Architecture:** A scheduled GitHub Actions workflow restores public photo cache, refreshes Strava data and rotating credentials, runs a standalone release validator, then atomically replaces `gh-pages`. Tests inspect workflow invariants and validator behavior.

**Tech Stack:** GitHub Actions YAML, Python 3, shell, Git, GitHub CLI, existing photobook CLI.

---

### Task 1: Validate generated releases

**Files:**
- Create: `tools/validate_release.py`
- Create: `tests/test_validate_release.py`

- [ ] Write failing tests for photo regression, blank endpapers, missing timeline, internal folios, and missing local assets.
- [ ] Implement a dependency-free HTML release validator with a CLI accepting the new book and optional baseline book.
- [ ] Run focused tests until green.

### Task 2: Add the scheduled workflow

**Files:**
- Create: `.github/workflows/nightly-photobook.yml`
- Create: `tests/test_workflow.py`

- [ ] Write a failing contract test for `0 13 * * *`, manual dispatch, concurrency, least-privilege contents access, four required secrets, immediate refresh-token persistence, validation before publish, and `gh-pages` push.
- [ ] Implement the workflow with safe temporary directories and explicit branch targets.
- [ ] Run focused tests until green.

### Task 3: Document and configure

**Files:**
- Modify: `README.md`
- Modify: `docs/setup.md`
- Modify: `tests/test_docs.py`

- [ ] Add beginner instructions for secrets, daily timing, manual runs, logs, disabling, and recovery.
- [ ] Configure repository secrets from the existing local authorized values without displaying them.
- [ ] Enable and manually dispatch the workflow.

### Task 4: Verify end to end

- [ ] Run all Python, Node, layout, compile, diff, and workflow contract tests.
- [ ] Observe the manual Actions run through build and deployment.
- [ ] Verify Pages remains public with 51 pages, 40 photos, timeline controls, and no blank endpapers.
- [ ] Commit and push `main`; report the workflow URL and next scheduled run.
