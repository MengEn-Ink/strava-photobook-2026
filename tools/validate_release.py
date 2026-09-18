"""Fail closed when a generated photobook is incomplete or regresses."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


class ValidationError(RuntimeError):
    pass


def _inspect(book: Path) -> tuple[str, list[str]]:
    index = book / "index.html"
    if not index.is_file():
        raise ValidationError(f"missing index: {index}")
    html = index.read_text(encoding="utf-8")
    return html, re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', html)


def validate_release(book: Path, baseline: Path | None = None) -> dict[str, int]:
    book = Path(book)
    html, images = _inspect(book)
    errors: list[str] = []
    if 'data-strava-photobook="1"' not in html:
        errors.append("missing photobook marker")
    if 'id="month-timeline"' not in html:
        errors.append("missing month timeline")
    if "endpaper" in html:
        errors.append("blank endpaper present")
    if 'class="folio"' in html:
        errors.append("internal folio present")
    for source in images:
        if source.startswith(("http://", "https://", "data:")):
            continue
        if not (book / source).is_file():
            errors.append(f"missing asset: {source}")
    photos = sum(source.startswith("assets/photos/") and "athlete" not in source for source in images)
    baseline_photos = 0
    if baseline and (Path(baseline) / "index.html").is_file():
        _, old_images = _inspect(Path(baseline))
        baseline_photos = sum(
            source.startswith("assets/photos/") and "athlete" not in source
            for source in old_images
        )
        if baseline_photos and photos < min(baseline_photos, 40):
            errors.append(f"photo count regressed: {photos} < {min(baseline_photos, 40)}")
    if errors:
        raise ValidationError("; ".join(errors))
    return {"photos": photos, "baseline_photos": baseline_photos}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("book", type=Path)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    result = validate_release(args.book, args.baseline)
    print(f"release valid: photos={result['photos']} baseline={result['baseline_photos']}")


if __name__ == "__main__":
    main()
