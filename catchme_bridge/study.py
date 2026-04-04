"""NCS 학습 추천 모듈.

CatchMe 메모리 데이터와 학습 진도 데이터를 교차 분석하여
사용자에게 최적의 학습 과목/유형을 추천합니다.

사용 예:
    python catchme_bridge/study.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from subprocess import TimeoutExpired

from catchme_bridge.config import run_catchme_cmd, is_catchme_installed

# NCS 과목 목록
NCS_SUBJECTS = [
    "의사소통능력",
    "수리능력",
    "문제해결능력",
    "경제학",
    "근로복지공단 전공",
    "국민건강보험법",
    "서민금융 법률",
    "서민금융 전공",
]

TRACKER_PATH = Path(__file__).parent.parent / "study" / "progress" / "tracker.json"


def get_recent_study_activity() -> dict:
    """CatchMe에서 최근 NCS 학습 활동을 조회합니다.

    Returns:
        {"activity_summary": str, "subjects_found": list[str], "error": str | None}
    """
    if not is_catchme_installed():
        return {
            "activity_summary": "",
            "subjects_found": [],
            "error": "CatchMe가 설치되어 있지 않습니다.",
        }

    try:
        result = run_catchme_cmd(
            ["ask", "--", "최근 NCS 공부 또는 시험 준비 관련 활동을 요약해줘. 어떤 과목을 공부했는지, 얼마나 했는지 알려줘."],
            timeout=120,
        )

        if result.returncode == 0 and result.stdout.strip():
            summary = result.stdout.strip()
            found_subjects = [s for s in NCS_SUBJECTS if s in summary]
            return {
                "activity_summary": summary,
                "subjects_found": found_subjects,
                "error": None,
            }
        return {"activity_summary": "", "subjects_found": [], "error": None}

    except (TimeoutExpired, RuntimeError) as e:
        return {"activity_summary": "", "subjects_found": [], "error": str(e)}


def load_tracker() -> dict | None:
    """학습 진도 추적 데이터를 로드합니다."""
    if not TRACKER_PATH.exists():
        return None
    with open(TRACKER_PATH) as f:
        return json.load(f)


def analyze_weak_subjects(tracker: dict) -> list[dict]:
    """진도 데이터에서 취약 과목을 분석합니다.

    Returns:
        [{"subject": str, "accuracy": float, "weak_types": list[str]}, ...]
    """
    weak = []
    subject_stats = tracker.get("subject_stats", {})

    for subject, stats in subject_stats.items():
        total = stats.get("total_attempted", 0)
        correct = stats.get("total_correct", 0)
        if total == 0:
            continue
        accuracy = correct / total * 100
        if accuracy < 70:
            weak.append({
                "subject": subject,
                "accuracy": round(accuracy, 1),
                "weak_types": stats.get("weak_types", []),
            })

    weak.sort(key=lambda x: x["accuracy"])
    return weak


def get_study_recommendation() -> dict:
    """CatchMe 기록과 진도 데이터를 분석하여 학습을 추천합니다.

    Returns:
        {
            "recommendation": str,
            "recommended_subjects": list[str],
            "reason": str,
            "catchme_available": bool,
            "tracker_available": bool,
        }
    """
    result = {
        "recommendation": "",
        "recommended_subjects": [],
        "reason": "",
        "catchme_available": False,
        "tracker_available": False,
    }

    # 1. CatchMe에서 최근 활동 조회
    activity = get_recent_study_activity()
    if not activity["error"]:
        result["catchme_available"] = True

    # 2. 진도 데이터 로드
    tracker = load_tracker()
    if tracker:
        result["tracker_available"] = True

    # 3. 추천 로직
    recently_studied = set(activity.get("subjects_found", []))
    not_studied = [s for s in NCS_SUBJECTS if s not in recently_studied]
    weak_subjects = []

    if tracker:
        weak_analysis = analyze_weak_subjects(tracker)
        weak_subjects = [w["subject"] for w in weak_analysis]

    # 우선순위: 취약 + 오래 안 한 과목 > 취약 과목 > 오래 안 한 과목
    priority = []

    # 취약하면서 최근에 안 한 과목 (최우선)
    for subject in weak_subjects:
        if subject in not_studied:
            priority.append(subject)

    # 나머지 취약 과목
    for subject in weak_subjects:
        if subject not in priority:
            priority.append(subject)

    # 나머지 오래 안 한 과목
    for subject in not_studied:
        if subject not in priority:
            priority.append(subject)

    # 아무 데이터도 없으면 전체 과목 추천
    if not priority:
        priority = NCS_SUBJECTS.copy()

    result["recommended_subjects"] = priority[:3]

    # 한국어 추천 메시지 생성
    if result["catchme_available"] and activity["activity_summary"]:
        result["reason"] = f"CatchMe 기록 분석 결과: {activity['activity_summary'][:200]}"
    elif result["tracker_available"] and weak_subjects:
        result["reason"] = f"진도 분석 결과, 취약 과목: {', '.join(weak_subjects[:3])}"
    else:
        result["reason"] = "아직 학습 기록이 부족하여 기본 추천을 합니다."

    subjects_str = ", ".join(result["recommended_subjects"])
    result["recommendation"] = f"오늘 추천 과목: {subjects_str}"

    return result


def format_recommendation_korean(rec: dict) -> str:
    """추천 결과를 한국어로 포맷합니다."""
    lines = []
    lines.append("=== 학습 추천 ===")
    lines.append("")
    lines.append(rec["recommendation"])
    lines.append("")
    lines.append(f"이유: {rec['reason']}")
    lines.append("")

    sources = []
    if rec["catchme_available"]:
        sources.append("CatchMe 활동 기록")
    if rec["tracker_available"]:
        sources.append("학습 진도 데이터")
    if sources:
        lines.append(f"분석 데이터: {', '.join(sources)}")
    else:
        lines.append("참고: CatchMe를 시작하고 공부를 하면 더 정확한 추천을 받을 수 있습니다.")

    return "\n".join(lines)


if __name__ == "__main__":
    rec = get_study_recommendation()
    print(format_recommendation_korean(rec))
