"""Recommendations — weak areas + due reviews + success area + tomorrow's action."""

from __future__ import annotations

from datetime import date

import pandas as pd

from .analyzer import (
    calculate_area_stats,
    calculate_fail_tag_stats,
    detect_risk_signals,
    load_recent_records,
)
from .constants import ACTION_RULES, DEFAULT_ACTION


def _select_weak_areas(area_stats: pd.DataFrame, fail_tag_combo: list, overall_avg_solve: float) -> pd.DataFrame:
    if area_stats.empty:
        return area_stats
    df = area_stats.copy()
    threshold_solve = overall_avg_solve * 1.2 if overall_avg_solve > 0 else float("inf")
    weak_mask = (
        ((df["wrong"] >= 2) & (df["accuracy"] <= 0.7))
        | (df["avg_solve_sec"] >= threshold_solve)
    )
    risky_areas = {(s, a) for s, a, _, _ in fail_tag_combo}
    if risky_areas:
        weak_mask = weak_mask | df.apply(
            lambda r: (r["subject"], r["area"]) in risky_areas, axis=1
        )
    weak = df[weak_mask].sort_values(by=["accuracy", "wrong"], ascending=[True, False])
    return weak


def _select_success_area(area_stats: pd.DataFrame) -> pd.DataFrame:
    if area_stats.empty:
        return area_stats
    success = area_stats[(area_stats["accuracy"] >= 0.75) & (area_stats["total"] >= 3)]
    return success.sort_values("accuracy", ascending=False)


def _select_due_reviews(records_df: pd.DataFrame, schedule_df: pd.DataFrame) -> pd.DataFrame:
    if schedule_df.empty:
        return pd.DataFrame()
    today_ts = pd.Timestamp(date.today())
    due = schedule_df[(schedule_df["review_date_dt"] <= today_ts) & (~schedule_df["is_done"])]
    if due.empty or records_df.empty:
        return due
    merged = due.merge(
        records_df[["id", "subject", "area", "source", "problem_no", "fail_tag", "memo", "date"]],
        left_on="record_id", right_on="id", how="left",
    )
    return merged.sort_values("review_date_dt")


def _generate_action(fail_tag_stats: pd.DataFrame) -> str:
    if fail_tag_stats.empty:
        return DEFAULT_ACTION
    top_tag = fail_tag_stats.iloc[0]["fail_tag"]
    return ACTION_RULES.get(top_tag, DEFAULT_ACTION)


def generate_recommendations(records_df: pd.DataFrame, schedule_df: pd.DataFrame) -> dict:
    recent = load_recent_records(records_df, days=30)
    area_stats = calculate_area_stats(recent)
    fail_tag_stats = calculate_fail_tag_stats(recent)
    risks = detect_risk_signals(recent)

    weak = _select_weak_areas(
        area_stats,
        risks["by_combo"],
        recent["solve_time_sec"].mean() if not recent.empty else 0,
    )
    success = _select_success_area(area_stats)
    due = _select_due_reviews(records_df, schedule_df)
    action = _generate_action(fail_tag_stats)

    weak_top = weak.head(2)
    success_top = success.head(1)

    return {
        "weak_areas": weak_top,
        "due_reviews": due,
        "success_area": success_top,
        "action": action,
        "fail_tag_stats": fail_tag_stats,
        "risk_combos": risks["by_combo"],
    }


def explain_weak_area(row: pd.Series, risk_combos: list, overall_avg_solve: float) -> list[str]:
    reasons: list[str] = []
    if row["total"] > 0:
        reasons.append(f"최근 정답률 {row['accuracy']*100:.0f}%")
    if row["wrong"] >= 2:
        reasons.append(f"오답 {int(row['wrong'])}건")
    matching_combos = [
        c for c in risk_combos
        if c[0] == row["subject"] and c[1] == row["area"]
    ]
    for s, a, tag, count in matching_combos:
        reasons.append(f"{tag} 태그 {int(count)}회 반복")
    if overall_avg_solve > 0 and row["avg_solve_sec"] >= overall_avg_solve * 1.2:
        delta = int(row["avg_solve_sec"] - overall_avg_solve)
        reasons.append(f"평균 풀이 시간이 전체 평균보다 {delta}초 김")
    return reasons
