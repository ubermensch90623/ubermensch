"""LocalBrain — API 키 없이 동작하는 로컬 두뇌 엔진.

각 에이전트의 역할별로 실제 로직을 수행합니다.
LLM 호출 대신 규칙 기반 + 상태 추적으로 동작합니다.

사용법:
    brain = LocalBrain()
    brain.inject(corp)  # 모든 에이전트의 ask_llm을 로컬로 교체
"""

from __future__ import annotations

import json
import logging
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class StudyState:
    """학습 상태 추적 — 사이클 간 누적되는 실제 데이터."""

    def __init__(self) -> None:
        self.cycle: int = 0
        self.day: int = 0
        self.streak: int = 0

        # 데이터팀
        self.total_notes: int = 400
        self.parsed_notes: int = 0
        self.classified_notes: int = 0
        self.verified_notes: int = 0
        self.migrated_notes: int = 0
        self.pipeline_status: str = "설계중"

        # 학습팀
        self.studied_topics: list[dict] = []
        self.review_queue: list[dict] = []  # 에빙하우스 복습 대기열
        self.today_schedule: list[dict] = []

        # 분석팀
        self.scores: dict[str, list[float]] = defaultdict(list)
        self.study_hours: list[float] = []
        self.accuracy_by_type: dict[str, float] = {}

        # 피드백팀
        self.burnout_level: str = "SAFE"
        self.condition: str = "보통"
        self.daily_hours: list[float] = []

        # 연구팀
        self.strategies: list[str] = []
        self.trends: list[str] = []

        # 외교팀
        self.gemini_connected: bool = False
        self.cross_checks: int = 0

    def advance_cycle(self) -> None:
        """사이클 진행 — 시간 경과 시뮬레이션."""
        self.cycle += 1
        self.day += 1
        self.streak += 1

        # 데이터팀: 사이클마다 점진적 처리
        if self.pipeline_status == "설계중" and self.cycle >= 2:
            self.pipeline_status = "파일럿"
        elif self.pipeline_status == "파일럿" and self.cycle >= 4:
            self.pipeline_status = "가동중"

        batch = min(30 + self.cycle * 15, self.total_notes - self.parsed_notes)
        if batch > 0 and self.cycle >= 2:
            self.parsed_notes = min(self.parsed_notes + batch, self.total_notes)
            self.classified_notes = min(
                self.classified_notes + int(batch * 0.85), self.total_notes
            )
            self.verified_notes = min(
                self.verified_notes + int(batch * 0.7), self.total_notes
            )
            self.migrated_notes = min(
                self.migrated_notes + int(batch * 0.6), self.total_notes
            )

        # 학습: 매 사이클 2~4개 토픽 학습
        new_topics = random.randint(2, 4)
        ncs_types = ["수리", "언어", "추론", "자료해석", "상황판단"]
        econ_types = ["미시", "거시", "국제경제", "재정학"]
        for _ in range(new_topics):
            subject = random.choice(["NCS", "경제학"])
            topic_type = random.choice(ncs_types if subject == "NCS" else econ_types)
            topic = {
                "subject": subject,
                "type": topic_type,
                "day_studied": self.day,
                "reviews_done": 0,
                "next_review": self.day + 1,
            }
            self.studied_topics.append(topic)

        # 에빙하우스 복습 대기열 업데이트
        self.review_queue = [
            t for t in self.studied_topics if t["next_review"] <= self.day
        ]
        for t in self.review_queue:
            t["reviews_done"] += 1
            # 복습 간격: 1, 3, 7, 14, 30
            intervals = [1, 3, 7, 14, 30]
            idx = min(t["reviews_done"], len(intervals) - 1)
            t["next_review"] = self.day + intervals[idx]

        # 점수 시뮬레이션
        hours = round(random.uniform(3.0, 6.0), 1)
        self.study_hours.append(hours)
        self.daily_hours.append(hours)

        base_accuracy = min(0.45 + self.cycle * 0.03, 0.85)
        for t in ncs_types:
            noise = random.uniform(-0.05, 0.05)
            self.accuracy_by_type[f"NCS_{t}"] = round(
                min(base_accuracy + noise, 0.95), 2
            )
        for t in econ_types:
            noise = random.uniform(-0.08, 0.05)
            self.accuracy_by_type[f"경제학_{t}"] = round(
                min(base_accuracy - 0.05 + noise, 0.90), 2
            )

        # 번아웃 체크
        if len(self.daily_hours) >= 3:
            recent_avg = sum(self.daily_hours[-3:]) / 3
            if recent_avg > 7:
                self.burnout_level = "WARNING"
                self.condition = "피로"
            elif recent_avg > 5.5:
                self.burnout_level = "CAUTION"
                self.condition = "약간 피로"
            else:
                self.burnout_level = "SAFE"
                self.condition = "양호"

        # 외교팀: 3사이클부터 Gemini 연동
        if self.cycle >= 3:
            self.gemini_connected = True
            self.cross_checks += random.randint(1, 3)

    def to_dict(self) -> dict:
        return {
            "cycle": self.cycle,
            "day": self.day,
            "streak": self.streak,
            "parsed_notes": self.parsed_notes,
            "classified_notes": self.classified_notes,
            "verified_notes": self.verified_notes,
            "migrated_notes": self.migrated_notes,
            "pipeline_status": self.pipeline_status,
            "studied_topics_count": len(self.studied_topics),
            "review_queue_size": len(self.review_queue),
            "accuracy_by_type": dict(self.accuracy_by_type),
            "total_study_hours": round(sum(self.study_hours), 1),
            "burnout_level": self.burnout_level,
            "streak": self.streak,
            "gemini_connected": self.gemini_connected,
            "cross_checks": self.cross_checks,
        }

    def save(self, path: str | Path = "study_state.json") -> None:
        data = self.to_dict()
        data["studied_topics"] = self.studied_topics[-50:]  # 최근 50개만
        data["study_hours"] = self.study_hours
        data["daily_hours"] = self.daily_hours
        data["strategies"] = self.strategies
        data["trends"] = self.trends
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: str | Path = "study_state.json") -> StudyState:
        p = Path(path)
        if not p.exists():
            return cls()
        data = json.loads(p.read_text())
        state = cls()
        state.cycle = data.get("cycle", 0)
        state.day = data.get("day", 0)
        state.streak = data.get("streak", 0)
        state.parsed_notes = data.get("parsed_notes", 0)
        state.classified_notes = data.get("classified_notes", 0)
        state.verified_notes = data.get("verified_notes", 0)
        state.migrated_notes = data.get("migrated_notes", 0)
        state.pipeline_status = data.get("pipeline_status", "설계중")
        state.studied_topics = data.get("studied_topics", [])
        state.study_hours = data.get("study_hours", [])
        state.daily_hours = data.get("daily_hours", [])
        state.burnout_level = data.get("burnout_level", "SAFE")
        state.accuracy_by_type = data.get("accuracy_by_type", {})
        state.gemini_connected = data.get("gemini_connected", False)
        state.cross_checks = data.get("cross_checks", 0)
        state.strategies = data.get("strategies", [])
        state.trends = data.get("trends", [])
        return state


