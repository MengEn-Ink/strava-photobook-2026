"""Activity 数据模型与高光筛选。"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Photo:
    """A resolved photo: a local relative web path plus optional caption."""
    web_path: str
    caption: str = ""
    landscape: bool = False


@dataclass
class Activity:
    id: str
    name: str
    date: str                 # ISO 'YYYY-MM-DDTHH:MM:SSZ'
    year: str
    description: str = ""
    kudos: int = 0
    pr_count: int = 0
    athlete_count: int = 1
    distance_km: float = 0.0
    elev_m: float = 0.0
    avg_speed_kmh: float = 0.0
    moving_time: int = 0
    polyline: str = ""
    photo_count: int = 0
    # populated during build
    photos: list[Photo] = field(default_factory=list)
    prs: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    @property
    def month_label(self) -> str:
        if "年" in self.date and "月" in self.date:
            return self.date.split("年")[-1].split("月")[0] + "月"
        mm = re.search(r"\d{4}-(\d{2})", self.date)
        return f"{int(mm.group(1))}月" if mm else ""

    @property
    def date_label(self) -> str:
        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", self.date)
        return f"{int(match.group(2))}月{int(match.group(3))}日" if match else self.month_label


@dataclass(frozen=True)
class Highlight:
    activity: Activity
    score: float
    reason: str


def clean_description(text: str) -> str:
    """Drop auto-generated weather/telemetry lines, keep the human lead."""
    if not text:
        return ""
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if "KlimatApp" in line or ("湿度" in line and "风" in line):
            continue
        if re.match(r"^[\U0001F300-\U0001FAFF\u2600-\u27BF]", line) and any(
            k in line for k in ("训练", "强度", "脂肪", "碳水", "保持", "负荷", "匹配")
        ):
            continue
        out.append(line)
    return "  ".join(out[:2]).strip()


def year_of(date: str) -> str:
    if "年" in date:
        return date.split("年")[0]
    m = re.match(r"(\d{4})", date)
    return m.group(1) if m else "?"


def by_year(acts: list[Activity]) -> dict[str, list[Activity]]:
    out: dict[str, list[Activity]] = {}
    for a in acts:
        out.setdefault(a.year, []).append(a)
    return out


def select_highlights(year_acts: list[Activity], limit: int = 12) -> dict:
    """Pick standout rides: most kudos, PR rides, group rides; plus photo rides."""
    return {
        "top_kudos": sorted(year_acts, key=lambda a: a.kudos, reverse=True)[:limit],
        "pr_rides": sorted(
            [a for a in year_acts if a.pr_count > 0],
            key=lambda a: (a.pr_count, a.kudos), reverse=True,
        )[:limit],
        "social": sorted(
            [a for a in year_acts if a.athlete_count > 1],
            key=lambda a: (a.athlete_count, a.kudos), reverse=True,
        )[:limit],
        "photo_acts": [a for a in year_acts if a.photo_count > 0],
    }


def _title_key(name: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", (name or "").lower()).replace("ride", "")


def _editorial_score(a: Activity) -> float:
    score = min(a.kudos, 100) * 1.0
    score += min(a.pr_count, 15) * 3.0
    score += min(max(a.athlete_count - 1, 0), 10) * 2.0
    score += min(a.distance_km, 200) * 0.10
    score += min(a.elev_m, 3000) * 0.008
    if a.photo_count:
        score += 18 + min(a.photo_count, 8) * 1.5
    if clean_description(a.description):
        score += 16
    if a.name and not re.fullmatch(r"(?:morning|evening|lunch|afternoon)?\s*ride", a.name, re.I):
        score += 5
    return score


def _highlight_reason(a: Activity) -> str:
    if a.photo_count and clean_description(a.description):
        return "照片与骑行故事完整"
    if a.pr_count >= 5:
        return "年度 PR 高光"
    if a.kudos >= 50:
        return "年度最多点赞"
    if a.distance_km >= 150 or a.elev_m >= 1800:
        return "长距离挑战"
    if a.athlete_count > 1:
        return "多人同行"
    if a.photo_count:
        return "影像记录"
    return "年度代表骑行"


def select_editorial_highlights(year_acts: list[Activity], limit: int = 6) -> list[Highlight]:
    """Select deterministic, photo-led highlights with month and title diversity."""
    ranked = sorted(year_acts, key=lambda a: (-_editorial_score(a), a.date, a.id))
    selected: list[Highlight] = []
    seen_months: set[str] = set()
    seen_titles: set[str] = set()
    for diversity_pass in (True, False):
        for activity in ranked:
            if any(item.activity.id == activity.id for item in selected):
                continue
            title = _title_key(activity.name)
            if title and title in seen_titles:
                continue
            if diversity_pass and activity.month_label in seen_months:
                continue
            selected.append(Highlight(activity, _editorial_score(activity), _highlight_reason(activity)))
            seen_months.add(activity.month_label)
            if title:
                seen_titles.add(title)
            if len(selected) >= limit:
                return selected
    return selected
