# Compact Page Flow and Aligned Landscape Photos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate empty endpapers and align landscape-photo geometry across spreads.

**Architecture:** Simplify the page sequence at generation time and enforce one CSS geometry contract for all landscape images. No runtime branching is needed.

**Tech Stack:** Python rendering, CSS, `unittest`, Node contract tests, browser acceptance.

---

### Task 1: Lock page-flow behavior

**Files:**
- Modify: `tests/test_book.py`
- Modify: `strava_photobook/book.py`

- [ ] Add a failing build assertion that generated content has no endpaper articles.
- [ ] Remove front and back endpapers from `build_year`.
- [ ] Confirm the final generated book has 51 meaningful pages and retains both covers.

### Task 2: Lock landscape alignment

**Files:**
- Modify: `tests/test_layout_gate.py`
- Modify: `strava_photobook/theme.py`

- [ ] Add failing assertions for a fixed 20% top offset, 60% image height, full width, and centered cover crop.
- [ ] Replace intrinsic contain sizing with the fixed landscape image band.
- [ ] Run focused tests until green.

### Task 3: Regress and publish

**Files:**
- Regenerate ignored output: `books/2026/`

- [ ] Run all Python, Node, layout, generated-contract, compile, and diff checks.
- [ ] Verify browser geometry for paired landscape images and confirm no blank pages or viewport overflow.
- [ ] Commit, publish GitHub Pages, push `main`, and repeat public desktop/mobile checks.