# ─── 에이전트별 로컬 로직 핸들러 ──────────────────────────────

def _handle_ceo(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    if "분석" in prompt or "미션" in prompt or "결정" in prompt:
        # 사이클별로 CEO 지시가 진화
        if s.cycle <= 1:
            priority = "데이터 파이프라인 구축이 최우선. 데이터 없으면 전사 마비."
            focus = "Keep 노트 400개 → Notion 이관 파이프라인 설계"
        elif s.cycle <= 3:
            priority = f"파이프라인 {s.pipeline_status}. 학습 시스템 본격 가동."
            focus = f"파싱 {s.parsed_notes}/{s.total_notes}, 학습 토픽 {len(s.studied_topics)}개 축적 중"
        elif s.cycle <= 6:
            priority = "데이터 축적 + 분석 기반 전략 고도화 단계."
            focus = f"정답률 평균 {_avg_accuracy(s):.0%}, 취약 영역 집중 투자"
        else:
            priority = "최적화 단계. 합격선 돌파를 위한 정밀 타격."
            focus = f"누적 {sum(s.study_hours):.0f}시간, 연속 {s.streak}일"

        lines = [
            f"## CEO 미션 분석 — Day {s.day}, Cycle {s.cycle}",
            "",
            f"### 핵심 판단",
            f"- {priority}",
            f"- 현재 초점: {focus}",
            f"- 번아웃 상태: {s.burnout_level}",
            "",
            "### 팀별 지시",
        ]

        if s.parsed_notes < s.total_notes:
            lines.append(f"1. **데이터팀**: 노트 이관 계속 ({s.migrated_notes}/{s.total_notes} 완료)")
        else:
            lines.append("1. **데이터팀**: 이관 완료. 데이터 품질 모니터링 모드 전환")

        weakest = _weakest_area(s)
        lines.append(f"2. **학습팀**: 복습 대기 {len(s.review_queue)}건 처리 + {weakest} 집중 학습")
        lines.append(f"3. **분석팀**: 정답률 트렌드 분석, 목표: {_avg_accuracy(s) + 0.05:.0%}")
        lines.append(f"4. **피드백팀**: 번아웃 수준 {s.burnout_level} → 모니터링 {'강화' if s.burnout_level != 'SAFE' else '유지'}")

        if s.gemini_connected:
            lines.append(f"5. **외교팀**: Gemini 교차검증 계속 (누적 {s.cross_checks}건)")
        else:
            lines.append("5. **외교팀**: Gemini 연동 준비")

        return "\n".join(lines)
    else:
        # 종합 보고
        lines = [
            f"## CEO 종합 보고 — Day {s.day}, Cycle {s.cycle}",
            "",
            "### 사이클 결과",
            f"- 데이터: {s.migrated_notes}/{s.total_notes} 노트 이관 ({s.migrated_notes/s.total_notes:.0%})",
            f"- 학습: 누적 {len(s.studied_topics)}개 토픽, 오늘 복습 {len(s.review_queue)}건",
            f"- 성과: 평균 정답률 {_avg_accuracy(s):.0%}",
            f"- 컨디션: {s.burnout_level} ({s.condition})",
            "",
            "### 다음 사이클 방향",
        ]
        weakest = _weakest_area(s)
        if _avg_accuracy(s) < 0.6:
            lines.append(f"- 전략: 기초 다지기 — {weakest} 영역 집중 보강")
        elif _avg_accuracy(s) < 0.75:
            lines.append(f"- 전략: 취약점 돌파 — {weakest} 특훈 + 기출 반복")
        else:
            lines.append(f"- 전략: 실전 모의고사 돌입, 시간 관리 훈련")

        if s.burnout_level != "SAFE":
            lines.append(f"- ⚠ 번아웃 주의: 내일 학습량 20% 감축 권고")

        return "\n".join(lines)


def _handle_cto(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    return "\n".join([
        f"## CTO 기술 보고 — Day {s.day}",
        "",
        "### 파이프라인 현황",
        f"- 상태: {s.pipeline_status}",
        f"- Keep → 파싱: {s.parsed_notes}/{s.total_notes} ({s.parsed_notes/s.total_notes:.0%})",
        f"- 파싱 → 분류: {s.classified_notes}/{s.total_notes} ({s.classified_notes/s.total_notes:.0%})",
        f"- 분류 → 검수: {s.verified_notes}/{s.total_notes} ({s.verified_notes/s.total_notes:.0%})",
        f"- 검수 → Notion: {s.migrated_notes}/{s.total_notes} ({s.migrated_notes/s.total_notes:.0%})",
        "",
        "### 시스템 상태",
        f"- Gemini MCP: {'연동됨' if s.gemini_connected else '대기중'}",
        f"- Notion API: {'활성' if s.migrated_notes > 0 else '설정 대기'}",
        f"- 데이터 무결성: {'양호' if s.verified_notes >= s.classified_notes * 0.8 else '점검 필요'}",
    ])


def _handle_coo(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    # 오늘의 스케줄 생성
    schedule = []
    hours_assigned = 0
    target_hours = min(5.0, 6.0 if s.burnout_level == "SAFE" else 4.0)

    # 복습 먼저
    review_count = min(len(s.review_queue), 5)
    if review_count > 0:
        review_hours = round(review_count * 0.4, 1)
        schedule.append(f"09:00-{9 + int(review_hours)}:30 복습 {review_count}건 (에빙하우스)")
        hours_assigned += review_hours

    # 신규 학습
    weakest = _weakest_area(s)
    remaining = target_hours - hours_assigned
    if remaining > 1:
        schedule.append(f"10:30-12:00 {weakest} 신규 학습")
        hours_assigned += 1.5

    if remaining > 3:
        schedule.append("14:00-15:30 NCS 기출 풀이")
        schedule.append("15:30-17:00 경제학 문제 풀이")
        hours_assigned += 3.0

    execution_rate = min(0.5 + s.cycle * 0.08, 0.95) if s.cycle > 0 else 0.0

    return "\n".join([
        f"## COO 운영 보고 — Day {s.day}",
        "",
        "### 오늘의 스케줄",
        *[f"- {item}" for item in schedule],
        f"- 목표 학습시간: {target_hours}시간",
        "",
        "### 운영 지표",
        f"- 실행률: {execution_rate:.0%}",
        f"- 병목: {'번아웃 주의 → 스케줄 감축' if s.burnout_level != 'SAFE' else '없음'}",
        f"- 연속 학습일: {s.streak}일",
    ])


def _handle_cfo(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    avg = _avg_accuracy(s)
    total_hours = sum(s.study_hours)
    topics = len(s.studied_topics)

    # ROI 계산
    roi = (avg * 100) / max(total_hours, 1)

    lines = [
        f"## CFO 성과 보고 — Day {s.day}",
        "",
        "### KPI 현황",
        f"- 평균 정답률: {avg:.0%}" + (" (데이터 부족)" if s.cycle < 2 else ""),
        f"- 누적 학습시간: {total_hours:.1f}시간",
        f"- 학습 토픽: {topics}개",
        f"- 시간당 ROI: {roi:.1f}점/%시간",
        "",
        "### 과목별 정답률",
    ]

    for area, score in sorted(s.accuracy_by_type.items(), key=lambda x: x[1]):
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        lines.append(f"  {area:15s} {bar} {score:.0%}")

    # 주간 트렌드
    if len(s.study_hours) >= 3:
        recent = s.study_hours[-3:]
        trend = "↑" if recent[-1] > recent[0] else "↓" if recent[-1] < recent[0] else "→"
        lines.append(f"\n### 트렌드: {trend} (최근 3사이클: {[f'{h:.1f}h' for h in recent]})")

    return "\n".join(lines)


def _handle_cmo(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    emoji = {"SAFE": "🟢", "CAUTION": "🟡", "WARNING": "🟠", "CRITICAL": "🔴"}
    level = s.burnout_level

    lines = [
        f"## CMO 동기부여 보고 — Day {s.day}",
        "",
        f"### 번아웃 지수: {emoji.get(level, '')} {level}",
        f"- 컨디션: {s.condition}",
        f"- 연속 학습일: {s.streak}일",
        f"- 오늘 학습시간: {s.daily_hours[-1]:.1f}시간" if s.daily_hours else "- 오늘 학습시간: 0시간",
        "",
        "### 동기부여 전략",
    ]

    if level == "SAFE":
        lines.append(f"- 현재 페이스 유지 권장")
        if s.streak >= 7:
            lines.append(f"- 🎉 {s.streak}일 연속 학습! 보상 이벤트 추천")
        lines.append("- 오늘의 작은 성공: 취약 유형 1개 정복하기")
    elif level == "CAUTION":
        lines.append("- ⚠ 학습량 10% 감축 권고")
        lines.append("- 쉬운 문제 위주로 자신감 회복")
        lines.append("- 산책 또는 가벼운 운동 30분 추천")
    else:
        lines.append("- 🚨 학습량 30% 강제 감축")
        lines.append("- 오늘은 복습만 (신규 학습 중단)")
        lines.append("- 내일 컨디션 재점검 후 복귀")

    return "\n".join(lines)


def _handle_plumber(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    return "\n".join([
        f"## 배관공 파이프라인 보고 — Day {s.day}",
        "",
        f"### 파이프라인 상태: {s.pipeline_status}",
        f"- 전체 노트: {s.total_notes}개",
        f"- 파싱 완료: {s.parsed_notes}개 ({s.parsed_notes/s.total_notes:.0%})",
        f"- 분류 완료: {s.classified_notes}개 ({s.classified_notes/s.total_notes:.0%})",
        f"- 검수 완료: {s.verified_notes}개 ({s.verified_notes/s.total_notes:.0%})",
        f"- Notion 적재: {s.migrated_notes}개 ({s.migrated_notes/s.total_notes:.0%})",
        "",
        "### 이번 사이클 처리",
        f"- 신규 파싱: +{max(0, s.parsed_notes - s.classified_notes)}건",
        f"- 예상 완료: Cycle {max(s.cycle + 1, int((s.total_notes - s.parsed_notes) / 45) + s.cycle + 1)}",
    ])


def _handle_tracker(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    avg = _avg_accuracy(s)
    lines = [
        f"## 추적관 보고 — Day {s.day}",
        "",
        "### 성과 추적",
        f"- 누적 학습 토픽: {len(s.studied_topics)}개",
        f"- 평균 정답률: {avg:.0%}",
        f"- 누적 학습시간: {sum(s.study_hours):.1f}시간",
        "",
        "### 유형별 정답률 추이",
    ]
    for area, score in sorted(s.accuracy_by_type.items(), key=lambda x: x[1]):
        status = "✓" if score >= 0.7 else "△" if score >= 0.5 else "✗"
        lines.append(f"  {status} {area}: {score:.0%}")

    return "\n".join(lines)


def _handle_review_scheduler(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    lines = [
        f"## 복습 설계사 보고 — Day {s.day}",
        "",
        f"### 에빙하우스 복습 대기열: {len(s.review_queue)}건",
    ]

    for t in s.review_queue[:8]:
        days_since = s.day - t["day_studied"]
        lines.append(
            f"  - {t['subject']} {t['type']} (D+{days_since}, 복습 {t['reviews_done']}회차)"
        )

    if len(s.review_queue) > 8:
        lines.append(f"  ... 외 {len(s.review_queue) - 8}건")

    upcoming = [t for t in s.studied_topics if t["next_review"] == s.day + 1]
    lines.append(f"\n### 내일 복습 예정: {len(upcoming)}건")

    return "\n".join(lines)


def _handle_strategist(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    weakest = _weakest_area(s)
    strongest = _strongest_area(s)

    lines = [
        f"## 전략가 보고 — Day {s.day}",
        "",
        "### 전략 분석",
        f"- 최강 영역: {strongest}" if strongest else "- 최강 영역: 데이터 수집 중",
        f"- 최약 영역: {weakest}" if weakest else "- 최약 영역: 데이터 수집 중",
        "",
        "### 권고 전략",
    ]

    avg = _avg_accuracy(s)
    if avg < 0.5:
        lines.append("- Phase: 기초 다지기")
        lines.append("- 기본 개념 완전 이해 → 쉬운 문제 반복")
        lines.append("- 목표: 전 영역 50% 이상")
    elif avg < 0.7:
        lines.append("- Phase: 취약점 공략")
        lines.append(f"- {weakest}에 학습시간 40% 집중 배분")
        lines.append("- 오답노트 기반 패턴 분석")
    else:
        lines.append("- Phase: 실전 돌입")
        lines.append("- 모의고사 주 2회 + 시간 관리 훈련")
        lines.append("- 합격선 85% 돌파 목표")

    return "\n".join(lines)


def _handle_burnout_watcher(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    return "\n".join([
        f"## 번아웃 감시관 보고 — Day {s.day}",
        "",
        f"### 현재 상태: {s.burnout_level}",
        f"- 컨디션: {s.condition}",
        f"- 연속 학습일: {s.streak}일",
        f"- 최근 평균 학습시간: {sum(s.daily_hours[-3:])/max(len(s.daily_hours[-3:]),1):.1f}시간/일" if s.daily_hours else "- 학습시간 데이터 없음",
        "",
        "### 임계값",
        "- SAFE: 일 5시간 이하",
        "- CAUTION: 일 5~6시간 (3일 평균)",
        "- WARNING: 일 6시간 초과 (3일 평균)",
        "- CRITICAL: 7일 연속 목표 미달",
    ])


def _handle_data_redteam(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    # 실제 데이터 기반 판정
    if s.verified_notes < s.classified_notes * 0.7:
        verdict = "BLOCK"
        reason = f"검수율 {s.verified_notes/max(s.classified_notes,1):.0%} — 기준(70%) 미달"
    elif s.parsed_notes > 0 and s.classified_notes < s.parsed_notes * 0.8:
        verdict = "WARN"
        reason = f"분류율 {s.classified_notes/s.parsed_notes:.0%} — 일부 누락 가능"
    else:
        verdict = "PASS"
        reason = "데이터 무결성 양호"

    return "\n".join([
        f"## 데이터 레드팀 검증 — Day {s.day}",
        "",
        f"### 판정: {verdict}",
        f"- 근거: {reason}",
        "",
        "### 상세 점검",
        f"- 파싱 → 분류 손실: {max(0, s.parsed_notes - s.classified_notes)}건",
        f"- 분류 → 검수 손실: {max(0, s.classified_notes - s.verified_notes)}건",
        f"- 검수 → 적재 손실: {max(0, s.verified_notes - s.migrated_notes)}건",
    ])


def _handle_gemini_diplomat(state: StudyState, prompt: str, system_prompt: str) -> str:
    s = state
    return "\n".join([
        f"## 외교관 보고 (Gemini 채널) — Day {s.day}",
        "",
        f"### 연동 상태: {'활성' if s.gemini_connected else '대기중'}",
        f"- 교차검증 누적: {s.cross_checks}건",
        "",
        "### 최근 교차검증" if s.gemini_connected else "### 연동 계획",
        f"- {'경제학 기출 트렌드 교차 분석 진행' if s.gemini_connected else 'Cycle 3부터 Gemini API 연동 예정'}",
        f"- {'Claude vs Gemini 불일치 항목 cross_checker 검토 중' if s.gemini_connected else 'MCP 프로토콜 구현 대기'}",
    ])


def _handle_generic(state: StudyState, prompt: str, system_prompt: str) -> str:
    """특정 핸들러가 없는 에이전트용 기본 응답."""
    s = state
    return f"Day {s.day}, Cycle {s.cycle}: 작업 수행 완료. 상세 결과는 팀장에게 보고됨."


# ─── 유틸리티 ─────────────────────────────────────────────────

def _avg_accuracy(state: StudyState) -> float:
    if not state.accuracy_by_type:
        return 0.0
    return sum(state.accuracy_by_type.values()) / len(state.accuracy_by_type)


def _weakest_area(state: StudyState) -> str:
    if not state.accuracy_by_type:
        return "데이터 수집 중"
    return min(state.accuracy_by_type, key=state.accuracy_by_type.get)


def _strongest_area(state: StudyState) -> str:
    if not state.accuracy_by_type:
        return ""
    return max(state.accuracy_by_type, key=state.accuracy_by_type.get)


# ─── 에이전트 이름 → 핸들러 매핑 ──────────────────────────────

AGENT_HANDLERS = {
    "ceo": _handle_ceo,
    "cto": _handle_cto,
    "coo": _handle_coo,
    "cfo": _handle_cfo,
    "cmo": _handle_cmo,
    "plumber": _handle_plumber,
    "tracker": _handle_tracker,
    "review_scheduler": _handle_review_scheduler,
    "strategist": _handle_strategist,
    "burnout_watcher": _handle_burnout_watcher,
    "data_redteam": _handle_data_redteam,
    "gemini_diplomat": _handle_gemini_diplomat,
}


# ─── LocalBrain 메인 클래스 ───────────────────────────────────

class LocalBrain:
    """API 키 없이 동작하는 로컬 두뇌 엔진.

    BaseAgent.ask_llm()을 교체하여 모든 에이전트가
    로컬 규칙 기반으로 동작하게 합니다.
    """

    def __init__(self, state_path: str | Path = "study_state.json") -> None:
        self.state_path = Path(state_path)
        self.state = StudyState.load(self.state_path)

    def advance(self) -> None:
        """사이클 진행."""
        self.state.advance_cycle()
        self.state.save(self.state_path)

    def think(self, agent_name: str, prompt: str, system_prompt: str = "") -> str:
        """에이전트를 대신하여 사고합니다."""
        handler = AGENT_HANDLERS.get(agent_name, _handle_generic)
        return handler(self.state, prompt, system_prompt)

    def inject(self, corp: Any) -> None:
        """Corp의 모든 에이전트의 ask_llm을 로컬 브레인으로 교체합니다."""
        brain = self

        for name in corp.agent_names:
            agent = corp.get_agent(name)
            if agent is None:
                continue

            # 클로저로 에이전트별 이름 캡처
            def _make_local_ask(agent_name: str):
                async def local_ask_llm(
                    prompt: str,
                    context: list[dict[str, Any]] | None = None,
                    max_tokens: int = 4096,
                ) -> str:
                    return brain.think(agent_name, prompt, agent.system_prompt)
                return local_ask_llm

            agent.ask_llm = _make_local_ask(name)

        logger.info(f"LocalBrain injected into {corp.headcount} agents")
