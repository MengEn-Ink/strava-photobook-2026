# Activity-linked Storytelling Implementation Plan

> For agentic workers: use the required plan execution workflow task by task.

Goal: Produce a polished yearly cycling journal whose highlights and photos remain linked to source activities and never overflow a page.

Architecture: Add deterministic editorial scoring and diversity selection in the model, render activity-aware photo pages in the book composer, enforce bounded typography in the theme, and verify HTML semantics and rendered geometry.

Tech stack: Python 3.9, unittest, HTML/CSS, StPageFlip, Node contract tests, agent-browser.

## Task 1: Editorial ranking

- Files: strava_photobook/model.py and tests/test_model.py.
- Write failing tests for multi-signal score, photo and description preference, reason labels, deterministic order, month diversity, and repeated-title limits.
- Run the model tests and verify RED.
- Add Highlight, score components, candidate ranking, and diversified selection.
- Run the tests and verify GREEN.

## Task 2: Activity-aware pages

- Files: strava_photobook/book.py and tests/test_book.py.
- Write failing tests proving every photo page contains activity ID, title, date, ride facts, reason, and optional caption.
- Verify RED.
- Add bounded-text helpers, activity photo renderer, and two-phase candidate hydration and ranking.
- Verify GREEN.

## Task 3: Editorial layout and overflow protection

- Files: strava_photobook/theme.py, tools/layout_gate.py, and tests/test_layout_gate.py.
- Write failing tests for line clamps, overflow clipping, route geometry, and caption rail bounds.
- Verify RED.
- Implement the monochrome cycling-journal layout and update the gate.
- Verify GREEN.

## Task 4: Beginner documentation

- Files: README.md, docs/setup.md, and .env.example.
- Add a documentation contract test for the complete first-run sequence and expected outputs.
- Verify RED.
- Rewrite setup documentation as a copy-pasteable beginner path with troubleshooting and privacy notes.
- Verify GREEN.

## Task 5: Real generation and browser acceptance

- Generated books/2026 remains ignored.
- Run all Python, Node, and layout tests.
- Regenerate the 2026 book.
- Serve locally and inspect every page at desktop and mobile sizes for overflow.
- Publish 2026 and verify Pages status, HTTP 200, activity markers, photos, and visible titles.
- Commit and push source changes while keeping secrets, cache, and generated books ignored.
