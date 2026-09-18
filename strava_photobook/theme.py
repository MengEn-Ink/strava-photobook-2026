"""画册样式：介绍页布局补充 + Pas Normal Studios 风格主题。

`FEATURE_CSS` 追加到运行时的 book-style.css（介绍页布局、满屏/留边照片、轨迹图形）。
`THEME_CSS` 写成独立的 theme.css 并最后加载，因此换风格无需改动共享运行时。
"""
from __future__ import annotations

# Layout additions the runtime doesn't ship (feature pages, bleed photos, route).
FEATURE_CSS = """
/* strava-photobook feature-page additions */
/* text flows in a left column; the route glyph owns the bottom-right corner,
   so the two never share an x-band and cannot overlap regardless of length. */
.art-page .feature{position:absolute;left:10%;right:34%;top:11%;bottom:9%;overflow:hidden;display:flex;flex-direction:column}
.art-page .feat-month{margin:0 0 3cqw}
.art-page .feat-title{margin:0 0 3.5cqw}
.art-page .feat-stats{margin:0 0 2cqw}
.art-page .feat-tags{margin:0 0 4cqw}
.art-page .feat-desc{margin:0 0 4cqw}
.art-page .feat-title,.art-page .feat-desc,.art-page .photo-note{display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden}
.art-page .feat-title{-webkit-line-clamp:3}
.art-page .feat-desc{-webkit-line-clamp:5}
.art-page .pr-list{list-style:none;padding:0;margin:0;padding-top:3cqw}
.art-page .pr-list li{display:flex;justify-content:space-between;gap:2cqw}
.art-page .pr-list li::before{align-self:center}
/* full-bleed photo pages: image fills the whole leaf */
.art-page.bleed{background:#111}
.art-page .full-bleed{position:absolute;inset:0;margin:0;overflow:hidden}
.art-page .full-bleed img{width:100%;height:100%;object-fit:cover;object-position:center}
/* landscape photos: one shared 3:2-ish band so facing leaves align exactly */
.art-page .contain{position:absolute;inset:0;margin:0;overflow:hidden}
.art-page .contain img{position:absolute;left:0;top:20%;width:100%;height:60%;object-fit:cover;object-position:center}
.art-page .full-bleed .bleed-cap,.art-page .contain .bleed-cap{position:absolute;left:0;right:0;bottom:0;max-height:36%;box-sizing:border-box;overflow:hidden;margin:0;padding:13cqw 7% 5%;color:#fff;background:linear-gradient(to top,rgb(0 0 0 / 82%),rgb(0 0 0 / 42%) 62%,transparent);display:flex;flex-direction:column;gap:1.2cqw}
.art-page .bleed-cap strong{font:700 4.2cqw/1.05 var(--book-sans);letter-spacing:-.01em;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.art-page .bleed-cap>span{font:600 1.9cqw/1.35 var(--book-sans);letter-spacing:.08em;text-transform:uppercase}
.art-page .bleed-cap .photo-note{-webkit-line-clamp:2;text-transform:none;letter-spacing:.02em;font-weight:500}
.art-page .feat-route{position:absolute;right:8%;bottom:11%;width:25%;opacity:1}
.art-page .feat-route .route{width:100%;height:auto;display:block}
/* companions row: athlete avatar + "+N" badge */
.art-page .companions{display:flex;align-items:center;gap:2.5cqw;margin:0 0 4cqw}
.art-page .companions .avatars{display:flex}
.art-page .companions .avatar{width:7cqw;height:7cqw;border-radius:50%;object-fit:cover;display:flex;align-items:center;justify-content:center;flex:none}
.art-page .companions .avatar + .avatar{margin-left:-2.2cqw}
/* --- portrait / single-page (phones) --- */
/* The leaf shows alone, so give text more width for readability while keeping
   the same non-overlap invariant: text's right edge (70%) stays left of the
   route column's left edge (71%). Slightly larger type for small screens. */
.book[data-layout="portrait"] .art-page .feature{left:9%;right:30%;top:9%;bottom:8%}
.book[data-layout="portrait"] .art-page .feat-route{right:5%;bottom:8%;width:24%}
"""

