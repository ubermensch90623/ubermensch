"""Analytics — overall/subject/area/fail-tag stats + risk signal detection."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd


def load_recent_records(records_df: pd.DataFrame, days: int | None = None) -> pd.DataFrame:
    if records_df.empty or days is None:
        return records_df
    cutoff = pd.Timestamp(date.today() - timedelta(days=days - 1))
    return records_df[records_df["date_dt"] >= cutoff].copy()


def calculate_overall_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total": 0, "correct": 0, "wrong": 0,
            "accuracy": 0.0, "avg_solve_sec": 0.0,
        }
    total = len(df)
    correct = int(df["is_correct"].sum())
    return {
        "total": total,
        "correct": correct,
        "wrong": total - correct,
        "accuracy": correct / total if total else 0.0,
        "avg_solve_sec": float(df["solve_time_sec"].mean()),
    }


def _group_stats(df: pd.DataFrame, key: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[key, "total", "correct", "wrong", "accuracy", "avg_solve_sec"])
    grouped = df.groupby(key, dropna=False).agg(
        total=("id", "count"),
        correct=("is_correct", "sum"),
        avg_solve_sec=("solve_time_sec", "mean"),
    ).reset_index()
    grouped["correct"] = grouped["correct"].astype(int)
    grouped["wrong"] = grouped["total"] - grouped["correct"]
    grouped["accuracy"] = grouped["correct"] / grouped["total"]
    return grouped[[key, "total", "correct", "wrong", "accuracy", "avg_solve_sec"]].sort_values(
        by=["accuracy", "total"], ascending=[True, False]
    )


def calculate_subject_stats(df: pd.DataFrame) -> pd.DataFrame:
    return _group_stats(df, "subject")


def calculate_area_stats(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["subject", "area", "total", "correct", "wrong", "accuracy", "avg_solve_sec"])
    grouped = df.groupby(["subject", "area"], dropna=False).agg(
        total=("id", "count"),
        correct=("is_correct", "sum"),
        avg_solve_sec=("solve_time_sec", "mean"),
    ).reset_index()
    grouped["correct"] = grouped["correct"].astype(int)
    grouped["wrong"] = grouped["total"] - grouped["correct"]
    grouped["accuracy"] = grouped["correct"] / grouped["total"]
    return grouped[["subject", "area", "total", "correct", "wrong", "accuracy", "avg_solve_sec"]].sort_values(
        by=["accuracy", "total"], ascending=[True, False]
    )


def calculate_fail_tag_stats(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["fail_tag", "count", "ratio"])
    wrong = df[(~df["is_correct"]) & (df["fail_tag"].astype(str).str.len() > 0)]
    if wrong.empty:
        return pd.DataFrame(columns=["fail_tag", "count", "ratio"])
    counts = wrong.groupby("fail_tag").size().reset_index(name="count")
    total_wrong = len(wrong)
    counts["ratio"] = counts["count"] / total_wrong
    return counts.sort_values("count", ascending=False).reset_index(drop=True)


def detect_risk_signals(df: pd.DataFrame, threshold: int = 3) -> dict:
    """Return tag-level and (subject, area, tag)-level risk signals."""
    out = {"by_tag": [], "by_combo": []}
    if df.empty:
        return out
    wrong = df[(~df["is_correct"]) & (df["fail_tag"].astype(str).str.len() > 0)]
    if wrong.empty:
        return out
    # by tag
    tag_counts = wrong.groupby("fail_tag").size().reset_index(name="count")
    risky_tags = tag_counts[tag_counts["count"] >= threshold].sort_values("count", ascending=False)
    out["by_tag"] = list(risky_tags.itertuples(index=False, name=None))

    # by subject+area+tag combo
    combo = wrong.groupby(["subject", "area", "fail_tag"]).size().reset_index(name="count")
    risky_combo = combo[combo["count"] >= threshold].sort_values("count", ascending=False)
    out["by_combo"] = list(risky_combo.itertuples(index=False, name=None))
    return out
