# Month Timeline and External Page Status Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an accessible month jump timeline between flip buttons and remove photo-internal page numbers.

**Architecture:** Render month metadata and available-month buttons from the generated activity body. Put pure month-index helpers in a small runtime module, then let `flipbook.js` synchronize PageFlip with those controls. Keep the authoritative page count in the existing external footer status.

**Tech Stack:** Python 3 string rendering, vanilla JavaScript ES modules, CSS, `unittest`, Node test runner.

---

### Task 1: Render month metadata and timeline markup

**Files:**
- Modify: `tests/test_book.py`
- Modify: `strava_photobook/book.py`

- [ ] Add failing assertions for `data-month`, ordered unique month buttons, and no photo folio.
- [ ] Add `data-month` to feature and photo articles.
- [ ] Generate timeline buttons from months present in the body and place them above the footer status.
- [ ] Run focused Python tests until green.

### Task 2: Implement month navigation

**Files:**
- Create: `runtime/month-timeline.js`
- Create: `runtime/month-timeline.test.mjs`
- Modify: `runtime/flipbook.js`
- Modify: `runtime/html-contract.test.mjs`

- [ ] Test first-page indexing and active-month resolution, including non-activity pages.
- [ ] Implement the pure helpers and import them from `flipbook.js`.
- [ ] Wire month clicks to `turnToPage` and update `aria-current` on every flip.
- [ ] Verify Node tests pass.

### Task 3: Style, regenerate, and publish

**Files:**
- Modify: `runtime/styles.css`
- Modify: `strava_photobook/theme.py`
- Modify: `tests/test_layout_gate.py`
- Regenerate ignored output: `books/2026/`

- [ ] Add a thin responsive timeline, 44-pixel targets, horizontal mobile scrolling, and scoped flip-button rules.
- [ ] Remove obsolete folio styling and assert the new layout contract.
- [ ] Run the full Python, Node, generated-contract, layout, compile, and diff checks.
- [ ] Commit, regenerate 53 pages with 40 photos, publish Pages, push `main`, and verify desktop and mobile browsers.
