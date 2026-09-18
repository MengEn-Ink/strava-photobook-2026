"""从 Activity 数据 + 照片源编排单年画册。

页面渲染函数都是纯字符串构造；`build_year` 负责把运行时拷贝、照片下载、
高光筛选与页面排序串起来，再写出 index.html 和 theme.css。
"""
from __future__ import annotations

import html
import shutil
from pathlib import Path

from .config import Config
from .model import Activity, by_year, select_highlights
from .route import route_svg
from .theme import FEATURE_CSS, THEME_CSS

PAGE_W, PAGE_H = 512, 640


def _esc(t: str) -> str:
    return html.escape(t or "", quote=True)


def _fmt_time(seconds: int) -> str:
    h, rem = divmod(int(seconds or 0), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# ---- page renderers -------------------------------------------------------

def _cover(year: str, subtitle: str) -> str:
    return (f'<article class="book-page art-page cloth recto" data-density="hard" '
            f'aria-label="Front cover"><h2 class="cover-title">{year}</h2>'
            f'<p class="cover-subtitle">{_esc(subtitle)}</p></article>')


def _back(year: str) -> str:
    return (f'<article class="book-page art-page cloth recto" data-density="hard" '
            f'aria-label="Back cover"><span class="back-mark">Strava Photobook · {year}</span></article>')


def _blank(label: str, cls: str = "endpaper") -> str:
    return f'<article class="book-page art-page {cls} verso" aria-label="{label}"></article>'


def _title_page(year: str, stats: dict) -> str:
    return (f'<article class="book-page art-page paper recto" aria-label="Title">'
            f'<div class="title-block"><h2>{year} 骑行纪年</h2>'
            f'<p>{stats["rides"]} 次骑行 · {stats["km"]:,.0f} km · '
            f'累计爬升 {stats["elev"]:,.0f} m</p></div></article>')


def _stats_page(stats: dict) -> str:
    lines = "".join(f"<p><b>{v}</b> {k}</p>" for k, v in stats["lines"])
    return (f'<article class="book-page art-page paper verso" aria-label="Year in numbers">'
            f'<div class="colophon"><p>年度数字</p>{lines}</div></article>')


def _photo_page(side: str, ph, folio: str) -> str:
    cap = f'<figcaption class="bleed-cap">{_esc(ph.caption)}</figcaption>' if ph.caption else ""
    mode = "contain" if ph.landscape else "full-bleed"
    return (f'<article class="book-page art-page bleed {side}" aria-label="photo">'
            f'<figure class="{mode}"><img src="{ph.web_path}" alt="{_esc(ph.caption) or "ride photo"}">{cap}</figure>'
            f'<p class="folio">{folio}</p></article>')


def _companions(avatar: str | None, athlete_count: int) -> str:
    """Companion row: the athlete's own avatar + a "+N" badge for co-riders.

    Strava doesn't expose co-riders' identities, so companions are shown as a
    count, not real faces — only the athlete's own avatar is a real photo.
    """
    if athlete_count <= 1:
        return ""
    others = athlete_count - 1
    me = (f'<img class="avatar" src="{avatar}" alt="rider">' if avatar
          else '<span class="avatar avatar-fallback">你</span>')
    badge = f'<span class="avatar avatar-more">+{others}</span>'
    return (f'<div class="companions"><div class="avatars">{me}{badge}</div>'
            f'<span class="companions-label">与 {others} 位车友同行</span></div>')


def _feature_page(side: str, a: Activity, avatar: str | None = None) -> str:
    tags = []
    if a.kudos:
        tags.append(f"♥ {a.kudos}")
    if a.pr_count:
        tags.append(f"{a.pr_count} PR")
    tags_html = f'<p class="feat-tags">{" · ".join(tags)}</p>' if tags else ""
    top = sorted([p for p in a.prs if p.get("pr_rank") == 1],
                 key=lambda p: p.get("elapsed_time") or 0)[:4]
    pr_html = ""
    if top:
        items = "".join(f"<li>{_esc(p['name'])} — {_fmt_time(p['elapsed_time'])}</li>" for p in top)
        pr_html = f'<ul class="pr-list">{items}</ul>'
    desc = f'<p class="feat-desc">{_esc(a.description)}</p>' if a.description else ""
    companions = _companions(avatar, a.athlete_count)
    route = route_svg(a.polyline, stroke="#0a0a0a", stroke_width=2.6)
    route_html = f'<div class="feat-route">{route}</div>' if route else ""
    return (f'<article class="book-page art-page paper {side}" aria-label="{_esc(a.name)[:40]}">'
            f'<div class="feature"><p class="feat-month">{a.month_label}</p>'
            f'<h3 class="feat-title">{_esc(a.name)}</h3>'
            f'<p class="feat-stats">{a.distance_km:.0f} km · 爬升 {a.elev_m:.0f} m · '
            f'均速 {a.avg_speed_kmh:.1f} km/h · {_fmt_time(a.moving_time)}</p>'
            f'{tags_html}{desc}{companions}{pr_html}</div>{route_html}</article>')


def _colophon(year: str) -> str:
    return (f'<article class="book-page art-page paper recto" aria-label="Colophon">'
            f'<div class="colophon"><p>Strava Photobook · {year}</p>'
            f'<p>由 Strava 骑行数据与照片自动编排。</p>'
            f'<p class="small-print">数据来源：Strava 官方 API。'
            f'照片为原图缩放，未改动源文件。</p></div></article>')


def _document(year: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN" data-strava-photobook="1">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Strava Photobook {year}</title>
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="theme.css">
</head>
<body>
<main class="room">
  <header class="book-header">
    <span>Strava · Cycling</span><h1>Strava Photobook {year}</h1><span id="orientation">Open spread</span>
  </header>
  <section class="stage" aria-label="Interactive photo book">
    <div class="book-rig">
      <div id="book" class="book" data-page-width="{PAGE_W}" data-page-height="{PAGE_H}">
        {body}
      </div>
    </div>
  </section>
  <footer class="controls" aria-label="Book controls">
    <button id="previous" type="button" aria-label="Previous page">←</button>
    <div class="status" aria-live="polite"><span id="page-status">Cover</span><small>拖动或方向键翻页</small></div>
    <button id="next" type="button" aria-label="Next page">→</button>
  </footer>
</main>
<script src="vendor/page-flip.browser.js"></script>
<script src="flipbook.js"></script>
</body>
</html>
"""


def _copy_runtime(cfg: Config, out: Path) -> Path:
    """Copy the shared runtime into the book dir; return the photos dir."""
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for item in cfg.runtime_dir.iterdir():
        if item.name == "index.html":
            continue
        dst = out / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)
    # append feature layout to the copied book-style.css (theme.css handles look)
    bs = out / "style" / "book-style.css"
    if bs.is_file() and "strava-photobook feature-page additions" not in bs.read_text("utf-8"):
        bs.write_text(bs.read_text("utf-8") + FEATURE_CSS, encoding="utf-8")
    (out / "theme.css").write_text(THEME_CSS, encoding="utf-8")
    photos = out / "assets" / "photos"
    photos.mkdir(parents=True, exist_ok=True)
    return photos


def _stats(acts: list[Activity]) -> dict:
    total_km = sum(a.distance_km for a in acts)
    total_elev = sum(a.elev_m for a in acts)
    total_time = sum(a.moving_time for a in acts)
    total_kudos = sum(a.kudos for a in acts)
    total_pr = sum(a.pr_count for a in acts)
    longest = max(acts, key=lambda a: a.distance_km)
    return {
        "rides": len(acts), "km": total_km, "elev": total_elev,
        "lines": [
            ("次骑行", f"{len(acts)}"),
            ("公里", f"{total_km:,.0f}"),
            ("米累计爬升", f"{total_elev:,.0f}"),
            ("小时在车上", f"{total_time/3600:,.0f}"),
            ("次收藏（kudos）", f"{total_kudos:,}"),
            ("个赛段 PR", f"{total_pr:,}"),
            (f"km 最长单骑（{_esc(longest.name)}）", f"{longest.distance_km:.0f}"),
        ],
    }


def build_year(cfg: Config, year: str, activities: list[Activity], hydrate,
               avatar_fetcher=None) -> Path:
    """Build the book for `year`. `hydrate(act, photos_dir, remaining)` fills photos+PRs.

    `avatar_fetcher(photos_dir) -> web_path | None` downloads the athlete's own
    photo (companions can't be resolved from the API, so group rides show the
    athlete + an "+N" badge).
    """
    ya = by_year(activities).get(year, [])
    if not ya:
        raise SystemExit(f"没有 {year} 的活动数据")
    out = cfg.book_dir(year)
    photos_dir = _copy_runtime(cfg, out)
    avatar = avatar_fetcher(photos_dir) if avatar_fetcher else None
    hl = select_highlights(ya)
    stats = _stats(ya)

    pages = [_cover(year, "A Year of Cycling · Strava"),
             _blank("front endpaper"),
             _title_page(year, stats),
             _stats_page(stats)]

    side = ["recto", "verso"]
    used = 0
    featured: set[str] = set()

    # feature spreads: top-kudos rides. Companions are rendered from each ride's
    # true athlete_count, which hydrate() corrects from the activity detail.
    for i, a in enumerate(hl["top_kudos"][:cfg.feature_rides]):
        featured.add(a.id)
        hydrate(a, photos_dir, 1 if a.photo_count else 0)
        pages.append(_feature_page(side[i % 2], a, avatar))
        if a.photos:
            used += 1
            pages.append(_photo_page(side[(i + 1) % 2], a.photos[0], str(i + 1)))

    # gallery: remaining photo rides by kudos
    folio = cfg.feature_rides + 1
    for a in sorted([x for x in hl["photo_acts"] if x.id not in featured],
                    key=lambda x: x.kudos, reverse=True):
        if used >= cfg.photos_per_book:
            break
        hydrate(a, photos_dir, min(2, cfg.photos_per_book - used))
        for ph in a.photos[:2]:
            if used >= cfg.photos_per_book:
                break
            pages.append(_photo_page(side[used % 2], ph, str(folio)))
            used += 1
            folio += 1

    pages += [_colophon(year), _blank("back endpaper"), _back(year)]
    (out / "index.html").write_text(_document(year, "\n        ".join(pages)), encoding="utf-8")
    print(f"built {out}  pages={len(pages)} photos={used}")
    return out
