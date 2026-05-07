"""Daily review report — today's stats + core bug + tomorrow's action."""

from __future__ import annotations

from datetime import date

import pandas as pd

from .analyzer import calculate_fail_tag_stats
from .constants import ACTION_RULES, DEFAULT_ACTION
from .utils import format_pct, format_secs


CORE_BUG_BY_TAG = {
    "조건 누락": "조건을 읽고도 풀이 중에 유지하지 못했다.",
    "계산 지연": "어림산/비율 비교 없이 정밀 계산으로 들어갔다.",
    "공식 혼동": "유사 공식 둘을 풀이 직전 분리하지 못했다.",
    "시간 초과": "방향이 안 보이는데도 같은 문제에 머물렀다.",
    "선지 판단 오류": "선지를 보기 전에 구해야 할 값을 정의하지 않았다.",
    "계산 실수": "마지막 계산 단계의 검산을 생략했다.",
    "개념 미흡": "개념 자체가 정리되지 않아 응용에서 무너졌다.",
    "그래프 해석 오류": "축 단위/방향 확인 단계를 건너뛰었다.",
    "표 해석 오류": "표 단위 변환 단계를 건너뛰었다.",
    "문제 접근 실패": "문제를 시작하는 1번째 단계가 정해져 있지 않았다.",
    "너무 오래 붙잡음": "이동 신호를 무시하고 매몰되었다.",
    "찍기 실패": "포기 시점에서 찍기 기준이 없었다.",
    "멘탈 흔들림": "워밍업 없이 어려운 문제로 시작했다.",
    "쉬운 문제 과소평가": "쉬워 보여서 조건 확인을 생략했다.",
    "복습 부족": "이전 오답을 다시 풀지 않은 채 새 문제로 갔다.",
    "기타": "오늘은 분류 안 된 패턴이 발생했다.",
}


def generate_daily_report(
    records_df: pd.DataFrame,
    schedule_df: pd.DataFrame,
    today: str | None = None,
) -> dict:
    today_str = today or date.today().isoformat()
    if records_df.empty:
        return {"empty": True, "date": today_str}

    today_records = records_df[records_df["date"] == today_str]
    if today_records.empty:
        return {"empty": True, "date": today_str}

    total = len(today_records)
    correct = int(today_records["is_correct"].sum())
    wrong = total - correct
    accuracy = correct / total if total else 0.0
    avg_solve = float(today_records["solve_time_sec"].mean()) if total else 0.0

    fail_tag_stats = calculate_fail_tag_stats(today_records)

    if not fail_tag_stats.empty:
        top_tag = fail_tag_stats.iloc[0]["fail_tag"]
        core_bug = CORE_BUG_BY_TAG.get(top_tag, "오늘의 핵심 버그를 분류하지 못했다.")
        action = ACTION_RULES.get(top_tag, DEFAULT_ACTION)
    else:
        core_bug = "오늘은 오답 태그가 없다."
        action = DEFAULT_ACTION

    review_counts = _count_upcoming_reviews(schedule_df)

    return {
        "empty": False,
        "date": today_str,
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "accuracy_text": format_pct(correct, total),
        "avg_solve_text": format_secs(avg_solve),
        "fail_tag_stats": fail_tag_stats,
        "core_bug": core_bug,
        "action": action,
        "review_counts": review_counts,
    }


def _count_upcoming_reviews(schedule_df: pd.DataFrame) -> dict:
    counts = {"1d": 0, "3d": 0, "7d": 0}
    if schedule_df.empty:
        return counts
    pending = schedule_df[~schedule_df["is_done"]]
    for review_type in counts:
        counts[review_type] = int((pending["review_type"] == review_type).sum())
    return counts
