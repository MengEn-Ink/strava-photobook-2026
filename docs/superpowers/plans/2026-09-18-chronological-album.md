# Chronological Album and Concise Captions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Present selected activity blocks from January through December and remove nonessential editorial labels from photo captions.

**Architecture:** Keep candidate scoring and selection intact, merge featured and gallery selections into one deterministically sorted timeline, then render each activity block in order. Keep the photo renderer responsible only for factual caption metadata.

**Tech Stack:** Python 3 standard library, `unittest`, static HTML, existing GitHub Pages publisher.

---

### Task 1: Lock caption and ordering behavior

**Files:**
- Modify: `tests/test_book.py`
- Modify: `tests/test_model.py`

- [ ] Change the photo-page assertion to require activity title, date, distance, elevation, and optional caption while rejecting the editorial reason.
- [ ] Add a build-level test with out-of-order activities and assert their `data-activity-id` markers appear in ascending date order with each featured introduction immediately before its photos.
- [ ] Run the focused tests and verify they fail because current rendering includes the reason and current build order follows ranking.

### Task 2: Render one chronological activity timeline

**Files:**
- Modify: `strava_photobook/book.py`
- Modify: `strava_photobook/model.py`

- [ ] Remove `photo-kicker` from `_activity_photo_page`.
- [ ] Replace the verbose photo-story reason with `影像记录`.
- [ ] Merge featured and remaining selected activities, sort by `(activity.date, activity.id)`, and render each activity block without separating highlights from the gallery.
- [ ] Number photo folios sequentially in rendered order and keep the configured photo limit.
- [ ] Run focused tests and verify they pass.

### Task 3: Regress, regenerate, and publish

**Files:**
- Regenerate ignored output: `books/2026/`

- [ ] Run all Python, Node, generated-contract, layout, compile, and diff checks.
- [ ] Build 2026 and verify activity markers are date-sorted and the removed phrase is absent.
- [ ] Commit source and documentation changes, publish `books/2026` to `gh-pages`, and push `main`.
- [ ] Open the public Pages URL in fresh desktop and mobile browser sessions; verify photos load, chronology starts at the earliest selected month, captions are concise, and no overflow appears.
