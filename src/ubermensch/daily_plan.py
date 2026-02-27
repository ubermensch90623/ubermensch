"""오늘의 학습 플랜 생성기.

CEO가 현재 상태를 분석하고 오늘 해야 할 일을 구체적으로 내린다.
`python -m ubermensch today` 한 줄로 실행.

출력:
- 오늘의 복습 리스트 (에빙하우스)
- 신규 학습 추천 (취약 영역 기반)
- 퀴즈 (파싱된 노트에서 추출)
- 시간 배분표
- 번아웃 경고
"""

from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

from ubermensch.core.local_brain import StudyState
from ubermensch.data.note import Note, NoteCategory, NoteType, load_notes


def generate_daily_plan(
    study_state_path: str | Path = "study_state.json",
    notes_path: str | Path = "notes.json",
) -> str:
    """오늘의 학습 플랜을 생성합니다."""
    state = StudyState.load(study_state_path)
    notes = _load_notes_safe(notes_path)

    lines: list[str] = []

    # 헤더
    lines.append("╔══════════════════════════════════════════════════╗")
    lines.append(f"║  Learning Agent Corp. — Day {state.day + 1} 일일 플랜")
    lines.append(f"║  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("╚══════════════════════════════════════════════════╝")

    # 현황 요약
    lines.append("")
    lines.append(_status_bar(state))

    # 1. 복습 (에빙하우스)
    lines.append("")
    lines.append(_review_section(state))

    # 2. 취약 영역 집중 학습
    lines.append("")
    lines.append(_weakness_section(state))

    # 3. 오늘의 시간표
    lines.append("")
    lines.append(_schedule_section(state))

    # 4. 퀴즈
    if notes:
        lines.append("")
        lines.append(_quiz_section(notes, state))

    # 5. 번아웃 체크
    lines.append("")
    lines.append(_burnout_section(state))

    # 6. CEO 한마디
    lines.append("")
    lines.append(_ceo_message(state))

    return "\n".join(lines)


def _status_bar(state: StudyState) -> str:
    """현황 요약 바."""
    avg = _avg_accuracy(state)
    total_h = sum(state.study_hours)

    # 정답률 프로그레스 바
    filled = int(avg * 20)
    bar = "█" * filled + "░" * (20 - filled)

    lines = [
        "── 현황 ──────────────────────────────────────────",
        f"  연속 학습: {state.streak}일  |  누적: {total_h:.0f}시간  |  토픽: {len(state.studied_topics)}개",
        f"  정답률:    [{bar}] {avg:.0%}",
        f"  컨디션:    {state.burnout_level} ({state.condition})",
    ]
    return "\n".join(lines)


def _review_section(state: StudyState) -> str:
    """에빙하우스 복습 섹션."""
    tomorrow = state.day + 1
    due = [t for t in state.studied_topics if t.get("next_review", 999) <= tomorrow]

    lines = ["── 오늘의 복습 (에빙하우스) ─────────────────────────"]

    if not due:
        lines.append("  복습 대기 없음. 신규 학습에 집중하세요.")
        return "\n".join(lines)

    lines.append(f"  총 {len(due)}건 복습 예정:")
    for i, t in enumerate(due[:10], 1):
        days_ago = tomorrow - t["day_studied"]
        review_num = t["reviews_done"] + 1
        lines.append(f"  {i}. [{t['subject']}] {t['type']} — D+{days_ago}, {review_num}회차 복습")

    if len(due) > 10:
        lines.append(f"  ... 외 {len(due) - 10}건")

    est_min = len(due) * 8  # 건당 약 8분
    lines.append(f"  예상 소요: ~{est_min}분")

    return "\n".join(lines)


def _weakness_section(state: StudyState) -> str:
    """취약 영역 분석 + 학습 추천."""
    lines = ["── 취약 영역 집중 학습 ──────────────────────────────"]

    if not state.accuracy_by_type:
        lines.append("  아직 데이터 부족. 오늘 첫 학습을 시작하세요!")
        return "\n".join(lines)

    # 하위 3개 영역
    sorted_areas = sorted(state.accuracy_by_type.items(), key=lambda x: x[1])
    weak = sorted_areas[:3]
    strong = sorted_areas[-2:]

    lines.append("  ✗ 취약 (집중 필요):")
    for area, score in weak:
        lines.append(f"    → {area}: {score:.0%}")

    lines.append("  ✓ 강점 (유지):")
    for area, score in strong:
        lines.append(f"    → {area}: {score:.0%}")

    # 추천
    target = weak[0][0] if weak else "전 영역"
    lines.append(f"\n  📌 오늘의 집중 영역: {target}")
    lines.append(f"     목표: {weak[0][1] + 0.05:.0%} 달성" if weak else "")

    return "\n".join(lines)


def _schedule_section(state: StudyState) -> str:
    """시간 배분표."""
    is_tired = state.burnout_level != "SAFE"
    total_target = 4.0 if is_tired else 5.5

    tomorrow = state.day + 1
    review_count = len([t for t in state.studied_topics if t.get("next_review", 999) <= tomorrow])
    review_hours = min(review_count * 0.15, 1.5)

    weakest = _weakest_area(state)

    schedule = []
    current = 9.0  # 9시 시작

    # 복습
    if review_count > 0:
        end = current + review_hours
        schedule.append((current, end, f"복습 {review_count}건 (에빙하우스)"))
        current = end + 0.25  # 15분 휴식

    # 취약 영역
    weak_hours = min(1.5, total_target * 0.35)
    schedule.append((current, current + weak_hours, f"{weakest} 집중 학습"))
    current += weak_hours + 0.5  # 30분 점심

    # 기출 풀이
    if current + 1.5 <= 17.0:
        schedule.append((current, current + 1.5, "기출 문제 풀이"))
        current += 1.5 + 0.25

    # 오답 정리
    if current + 1.0 <= 17.5:
        schedule.append((current, current + 1.0, "오답 노트 정리 + 복습"))

    lines = ["── 오늘의 시간표 ────────────────────────────────────"]
    if is_tired:
        lines.append(f"  ⚠ 컨디션 {state.burnout_level} — 학습량 감축 ({total_target}시간)")
    else:
        lines.append(f"  목표: {total_target}시간")

    lines.append("")
    for start, end, task in schedule:
        sh, sm = int(start), int((start % 1) * 60)
        eh, em = int(end), int((end % 1) * 60)
        lines.append(f"  {sh:02d}:{sm:02d} ~ {eh:02d}:{em:02d}  {task}")

    return "\n".join(lines)


def _quiz_section(notes: list[Note], state: StudyState) -> str:
    """파싱된 노트에서 퀴즈 생성."""
    lines = ["── 오늘의 퀴즈 ──────────────────────────────────────"]

    # 문제/오답분석 유형 노트에서 퀴즈 추출
    quiz_candidates = [
        n for n in notes
        if n.note_type in (NoteType.PROBLEM, NoteType.WRONG_ANSWER, NoteType.CONCEPT)
        and len(n.content) > 30
    ]

    if not quiz_candidates:
        lines.append("  퀴즈 소스 노트가 없습니다. Keep 노트를 파이프라인에 넣어주세요.")
        return "\n".join(lines)

    # 취약 영역 우선 선택
    weakest = _weakest_area(state)
    weak_notes = [n for n in quiz_candidates if weakest and weakest.split("_")[-1] in n.subject]
    pool = weak_notes if weak_notes else quiz_candidates

    selected = random.sample(pool, min(3, len(pool)))

    for i, note in enumerate(selected, 1):
        lines.append(f"\n  Q{i}. [{note.category.value}/{note.subject}] {note.title}")
        # 내용에서 첫 3줄만 보여주기
        content_lines = note.content.strip().split("\n")
        for cl in content_lines[:3]:
            lines.append(f"      {cl.strip()}")
        if len(content_lines) > 3:
            lines.append(f"      ... (전체 {len(content_lines)}줄)")

    lines.append(f"\n  총 {len(quiz_candidates)}개 노트에서 추출 가능")

    return "\n".join(lines)


def _burnout_section(state: StudyState) -> str:
    """번아웃 체크."""
    level = state.burnout_level
    lines = ["── 번아웃 체크 ──────────────────────────────────────"]

    if level == "SAFE":
        lines.append(f"  🟢 SAFE — 컨디션 양호. 오늘도 화이팅!")
        if state.streak >= 7:
            lines.append(f"  🎉 {state.streak}일 연속 학습 중! 대단합니다.")
    elif level == "CAUTION":
        lines.append(f"  🟡 CAUTION — 약간 피로 감지.")
        lines.append(f"  → 오늘은 목표 시간 10% 감축 권장")
        lines.append(f"  → 산책 30분 추천")
    elif level == "WARNING":
        lines.append(f"  🟠 WARNING — 피로 누적.")
        lines.append(f"  → 오늘은 복습만 (신규 학습 중단)")
        lines.append(f"  → 학습 시간 4시간 이내로 제한")
    else:
        lines.append(f"  🔴 CRITICAL — 강제 휴식 권고.")
        lines.append(f"  → 오늘은 쉬세요. 내일 재개.")

    return "\n".join(lines)


def _ceo_message(state: StudyState) -> str:
    """CEO 한마디."""
    avg = _avg_accuracy(state)
    lines = ["── CEO 한마디 ───────────────────────────────────────"]

    if state.day == 0:
        lines.append("  \"첫 걸음을 내딛었습니다. 데이터부터 쌓겠습니다.\"")
    elif avg < 0.5:
        lines.append("  \"기초를 다지는 시간입니다. 서두르지 마세요.\"")
    elif avg < 0.7:
        weakest = _weakest_area(state)
        lines.append(f"  \"{weakest}만 돌파하면 합격선이 보입니다. 집중하세요.\"")
    elif avg < 0.85:
        lines.append(f"  \"정답률 {avg:.0%}. 합격선 돌파까지 정밀 타격 모드.\"")
    else:
        lines.append(f"  \"정답률 {avg:.0%}. 실전 모의고사로 전환합니다.\"")

    lines.append("")
    lines.append("══════════════════════════════════════════════════")

    return "\n".join(lines)


# ─── 유틸 ─────────────────────────────────────────────────────

def _avg_accuracy(state: StudyState) -> float:
    if not state.accuracy_by_type:
        return 0.0
    return sum(state.accuracy_by_type.values()) / len(state.accuracy_by_type)


def _weakest_area(state: StudyState) -> str:
    if not state.accuracy_by_type:
        return "전 영역"
    return min(state.accuracy_by_type, key=state.accuracy_by_type.get)


def _load_notes_safe(path: str | Path) -> list[Note]:
    try:
        return load_notes(path)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
