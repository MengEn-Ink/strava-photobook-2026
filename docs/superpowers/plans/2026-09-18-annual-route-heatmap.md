# Annual Route Heatmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a theme-aware annual Strava route heatmap immediately after the title page without external map dependencies.

**Architecture:** Extend the existing route module with a pure multi-polyline SVG renderer. The book renderer conditionally inserts one semantic heatmap page, and existing CSS variables provide all theme colors.

**Tech Stack:** Python standard library, inline SVG, HTML/CSS, unittest.

---

### Task 1: Define the aggregate SVG contract

**Files:**
- Modify: `tests/test_route.py`
- Modify: `strava_photobook/route.py`

- [ ] Write tests proving multiple valid polylines share one SVG, malformed input is skipped, CSS theme variables are used, and no valid input returns an empty string.
- [ ] Run `python -m unittest tests.test_route -v` and verify the new tests fail for the missing API.
- [ ] Implement `route_heatmap_svg(encoded_routes)` using the existing decoder and one shared projection bounds calculation.
- [ ] Run `python -m unittest tests.test_route -v` and verify it passes.

### Task 2: Define the page contract

**Files:**
- Modify: `tests/test_book.py`
- Modify: `strava_photobook/book.py`

- [ ] Write tests proving the heatmap follows the title page, contains compact annual metrics, and disappears when no valid routes exist.
- [ ] Run `python -m unittest tests.test_book -v` and verify the new tests fail.
- [ ] Add `_heatmap_page` and pass yearly activities into `_frame_pages`; render only when aggregate SVG is non-empty.
- [ ] Run `python -m unittest tests.test_book -v` and verify it passes.

### Task 3: Style and release-gate the page

**Files:**
- Modify: `strava_photobook/theme.py`
- Modify: `tests/test_layout_gate.py`
- Modify: `tools/validate_release.py`
- Modify: `tests/test_validate_release.py`

- [ ] Write failing tests for safe page bounds, hidden overflow, theme variables, and the generated heatmap marker.
- [ ] Add a restrained editorial layout with the SVG as the dominant visual and a three-item summary strip.
- [ ] Update release validation so generated candidates with route data cannot silently lose the heatmap page.
- [ ] Run the focused Python tests and confirm they pass.

### Task 4: Rebuild, regress, and publish

**Files:**
- Regenerate: `books/2026/*`

- [ ] Run `python -m strava_photobook build 2026`.
- [ ] Run `python -m unittest discover -v`, `node --test runtime/*.test.mjs`, the generated HTML contract test, layout gate, and release validator.
- [ ] Commit the source, tests, design, and plan; push `main`.
- [ ] Run the nightly workflow manually and verify the public Pages output contains the heatmap, all 40 photos, the month timeline, and no blank pages.
