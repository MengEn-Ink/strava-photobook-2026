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


def _project_routes(
    routes: list[list[tuple[float, float]]], *, size: int, pad: float
) -> list[list[tuple[float, float]]]:
    """Project several routes into one shared, north-up square canvas."""
    import math

    points = [point for route in routes for point in route]
    lat0 = sum(point[0] for point in points) / len(points)
    kx = math.cos(math.radians(lat0))
    projected = [[(lng * kx, lat) for lat, lng in route] for route in routes]
    xs = [point[0] for route in projected for point in route]
    ys = [point[1] for route in projected for point in route]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = (max_x - min_x) or 1e-9
    span_y = (max_y - min_y) or 1e-9
    span = max(span_x, span_y)
    inner = size - 2 * pad
    off_x = pad + (inner - inner * span_x / span) / 2
    off_y = pad + (inner - inner * span_y / span) / 2

    def project(x: float, y: float) -> tuple[float, float]:
        return (
            round(off_x + (x - min_x) / span * inner, 1),
            round(off_y + (max_y - y) / span * inner, 1),
        )

    return [[project(x, y) for x, y in route] for route in projected]


def route_heatmap_svg(encoded_routes: list[str], *, size: int = 100, pad: float = 5.0) -> str:
    """Render valid activity routes together; overlapping strokes accumulate heat."""
    routes: list[list[tuple[float, float]]] = []
    for encoded in encoded_routes:
        try:
            points = decode_polyline(encoded) if encoded else []
        except (IndexError, TypeError, ValueError):
            continue
        if len(points) >= 2:
            # A bounded point count keeps a full season's inline SVG compact.
            stride = max(1, (len(points) + 178) // 179)
            sampled = points[::stride]
            if sampled[-1] != points[-1]:
                sampled.append(points[-1])
            routes.append(sampled)
    if not routes:
        return ""

    # Keep the densest geographic region legible. A single trip thousands of
    # kilometres away would otherwise collapse the rider's everyday network.
    clusters: list[list[list[tuple[float, float]]]] = []
    for route in routes:
        centre = (
            sum(point[0] for point in route) / len(route),
            sum(point[1] for point in route) / len(route),
        )
        for cluster in clusters:
            anchor = cluster[0]
            anchor_centre = (
                sum(point[0] for point in anchor) / len(anchor),
                sum(point[1] for point in anchor) / len(anchor),
            )
            if abs(centre[0] - anchor_centre[0]) <= 5 and abs(centre[1] - anchor_centre[1]) <= 5:
                cluster.append(route)
                break
        else:
            clusters.append([route])
    plotted = max(clusters, key=len)
    remote_count = len(routes) - len(plotted)

    paths = []
    for points in _project_routes(plotted, size=size, pad=pad):
        d = "M" + " L".join(f"{x},{y}" for x, y in points)
        paths.append(f'<path class="heat-route base" d="{d}"/>')
        paths.append(f'<path class="heat-route hot" d="{d}"/>')
    return (
        f'<svg class="route-heatmap" viewBox="0 0 {size} {size}" fill="none" '
        f'data-plotted-routes="{len(plotted)}" data-remote-routes="{remote_count}" '
        'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" '
        'style="color:var(--theme-primary);--heat:var(--theme-accent)">'
        + "".join(paths) + "</svg>"
    )


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
