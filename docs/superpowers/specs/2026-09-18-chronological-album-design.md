# Chronological Album and Concise Photo Captions Design

## Goal

Keep editorial scoring for deciding which activities belong in the book, while presenting every selected activity in calendar order from January through December. Remove generic editorial labels from photo overlays so captions contain only useful activity context.

## Ordering

The existing bounded candidate hydration and editorial selection stay unchanged. After featured and gallery activities are selected, they are merged into one activity timeline and sorted by `start_date_local` ascending, with activity ID as a deterministic tie-breaker. Months without selected activities simply produce no pages; the next available date follows.

Each activity remains an indivisible block. A featured activity renders its introduction page first and then its associated photos. A non-featured activity renders its photos. Photos within one activity preserve their source order. This gives the whole activity portion of the book one January-to-December chronology without breaking photo-to-activity association.

## Caption Content

Photo overlays contain only the activity title, date, distance, elevation, and an optional original photo caption. They do not render editorial reason labels such as `照片与骑行故事完整`. Featured introduction pages may retain concise, evidence-based reasons such as PR, kudos, distance, or group participation. The generic photo-plus-story reason is replaced by the shorter `影像记录` fallback so the removed phrase cannot reappear elsewhere.

## Verification

Unit tests prove that mixed-month activities render in ascending date order, activity introduction pages remain adjacent to their photos, photo captions omit editorial reasons, and key metadata remains. Existing page-count, layout, theme, and publishing checks continue to run. The regenerated public book is verified in a fresh desktop and mobile browser session.
