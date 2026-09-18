# Photo Layout and Click Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore full-screen portrait photos, give landscape photos a separate information area, add deterministic left/right click navigation, and fail publication when photo or cover copy can overlap protected imagery.

**Architecture:** `book.py` emits explicit portrait, landscape, and cover safety contracts. `photo_layout_gate.py` validates the declared percentage zones and forbidden overlays. The runtime disables library click flipping and owns one tested left/right click dispatcher while preserving drag, keyboard, and timeline controls.

**Tech Stack:** Python HTML rendering and unittest, CSS, vanilla JavaScript with Node tests, agent-browser visual verification.

---

### Task 1: Portrait and landscape render contracts

- [ ] Change `tests/test_book.py` to require portrait-full/no-caption and landscape-split/complete-caption markup.
- [ ] Run the focused test and observe failure against the shared 72/28 frame.
- [ ] Update `_activity_photo_page()` to emit the two layouts with explicit safety-zone attributes.
- [ ] Pass the focused test.

### Task 2: Orientation-specific CSS

- [ ] Change `tests/test_layout_gate.py` to require full-page portrait cover and non-overlapping landscape image/copy bands.
- [ ] Replace the shared frame CSS with portrait-full and landscape-split rules.
- [ ] Run focused CSS tests and rebuild the 2026 book.

### Task 3: Cover zero-occlusion structure

- [ ] Add a failing cover render test requiring subject-safe metadata and separated image/copy zones.
- [ ] Move every cover text element into the lower poster panel and remove the photo gradient overlay.
- [ ] Pass the focused cover test.

### Task 4: Fail-closed visual gate

- [ ] Create `tests/test_photo_layout_gate.py` with valid, overlapping, missing-attribute, and portrait-caption fixtures.
- [ ] Create `tools/photo_layout_gate.py` to parse contracts and reject invalid or intersecting zones.
- [ ] Add the gate to the nightly workflow before publish.
- [ ] Pass focused gate and workflow tests.

### Task 5: Explicit left/right click navigation

- [ ] Add runtime Node tests for click direction, interactive-target exclusion, and drag-click suppression.
- [ ] Extract a pure click-direction helper and wire it to the book container with PageFlip click flipping disabled.
- [ ] Pass runtime tests and retain keyboard, drag, swipe, and timeline behavior.

### Task 6: Verify and publish

- [ ] Update beginner docs with portrait, landscape, cover safety, and click behavior.
- [ ] Run all Python and Node tests, layout gates, photo layout gate, and release validator.
- [ ] Inspect cover, portrait, landscape spread, and click navigation at desktop and mobile viewports.
- [ ] Commit, push, publish `gh-pages`, and verify public invariants.
