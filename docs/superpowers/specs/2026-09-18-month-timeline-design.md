# Month Timeline and External Page Status Design

## Goal

Add a compact month timeline to the flip controls and prevent page numbers from overlapping photo captions.

## Interaction

The footer keeps previous and next buttons at its edges. Its center becomes a compact navigation stack: an interactive month timeline above the existing page status. Only months represented by selected activity pages are rendered. Clicking a month turns directly to that month's first activity page. Normal flipping updates `aria-current` and the accent-colored marker for the visible activity month. Introductory and closing pages leave all month markers inactive.

Desktop labels use `2月`, `3月`, and so on. On narrow screens labels collapse to their month number and the timeline may scroll horizontally without widening the viewport. Buttons keep at least a 44-pixel touch target while the visible track remains visually thin.

## Page Numbers

Photo pages no longer render an internal folio. The footer's existing `current / total` status remains the single page-number source, outside the artwork and therefore unable to collide with photo captions.

## Data and Accessibility

Activity pages expose a numeric `data-month` alongside `data-activity-id`. The generated footer exposes one button per represented month, with `aria-label`, `aria-controls`, and `aria-current`. Runtime code derives the first page index for every month directly from the page DOM; no duplicate date table is embedded. Theme selection and PageFlip state remain independent.

## Verification

Python rendering tests cover month metadata, unique ordered timeline buttons, and absence of photo folios. Node contract tests cover month-to-page indexing and active-month resolution. Browser acceptance verifies mouse/touch navigation, current marker updates, no viewport overflow, and no caption collision on desktop and mobile.
