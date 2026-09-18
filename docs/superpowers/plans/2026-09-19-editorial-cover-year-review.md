# Editorial Cover and Year Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the plain cover and statistics list with a theme-aware photographic poster cover and a two-page annual review, while preserving the existing photo, timeline, and publishing guarantees.

**Architecture:** A new `editorial.py` module computes a deterministic `CoverSelection` and `YearReview` from hydrated activities. `book.py` consumes those presentation-neutral values to render the cover and two review pages; `theme.py` owns the layout and visual treatment.

**Tech Stack:** Python standard library and dataclasses, Pillow-backed local image metadata already available in the project, static HTML/CSS, unittest, Node HTML contract tests.

---

### Task 1: Cover selection model

**Files:**
- Create: `strava_photobook/editorial.py`
- Create: `tests/test_editorial.py`

- [ ] Write a failing test with landscape and portrait photos proving `select_cover()` chooses the landscape photo from the stronger editorial activity and returns its activity title.
- [ ] Run `python3 -m unittest tests.test_editorial -v`; expect an import failure for the missing module.
- [ ] Implement immutable `CoverSelection(photo, activity, object_position)` plus a deterministic score using photo orientation, Kudos, PR, distance, elevation, and meaningful title. Return `None` for no photos.
- [ ] Add and pass a second test proving equal-score input is stable by activity date and ID.
- [ ] Commit `feat(book): select editorial cover photos`.

### Task 2: Annual review data

**Files:**
- Modify: `strava_photobook/editorial.py`
- Modify: `tests/test_editorial.py`

- [ ] Write failing tests for monthly distance ordering, active-month count, peak month, longest ride, total moving hours, Kudos, and PR.
- [ ] Run the focused test and verify the failure is caused by missing `build_year_review()`.
- [ ] Implement immutable `MonthReview` and `YearReview` values; compute month buckets 1 through 12 from the activity dates and keep only active months for display.
- [ ] Run the focused tests and commit `feat(book): calculate annual review narrative`.

### Task 3: Poster cover and fallback

**Files:**
- Modify: `tests/test_book.py`
- Modify: `strava_photobook/book.py`

- [ ] Write failing render tests requiring `data-cover-mode="photo"`, a local cover image, bounded activity title, yearly metrics, and `data-cover-mode="route"` when no selection exists.
- [ ] Run `python3 -m unittest tests.test_book -v` and confirm the old plain cover fails the contract.
- [ ] Replace `_cover()` with a renderer accepting `CoverSelection | None`, `YearReview`, and route SVG. The fallback must contain no image element.
- [ ] Pass the focused tests and commit `feat(book): render photographic poster cover`.

### Task 4: Two-page annual review

**Files:**
- Modify: `tests/test_book.py`
- Modify: `strava_photobook/book.py`

- [ ] Write failing tests requiring exactly one `year-declaration` page and one `year-rhythm` page, month bars from real distances, one peak marker, bounded longest-ride text, and removal of the old title/stat pages.
- [ ] Implement `_year_declaration_page()` and `_year_rhythm_page()` and place them before the annual route heatmap.
- [ ] Run the focused tests and commit `feat(book): add annual review spread`.

### Task 5: Theme and safety contracts

**Files:**
- Modify: `strava_photobook/theme.py`
- Modify: `tests/test_layout_gate.py`
- Modify: `tools/validate_release.py`
- Modify: `tests/test_validate_release.py`

- [ ] Add failing checks for the 68-74% cover image band, independent dark photo overlay, theme variables, safe text bounds, month bars, peak accent, and required cover/review markers.
- [ ] Add the poster and annual-review CSS using only existing theme variables; include portrait-layout overrides where the desktop spread assumptions differ.
- [ ] Require one valid cover mode and both annual-review pages in release validation.
- [ ] Run focused tests and commit `style(book): polish poster and annual review`.

### Task 6: Build and publish verification

**Files:**
- Modify: `README.md`
- Modify: `docs/setup.md`
- Regenerate: `books/2026/*` (ignored output)

- [ ] Document the automatic poster selection, route fallback, and new reading order.
- [ ] Build 2026 and run Python unit tests, runtime Node tests, generated HTML contract, layout gate, and release validator.
- [ ] Inspect 1440×900 and 390×844 in one dark and one light theme; verify no overflow and the page order cover → declaration → rhythm → heatmap.
- [ ] Commit documentation, push `main`, publish atomically to `gh-pages`, and verify 40 photos, required markers, month timeline, and no blank pages on the public URL.
