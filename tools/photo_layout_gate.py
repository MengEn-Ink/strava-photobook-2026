#!/usr/bin/env python3
"""Fail closed when photo or cover copy can overlap protected imagery."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path


class PhotoLayoutError(RuntimeError):
    pass


class _Layouts(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[dict[str, object]] = []
        self.stack: list[int | None] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        index = None
        if values.get("data-layout") in {"portrait-full", "landscape-split", "subject-safe"}:
            index = len(self.items)
            self.items.append({"tag": tag, "attrs": values, "caption": False})
        elif tag == "figcaption":
            for active in reversed(self.stack):
                if active is not None:
                    self.items[active]["caption"] = True
                    break
        if tag not in {"img", "br", "meta", "link", "input", "hr"}:
            self.stack.append(index)

    def handle_endtag(self, tag: str) -> None:
        if self.stack:
            self.stack.pop()


def _zone(raw: str | None, label: str) -> tuple[float, float, float, float]:
    try:
        values = tuple(float(value.strip()) for value in (raw or "").split(","))
    except ValueError as exc:
        raise PhotoLayoutError(f"{label} invalid zone") from exc
    if len(values) != 4:
        raise PhotoLayoutError(f"{label} missing zone")
    x, y, width, height = values
    if min(values) < 0 or width <= 0 or height <= 0 or x + width > 100 or y + height > 100:
        raise PhotoLayoutError(f"{label} zone outside page")
    return x, y, width, height


def _overlap(a: tuple[float, ...], b: tuple[float, ...]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def validate_photo_layouts(path: Path) -> dict[str, int]:
    parser = _Layouts()
    parser.feed(Path(path).read_text(encoding="utf-8"))
    for item in parser.items:
        attrs = item["attrs"]
        assert isinstance(attrs, dict)
        layout = str(attrs.get("data-layout"))
        if layout == "portrait-full":
            if attrs.get("data-overlay") != "forbid":
                raise PhotoLayoutError("portrait-full must forbid overlay")
            if item["caption"]:
                raise PhotoLayoutError("portrait-full caption is forbidden")
        else:
            image = _zone(attrs.get("data-image-zone"), f"{layout} image")
            copy = _zone(attrs.get("data-copy-zone"), f"{layout} copy")
            if _overlap(image, copy):
                raise PhotoLayoutError(f"{layout} image/copy overlap")
            if layout == "subject-safe" and attrs.get("data-overlay") != "forbid":
                raise PhotoLayoutError("subject-safe must forbid overlay")
    if not parser.items:
        raise PhotoLayoutError("missing photo layout contracts")
    return {"layouts": len(parser.items)}


def main() -> None:
    argument = argparse.ArgumentParser()
    argument.add_argument("html", type=Path)
    args = argument.parse_args()
    result = validate_photo_layouts(args.html)
    print(f"photo layout gate: passed layouts={result['layouts']}")


if __name__ == "__main__":
    main()
