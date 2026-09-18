# Activity-linked Storytelling Design

## Goal

Turn the yearly book from a loose photo gallery into an activity-led editorial story. Every published photo retains its activity context, and every text block remains inside the physical page at desktop and mobile sizes.

## Editorial model

The book hydrates a bounded candidate pool of rides with photos before final ranking. The score combines photo availability, human-written title and description, kudos, PR count, group participation, distance, elevation, and photo count.

Selection is not a raw top-score list. It limits repeated normalized titles and prefers month diversity, so one recurring route cannot consume the book. Every chosen activity receives a readable reason such as 年度最多点赞, 照片与骑行故事完整, 年度 PR 高光, 长距离挑战, or 多人同行.

## Page system

The visual thesis is a restrained monochrome cycling journal: documentary photography, oversized issue typography, compact ride facts, and route lines used as evidence rather than decoration.

Each highlight is a connected sequence: an activity opener with date, title, reason, metrics, short description, PR summary, companions, and route; then one or two photos from that activity. Every photo has a persistent caption rail with activity title, date, distance, elevation, reason, and optional original caption.

The remaining gallery is also activity-linked and ordered by editorial score. No anonymous image page remains.

## Overflow invariants

Render-time text budgets trim title, description, captions, and PR labels at boundaries. CSS uses fixed regions, line clamping, overflow clipping, safe minimums, and separate route/media columns.

The static gate checks column geometry and required clamping. A browser gate renders every page at desktop and phone sizes, then asserts headings, descriptions, lists, captions, and metadata remain within their page rectangle.

## Data and failure behavior

Candidate hydration is best-effort and limited. Failed detail calls reduce information score without aborting the book. Failed photo downloads remove that photo. The generated HTML includes activity IDs for traceability without exposing credentials or raw cache data.

## Documentation

The README follows a beginner journey: prerequisites, Strava app creation, installation, authorization, fetch, year discovery, build, preview, GitHub authorization, publish, verification, updates, privacy, and troubleshooting. A setup guide includes exact expected outputs and recovery steps.

## Acceptance

- No photo page lacks an activity ID and visible activity title.
- Highlight selection is deterministic, multi-signal, and diverse.
- Long synthetic content passes static and browser overflow checks.
- The real 2026 book is regenerated, published, returns HTTP 200, and visually loads on desktop and mobile.
