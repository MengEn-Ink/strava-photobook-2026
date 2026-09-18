#!/usr/bin/env python3
"""把 Strava 编码折线转成简洁的 SVG 路线图形。

Strava 的 `map.summary_polyline` 使用 Google 编码折线算法。这里解码成经纬度，
用局部等距投影（对单条骑行的包围盒足够），归一化到 viewBox，输出内联 SVG <path>。
不用位图、不依赖外部服务——轨迹就是一个矢量图形。
"""
from __future__ import annotations


def decode_polyline(encoded: str) -> list[tuple[float, float]]:
    """Decode a Google-encoded polyline to a list of (lat, lng)."""
    points: list[tuple[float, float]] = []
    index = lat = lng = 0
    length = len(encoded)
    while index < length:
        for is_lng in (False, True):
            shift = result = 0
            while True:
                b = ord(encoded[index]) - 63
                index += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            delta = ~(result >> 1) if (result & 1) else (result >> 1)
            if is_lng:
                lng += delta
            else:
                lat += delta
        points.append((lat / 1e5, lng / 1e5))
    return points


def route_svg(
    encoded: str,
    *,
    size: int = 100,
    stroke: str = "currentColor",
    stroke_width: float = 2.4,
    pad: float = 6.0,
    show_start: bool = True,
) -> str:
    """Return an inline SVG string tracing the ride, or "" if undecodable.

    The path is projected with a cos(lat) longitude correction, flipped on Y so
    north is up, scaled to fit a square viewBox while preserving aspect ratio.
    """
    if not encoded:
        return ""
    pts = decode_polyline(encoded)
    if len(pts) < 2:
        return ""

    import math

    lat0 = sum(p[0] for p in pts) / len(pts)
    kx = math.cos(math.radians(lat0))
    xs = [p[1] * kx for p in pts]
    ys = [p[0] for p in pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = (max_x - min_x) or 1e-9
    span_y = (max_y - min_y) or 1e-9
    span = max(span_x, span_y)
    inner = size - 2 * pad
    # centre the smaller dimension
    off_x = pad + (inner - inner * span_x / span) / 2
    off_y = pad + (inner - inner * span_y / span) / 2

    def project(x: float, y: float) -> tuple[float, float]:
        px = off_x + (x - min_x) / span * inner
        # flip Y so north points up
        py = off_y + (max_y - y) / span * inner
        return round(px, 1), round(py, 1)

    coords = [project(x, y) for x, y in zip(xs, ys)]
    d = "M" + " L".join(f"{px},{py}" for px, py in coords)
    start = ""
    if show_start:
        sx, sy = coords[0]
        start = f'<circle cx="{sx}" cy="{sy}" r="{stroke_width * 1.4:.1f}" fill="{stroke}"/>'
    return (
        f'<svg class="route" viewBox="0 0 {size} {size}" '
        f'fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        f'<path d="{d}" stroke="{stroke}" stroke-width="{stroke_width}" '
        f'stroke-linejoin="round" stroke-linecap="round"/>{start}</svg>'
    )


if __name__ == "__main__":
    # tiny self-test with a hand-made polyline (no external files needed)
    demo = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
    svg = route_svg(demo)
    print("points:", len(decode_polyline(demo)), "| svg bytes:", len(svg))
    print(svg[:160], "...")