# Pas Normal Studios-inspired: black & white, geometric sans, uppercase + wide
# tracking, big type, generous whitespace.
THEME_CSS = """
/* ===== Strava Photobook · Pas Normal Studios-inspired theme ===== */
:root{
  --theme-primary:#0A0A0A;--theme-accent:#FF5A36;--theme-accent-ink:#FFFFFF;
  --theme-paper:color-mix(in srgb,var(--theme-primary) 3%,white);
  --paper:var(--theme-paper); --ink:#0a0a0a; --cloth:var(--theme-primary);
  --book-serif:"Helvetica Neue",Inter,"PingFang SC","Hiragino Sans GB",Arial,sans-serif;
  --book-sans:"Helvetica Neue",Inter,Arial,sans-serif;
}
html,body,.room{background:color-mix(in srgb,var(--theme-primary) 2%,white);color:var(--ink)}
.art-page{background:var(--theme-paper) !important}
.art-page.endpaper{background:color-mix(in srgb,var(--theme-primary) 7%,white) !important}
.art-page.cloth{background:var(--theme-primary) !important;color:#fff}
.book{filter:drop-shadow(0 10px 24px rgb(0 0 0 / 18%))}
.book-header h1{font:600 18px/1.2 var(--book-sans);letter-spacing:.14em;text-transform:uppercase}
.book-header a,.book-header span{font:500 10px/1.4 var(--book-sans);letter-spacing:.18em;text-transform:uppercase;color:#111}
.controls>button{border:1px solid var(--theme-primary);border-radius:0;background:#fff;color:var(--theme-primary)}
.controls>button:hover:not(:disabled){background:var(--theme-primary);color:#fff}
.status span{font:600 10px/1.4 var(--book-sans);letter-spacing:.22em;text-transform:uppercase;color:#111}
.status small{font:500 9px/1.4 var(--book-sans);letter-spacing:.12em;text-transform:uppercase;color:#8a8a8a}
.art-page .cover-title{font:700 20cqw/.9 var(--book-sans);letter-spacing:-.02em;text-shadow:none;color:#fff}
.art-page .cover-subtitle{font:600 2.4cqw/1.4 var(--book-sans);letter-spacing:.28em;text-transform:uppercase;color:#e8e8e8}
.art-page .back-mark{font:600 2.6cqw/1.4 var(--book-sans);letter-spacing:.24em;text-transform:uppercase;color:#fff}
.art-page .title-block{top:22%}
.art-page .title-block h2{font:700 8.5cqw/1.02 var(--book-sans);letter-spacing:-.02em;text-transform:uppercase;margin:0 0 5cqw}
.art-page .title-block p{font:500 2.6cqw/1.5 var(--book-sans);letter-spacing:.04em}
.art-page .colophon{font:500 2.6cqw/1.55 var(--book-sans)}
.art-page .colophon p{margin:0 0 4cqw}
.art-page .colophon p b{font-weight:700;font-size:1.5em}
.art-page .year-stats{top:15%;max-height:76%;overflow:hidden}
.art-page .year-stats p{margin:0 0 2.6cqw}
.art-page .year-stats p:first-child{margin-bottom:4cqw}
.art-page .colophon .small-print{font:500 1.8cqw/1.6 var(--book-sans);color:#8a8a8a}
.art-page .feat-month{font:600 2.2cqw/1 var(--book-sans);letter-spacing:.28em;color:#111;text-transform:uppercase}
.art-page .feat-reason{align-self:flex-start;margin:0 0 3cqw;padding:.8cqw 1.4cqw;background:var(--theme-accent);color:var(--theme-accent-ink);font:700 1.6cqw/1 var(--book-sans);letter-spacing:.12em;text-transform:uppercase}
.art-page .feat-title{font:700 7.2cqw/1.0 var(--book-sans);letter-spacing:-.02em;text-transform:uppercase}
.art-page .feat-stats{font:500 2.5cqw/1.5 var(--book-sans);letter-spacing:.02em;color:#111}
.art-page .feat-tags{font:600 2.6cqw/1.4 var(--book-sans);letter-spacing:.06em;color:#111;text-transform:uppercase}
.art-page .feat-desc{font:500 2.6cqw/1.48 var(--book-sans);color:#111}
.art-page .companions .avatar{border:.4cqw solid #fff;box-shadow:0 0 0 .4cqw #111}
.art-page .companions .avatar-fallback,.art-page .companions .avatar-more{background:var(--theme-primary);color:#fff;font:600 2.4cqw/1 var(--book-sans);letter-spacing:.02em}
.art-page .companions-label{font:600 2.4cqw/1.3 var(--book-sans);letter-spacing:.06em;color:#111;text-transform:uppercase}
.art-page .pr-list{border-top:1px solid #111}
.art-page .pr-list li{font:500 2.3cqw/1.7 var(--book-sans);color:#111}
.art-page .pr-list li::before{content:"PR";font:600 1.6cqw var(--book-sans);letter-spacing:.1em;color:#8a8a8a}
.art-page .feat-route .route path{stroke:#c2c2c2}
.art-page .feat-route .route circle{fill:var(--theme-accent)}
.art-page .bleed-cap{font:600 2.2cqw/1.35 var(--book-sans);letter-spacing:.14em;text-transform:uppercase}
.art-page.annual-heatmap{overflow:hidden;background:color-mix(in srgb,var(--theme-primary) 5%,white) !important}
.art-page .heatmap-heading{position:absolute;left:9%;right:9%;top:8%;z-index:2}
.art-page .heatmap-heading span{font:700 1.7cqw/1 var(--book-sans);letter-spacing:.28em;color:var(--theme-accent)}
.art-page .heatmap-heading h2{margin:1.4cqw 0 0;font:700 6.4cqw/.95 var(--book-sans);letter-spacing:-.03em;color:var(--theme-primary)}
.art-page .heatmap-canvas{position:absolute;left:7%;right:7%;top:23%;bottom:20%;overflow:hidden}
.art-page .route-heatmap{display:block;width:100%;height:100%;filter:drop-shadow(0 0 1.8cqw color-mix(in srgb,var(--theme-accent) 42%,transparent))}
.art-page .heat-route{fill:none;stroke-linecap:round;stroke-linejoin:round}
.art-page .heat-route.base{stroke:var(--theme-primary);stroke-width:1.8;opacity:.13}
.art-page .heat-route.hot{stroke:var(--theme-accent);stroke-width:.62;opacity:.4;mix-blend-mode:multiply}
.art-page .heatmap-note{position:absolute;left:9%;bottom:17%;margin:0;font:500 1.35cqw/1 var(--book-sans);letter-spacing:.12em;color:color-mix(in srgb,var(--theme-primary) 55%,white);text-transform:uppercase}
.art-page .heatmap-summary{position:absolute;left:9%;right:9%;bottom:7%;display:grid;grid-template-columns:repeat(3,1fr);gap:2cqw;border-top:1px solid color-mix(in srgb,var(--theme-primary) 28%,transparent);padding-top:3cqw;overflow:hidden}
.art-page .heatmap-summary span{font:600 1.65cqw/1.3 var(--book-sans);letter-spacing:.06em;color:var(--theme-primary);white-space:nowrap}
.art-page .heatmap-summary b{display:block;margin-bottom:.7cqw;font:700 3.2cqw/1 var(--book-sans);letter-spacing:-.02em}
"""
