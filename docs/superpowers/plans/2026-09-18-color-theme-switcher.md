# Color Theme Switcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the approved top-bar palette popover with the existing editorial default and all 18 specified color pairs, instant application, persistence, accessibility, and responsive behavior.

**Architecture:** Keep theme data in a small standalone browser module that owns the ordered catalog, validation, contrast calculation, CSS-variable application, and local-storage recovery. The flipbook runtime owns only popover interaction and calls the theme module; generated HTML supplies semantic controls, while `theme.css` and `styles.css` consume shared variables instead of duplicating rules per theme.

**Tech Stack:** Vanilla HTML/CSS/JavaScript, Node built-in test runner, Python string rendering, PageFlip, localStorage.

---

## File map

- Create `runtime/theme-catalog.js`: ordered theme catalog plus pure helpers and browser application API.
- Create `runtime/theme-catalog.test.mjs`: exact catalog, contrast, validation, persistence, and DOM application tests.
- Modify `strava_photobook/book.py`: render the theme trigger, palette popover, early restore script, and runtime module script.
- Modify `runtime/flipbook.js`: open/close/focus/outside-click/Escape behavior without touching page state.
- Modify `runtime/styles.css`: responsive popover, swatches, focus, and touch targets.
- Modify `strava_photobook/theme.py`: replace fixed colors with semantic theme variables across book pages.
- Modify `runtime/html-contract.test.mjs`: assert semantic theme controls and runtime assets.
- Modify `tests/test_book.py`: assert generated theme markup and fallback.
- Modify `tests/test_layout_gate.py` and `tools/layout_gate.py`: assert theme-variable coverage without weakening overflow rules.
- Modify `README.md` and `docs/setup.md`: explain switching, persistence, and reset.

### Task 1: Theme catalog and application API

- [ ] Add failing Node tests in `runtime/theme-catalog.test.mjs` that import `THEMES`, `DEFAULT_THEME_ID`, `accentInk`, `resolveThemeId`, and `applyTheme`; assert the 19 ordered IDs, exact names/colors, default ID, black/white contrast choices, invalid-ID fallback, root CSS variables, and storage writes.
- [ ] Run `node --test runtime/theme-catalog.test.mjs`; expect failure because `runtime/theme-catalog.js` does not exist.
- [ ] Create `runtime/theme-catalog.js` with the exact catalog from the approved spec. Export pure helpers and a dependency-injected `applyTheme(id, root, storage)` that catches storage failures and returns the resolved theme. Also attach the public API to `window.StravaPhotobookThemes` when `window` exists.
- [ ] Run `node --test runtime/theme-catalog.test.mjs`; expect all catalog tests to pass.
- [ ] Commit `runtime/theme-catalog.js` and its test as `feat(theme): add color theme catalog`.

### Task 2: Generated semantic selector markup

- [ ] Add failing assertions to `tests/test_book.py` for `id="theme-toggle"`, `aria-expanded="false"`, `id="theme-popover"`, 19 `data-theme-id` buttons, `aria-pressed`, the early restore script, and `theme-catalog.js` loading before `flipbook.js`.
- [ ] Run `python3 -m unittest tests.test_book -v`; expect markup assertions to fail.
- [ ] Add `_theme_picker()` and `_theme_restore_script()` helpers to `strava_photobook/book.py`. Render an ordered theme grid using a Python constant mirroring the approved public catalog for static HTML, with CSS custom properties on each swatch. Add the trigger to the header and scripts in dependency order.
- [ ] Run `python3 -m unittest tests.test_book -v`; expect all book tests to pass.
- [ ] Commit renderer and tests as `feat(theme): render accessible theme picker`.

### Task 3: Popover interaction and persistence

- [ ] Extend `runtime/html-contract.test.mjs` with failing source-contract assertions for catalog initialization, `localStorage`, `aria-expanded`, `aria-pressed`, Escape, outside click, and focus restoration.
- [ ] Run `node --test runtime/html-contract.test.mjs`; expect the new interaction contract to fail.
- [ ] Modify `runtime/flipbook.js` to initialize from the stored theme, apply the default on errors, update button states and the current label, open with focus on the selected option, close on trigger/Escape/outside click, and restore trigger focus. Theme selection must not call any PageFlip navigation method.
- [ ] Run both Node test files; expect all tests to pass.
- [ ] Commit runtime behavior as `feat(theme): add persistent palette interaction`.

### Task 4: Responsive visual system

- [ ] Add failing assertions to `tests/test_layout_gate.py` and `tools/layout_gate.py` for semantic variables (`--theme-primary`, `--theme-accent`, `--theme-accent-ink`, `--theme-paper`), selector overflow, 44px touch targets, and variable use in cover, highlighter, photo kicker, controls, route endpoint, and focus ring.
- [ ] Run `python3 -m unittest tests.test_layout_gate -v && python3 -m tools.layout_gate`; expect missing-variable failures.
- [ ] Modify `runtime/styles.css` with a compact desktop popover anchored to the header and a fixed mobile bottom sheet capped at `55dvh`, internally scrollable, with two columns and 44px minimum targets.
- [ ] Modify `strava_photobook/theme.py` so default variables preserve the current black/white/orange result and all themed elements use semantic variables. Keep photo gradients neutral and existing geometry unchanged.
- [ ] Run layout tests and gate; expect them to pass.
- [ ] Commit styling as `feat(theme): apply responsive color themes`.

### Task 5: Documentation and full automated regression

- [ ] Add failing documentation assertions to `tests/test_docs.py` for the 19-theme picker, persistence, and reset instructions.
- [ ] Run `python3 -m unittest tests.test_docs -v`; expect failure.
- [ ] Update `README.md` and `docs/setup.md`: describe the theme button, current default, instant switching, saved preference, and reset through choosing the default or clearing `strava-photobook.theme`.
- [ ] Regenerate with `python3 -m strava_photobook build 2026`.
- [ ] Run `python3 -m unittest discover -s tests -v`, `node --test runtime/*.test.mjs`, `python3 -m tools.layout_gate`, `python3 -m compileall -q strava_photobook tools`, and `git diff --check`; expect all checks to pass.
- [ ] Commit docs and integration changes as `docs: explain photobook theme switching`.

### Task 6: Browser acceptance, publish, and source push

- [ ] Serve `books/2026` locally and inspect default, `klein-neon`, `china-red-white`, and `hidden-green-spring` at `1440×1000` and `390×844`. Verify popover bounds, 44px controls, activity/photo text bounds, page preservation, and refresh persistence.
- [ ] Capture desktop and mobile screenshots for the default and at least two contrasting themes.
- [ ] Publish with `python3 -m strava_photobook publish 2026 --repo strava-photobook-2026`.
- [ ] Fetch the public Pages HTML and assets; verify HTTP 200, 19 theme buttons, `theme-catalog.js`, `strava-photobook.theme`, and activity markers.
- [ ] Confirm `.env`, `data/`, `books/`, and `.superpowers/` are ignored or unstaged; push `main` without force.
