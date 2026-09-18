# Compact Page Flow and Aligned Landscape Photos Design

## Goal

Remove pages with no reader value and make adjacent landscape photos share one consistent visual grid.

## Page Flow

Remove the front and back blank endpapers. Keep the cover, title, annual statistics, activity pages, colophon, and back cover because each has content or a clear book function. With `showCover` enabled, the resulting odd page count keeps the front and back covers as single leaves while all interior content forms complete spreads.

## Landscape Photo Layout

Landscape photos use a fixed 60% image band positioned from 20% to 80% of the leaf. The image fills that band with centered `object-fit: cover`; the caption remains anchored to the bottom edge with the existing gradient. Consequently, two landscape photographs in one spread have identical top edge, bottom edge, and caption baseline even when their source aspect ratios differ. Portrait photos retain the full-bleed treatment.

## Verification

Rendering tests reject blank endpapers. Layout tests require fixed geometry for `.contain img`. Generated-book checks verify there are no empty articles, landscape photos share equal bounding boxes in a desktop spread, and mobile content remains within the viewport.
