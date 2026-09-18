"""Presentation-neutral cover selection and annual review calculations."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .model import Activity, Photo


@dataclass(frozen=True)
class CoverSelection:
    photo: Photo
    activity: Activity
    object_position: str = "center"


@dataclass(frozen=True)
class MonthReview:
    month: int
    distance_km: float


@dataclass(frozen=True)
class YearReview:
    rides: int
    distance_km: float
    elevation_m: float
    moving_hours: int
    kudos: int
    pr_count: int
    months: tuple[MonthReview, ...]
    peak_month: MonthReview
    longest_ride: Activity

    @property
    def active_months(self) -> int:
        return len(self.months)


def _cover_score(activity: Activity, photo: Photo) -> float:
    score = 32 if photo.landscape else 0
    score += min(activity.kudos, 100)
    score += min(activity.pr_count, 15) * 4
    score += min(activity.distance_km, 200) * .16
    score += min(activity.elev_m, 3000) * .01
    if activity.name and not re.fullmatch(r"(?:morning|evening|lunch|afternoon)?\s*ride", activity.name, re.I):
        score += 12
    return score


def select_cover(activities: list[Activity]) -> CoverSelection | None:
    candidates = [
        (_cover_score(activity, photo), activity.date, activity.id, activity, photo)
        for activity in activities for photo in activity.photos
    ]
    if not candidates:
        return None
    _, _, _, activity, photo = max(candidates, key=lambda item: item[:3])
    return CoverSelection(photo=photo, activity=activity)


def build_year_review(activities: list[Activity]) -> YearReview:
    if not activities:
        raise ValueError("annual review needs at least one activity")
    monthly: dict[int, float] = {}
    for activity in activities:
        match = re.search(r"\d{4}-(\d{2})", activity.date)
        if match:
            month = int(match.group(1))
            monthly[month] = monthly.get(month, 0) + activity.distance_km
    months = tuple(MonthReview(month, round(distance, 1)) for month, distance in sorted(monthly.items()))
    return YearReview(
        rides=len(activities),
        distance_km=sum(activity.distance_km for activity in activities),
        elevation_m=sum(activity.elev_m for activity in activities),
        moving_hours=round(sum(activity.moving_time for activity in activities) / 3600),
        kudos=sum(activity.kudos for activity in activities),
        pr_count=sum(activity.pr_count for activity in activities),
        months=months,
        peak_month=max(months, key=lambda item: (item.distance_km, -item.month)),
        longest_ride=max(activities, key=lambda activity: (activity.distance_km, activity.date, activity.id)),
    )
