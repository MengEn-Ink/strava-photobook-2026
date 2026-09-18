#!/usr/bin/env python3
"""布局门禁：静态核对高光页排版不会堆积/遮挡，无需浏览器。

高光页把文字放在左栏、轨迹图放在右下角。只要「文字栏右边界」不越过「轨迹栏
左边界」，两者就不可能在任何内容长度下重叠。本门禁直接解析 theme.py 的 CSS
断言这条几何不变量，并核对轨迹颜色足够浅、关键文字类都有样式。

用法：
  python -m tools.layout_gate         # 校验 CSS 不变量
  python tools/layout_gate.py

配套的动态核对（真实浏览器逐页测元素矩形碰撞）见 README 的「布局门禁」一节。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "strava_photobook" / "theme.py"


def _pct(css: str, selector: str, prop: str) -> float | None:
    """Read a percentage value of `prop` from the rule block of `selector`."""
    m = re.search(re.escape(selector) + r"\{([^}]*)\}", css)
    if not m:
        return None
    pm = re.search(prop + r"\s*:\s*([\d.]+)%", m.group(1))
    return float(pm.group(1)) if pm else None


def _luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def _no_overlap(css: str, feature_sel: str, route_sel: str, label: str) -> str | None:
    """确认某布局下「文字栏右边界」不越过「轨迹栏左边界」。返回错误或 None。"""
    feat_right = _pct(css, feature_sel, "right")
    route_right = _pct(css, route_sel, "right")
    route_width = _pct(css, route_sel, "width")
    if None in (feat_right, route_right, route_width):
        return f"{label}：无法解析 {feature_sel} / {route_sel} 的百分比布局"
    text_right_edge = 100 - feat_right
    route_left_edge = 100 - route_right - route_width
    gap = route_left_edge - text_right_edge
    if gap < 1:
        return (f"{label}：文字栏(右边界 {text_right_edge:.0f}%) 与轨迹栏"
                f"(左边界 {route_left_edge:.0f}%) 重叠/相接，gap={gap:.0f}%")
    return None


def check(css: str) -> list[str]:
    errors: list[str] = []

    # 1) text column vs route column must not cross — in both layouts.
    e = _no_overlap(css, ".art-page .feature", ".art-page .feat-route", "横屏/双页")
    if e:
        errors.append(e)
    # portrait (phone single-page) overrides
    e = _no_overlap(css,
                    '.book[data-layout="portrait"] .art-page .feature',
                    '.book[data-layout="portrait"] .art-page .feat-route',
                    "竖屏/手机")
    if e:
        errors.append(e)

    # 2) route glyph must be light (not near-black), per the requirement.
    sm = re.search(r"\.feat-route \.route path\{stroke:(#[0-9a-fA-F]{3,6})\}", css)
    if not sm:
        errors.append("找不到 .feat-route .route path 的 stroke 颜色")
    elif _luminance(sm.group(1)) < 0.55:
        errors.append(f"轨迹颜色过深：{sm.group(1)}（要求更浅，亮度≥0.55）")

    # 3) key text classes must be styled (typography present).
    for sel in (".feat-title", ".feat-stats", ".feat-desc", ".companions-label", ".pr-list"):
        if f"{sel}{{" not in css.replace(" ", "") and f".art-page {sel}" not in css:
            errors.append(f"缺少 {sel} 的排版样式")

    compact = css.replace(" ", "")
    for required in ("overflow:hidden", "-webkit-line-clamp:3", "-webkit-line-clamp:5",
                     ".portrait-fullimg{", "height:100%", ".landscape-splitimg{",
                     "height:66%", "height:34%",
                     ".year-stats{", "max-height:76%"):
        if required not in compact:
            errors.append(f"缺少防溢出规则：{required}")

    for variable in ("--theme-primary", "--theme-accent", "--theme-accent-ink", "--theme-paper"):
        if variable not in css:
            errors.append(f"缺少主题变量：{variable}")

    return errors


def main() -> int:
    css = THEME.read_text(encoding="utf-8")
    errors = check(css)
    if errors:
        print("布局门禁：未通过")
        for e in errors:
            print("  ✗", e)
        return 1
    print("布局门禁：通过（文字与轨迹分栏不重叠、轨迹色够浅、排版齐全）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
