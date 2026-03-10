"""
수집된 자료 분석 및 정리
- 크롤링 결과에서 시험 관련 정보 추출
- 기관별/과목별 분류
- 출제 패턴 분석용 데이터 정리
"""

import json
import os
import re
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def extract_exam_info(crawl_data: dict) -> dict:
    """크롤링 결과에서 시험 관련 정보만 추출"""
    exam_info = {
        "extracted_at": datetime.now().isoformat(),
        "institutions": {},
        "common_ncs": [],
        "exam_reviews": [],
        "question_patterns": [],
        "recruitment_info": [],
    }

    ncs_keywords = [
        "NCS", "직업기초", "의사소통", "수리능력", "문제해결",
        "자원관리", "정보능력", "조직이해", "기출", "필기",
        "시험", "채용", "모의고사", "합격", "후기",
    ]

    for result in crawl_data.get("results", []):
        if not result.get("success"):
            continue

        content = result.get("content", "")
        source_type = result.get("source_type", "")
        source_name = result.get("source_name", "")

        # NCS 관련 키워드가 포함된 콘텐츠만 필터링
        relevance_score = sum(1 for kw in ncs_keywords if kw in content)
        if relevance_score < 2:
            continue

        entry = {
            "source": source_name,
            "url": result.get("url", ""),
            "title": result.get("title", ""),
            "relevance": relevance_score,
            "type": source_type,
            "content_preview": content[:2000],
            "links": [
                link for link in result.get("links", [])
                if any(kw in link.get("text", "") for kw in ncs_keywords)
            ][:20],
        }

        if source_type == "recruitment":
            exam_info["recruitment_info"].append(entry)
        elif source_type in ("official_questions", "mock_exam"):
            exam_info["common_ncs"].append(entry)
        elif source_type in ("exam_review", "community"):
            exam_info["exam_reviews"].append(entry)
        else:
            exam_info["common_ncs"].append(entry)

    return exam_info


def analyze_patterns(exam_info: dict) -> dict:
    """출제 패턴 분석"""
    patterns = {
        "subject_frequency": {},
        "question_types": {},
        "difficulty_hints": [],
        "key_topics": [],
    }

    subject_keywords = {
        "의사소통능력": ["의사소통", "언어", "독해", "문서", "작성", "맞춤법"],
        "수리능력": ["수리", "수학", "계산", "통계", "비율", "증감률", "자료해석"],
        "문제해결능력": ["문제해결", "논리", "추론", "판단", "분석", "SWOT"],
        "자원관리능력": ["자원관리", "예산", "일정", "인력", "시간관리"],
        "정보능력": ["정보", "컴퓨터", "데이터", "소프트웨어", "네트워크"],
        "조직이해능력": ["조직", "경영", "업무", "회의", "규정"],
    }

    all_content = ""
    for category in ["common_ncs", "exam_reviews", "recruitment_info"]:
        for entry in exam_info.get(category, []):
            all_content += " " + entry.get("content_preview", "")

    # 과목별 빈도 분석
    for subject, keywords in subject_keywords.items():
        count = sum(all_content.count(kw) for kw in keywords)
        patterns["subject_frequency"][subject] = count

    # 난이도 힌트 추출
    difficulty_words = {
        "쉬움": ["쉬운", "쉬웠", "기본", "기초", "평이"],
        "보통": ["보통", "적당", "무난", "평균"],
        "어려움": ["어려운", "어려웠", "고난도", "까다", "함정"],
    }
    for level, words in difficulty_words.items():
        count = sum(all_content.count(w) for w in words)
        if count > 0:
            patterns["difficulty_hints"].append({"level": level, "mentions": count})

    return patterns


def generate_summary(exam_info: dict, patterns: dict) -> str:
    """수집된 자료 요약 생성"""
    lines = ["# 크롤링 결과 요약\n"]
    lines.append(f"분석 시점: {exam_info.get('extracted_at', '')}\n")

    # 수집 현황
    total = sum(
        len(exam_info.get(cat, []))
        for cat in ["common_ncs", "exam_reviews", "recruitment_info"]
    )
    lines.append(f"## 수집 현황")
    lines.append(f"- 총 수집 자료: {total}건")
    lines.append(f"  - NCS 공통 자료: {len(exam_info.get('common_ncs', []))}건")
    lines.append(f"  - 시험 후기: {len(exam_info.get('exam_reviews', []))}건")
    lines.append(f"  - 채용 공고: {len(exam_info.get('recruitment_info', []))}건\n")

    # 과목별 출제 빈도
    lines.append("## 과목별 출제 빈도 (추정)")
    freq = patterns.get("subject_frequency", {})
    sorted_subjects = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    for subject, count in sorted_subjects:
        bar = "█" * min(count // 5, 20)
        lines.append(f"- {subject}: {bar} ({count})")

    lines.append("")

    # 난이도 분석
    if patterns.get("difficulty_hints"):
        lines.append("## 난이도 힌트")
        for hint in patterns["difficulty_hints"]:
            lines.append(f"- {hint['level']}: {hint['mentions']}회 언급")

    return "\n".join(lines)


def process_crawl_results(crawl_filepath: str) -> tuple[dict, dict, str]:
    """크롤링 결과를 종합 처리"""
    with open(crawl_filepath, "r", encoding="utf-8") as f:
        crawl_data = json.load(f)

    exam_info = extract_exam_info(crawl_data)
    patterns = analyze_patterns(exam_info)
    summary = generate_summary(exam_info, patterns)

    # 분석 결과 저장
    analysis_path = os.path.join(DATA_DIR, "analysis_latest.json")
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump({
            "exam_info": exam_info,
            "patterns": patterns,
        }, f, ensure_ascii=False, indent=2)

    # 요약 저장
    summary_path = os.path.join(DATA_DIR, "summary_latest.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)

    return exam_info, patterns, summary
