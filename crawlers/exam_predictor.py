"""
예상문제 생성기
- 크롤링된 자료 + 기존 문제 분석
- 기관별 출제 패턴에 맞춘 예상문제 생성
- Claude API 또는 Claude Code에서 직접 사용
"""

import json
import os
from datetime import datetime

QUESTIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "study", "questions")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_existing_questions() -> dict:
    """기존 문제 전체 로드"""
    questions = {}
    for filename in os.listdir(QUESTIONS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(QUESTIONS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                subject = data.get("subject", filename)
                questions[subject] = data.get("questions", [])
    return questions


def load_crawl_analysis() -> dict | None:
    """최신 크롤링 분석 결과 로드"""
    analysis_path = os.path.join(DATA_DIR, "analysis_latest.json")
    if not os.path.exists(analysis_path):
        return None
    with open(analysis_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prediction_prompt(institution: str, subject: str, count: int = 5) -> str:
    """
    예상문제 생성용 프롬프트 빌드
    - Claude Code에서 이 프롬프트를 사용해서 문제 생성
    - 또는 Claude API로 전송
    """
    existing = load_existing_questions()
    analysis = load_crawl_analysis()

    prompt_parts = []
    prompt_parts.append(f"""당신은 한국 공기업 NCS 시험 전문가입니다.
다음 정보를 바탕으로 '{institution}' 시험에 출제될 가능성이 높은 '{subject}' 과목 예상문제 {count}개를 만들어주세요.

## 요구사항
1. 실제 시험과 동일한 형식 (4지선다)
2. 난이도 분포: 하(1개), 중(3개), 상(1개)
3. 기존 문제와 겹치지 않는 새로운 문제
4. 해설은 쉬운 말로, 비전공자도 이해할 수 있게
5. JSON 형식으로 출력

## 출력 형식
```json
[
  {{
    "id": "{subject[:3]}-pred-001",
    "difficulty": "중",
    "type": "유형명",
    "question": "문제 내용",
    "choices": ["① 선택지1", "② 선택지2", "③ 선택지3", "④ 선택지4"],
    "answer": 정답번호,
    "explanation": "해설",
    "prediction_reason": "이 문제를 예상한 이유"
  }}
]
```
""")

    # 기존 문제 참조
    if subject in existing:
        existing_qs = existing[subject][:5]
        prompt_parts.append(f"\n## 기존 문제 샘플 (이와 겹치지 않게)\n")
        for q in existing_qs:
            prompt_parts.append(f"- [{q.get('difficulty', '')}] {q.get('question', '')}")

    # 크롤링 분석 결과 참조
    if analysis:
        patterns = analysis.get("patterns", {})
        freq = patterns.get("subject_frequency", {})
        prompt_parts.append(f"\n## 출제 빈도 분석\n")
        for subj, count in sorted(freq.items(), key=lambda x: x[1], reverse=True):
            prompt_parts.append(f"- {subj}: {count}회")

        # 수집된 자료에서 관련 내용 추출
        exam_info = analysis.get("exam_info", {})
        reviews = exam_info.get("exam_reviews", [])
        if reviews:
            prompt_parts.append(f"\n## 시험 후기에서 수집된 정보\n")
            for review in reviews[:3]:
                preview = review.get("content_preview", "")[:500]
                prompt_parts.append(f"- {review.get('source', '')}: {preview}")

    # 기관별 특성
    from crawlers.sources import TARGET_INSTITUTIONS
    inst_info = TARGET_INSTITUTIONS.get(institution, {})
    if inst_info:
        prompt_parts.append(f"\n## 기관 정보\n")
        prompt_parts.append(f"- 기관명: {inst_info.get('name', '')}")
        prompt_parts.append(f"- 시험 유형: {inst_info.get('exam_type', '')}")
        prompt_parts.append(f"- 시험 과목: {', '.join(inst_info.get('subjects', []))}")

    return "\n".join(prompt_parts)


def save_predicted_questions(questions: list, institution: str, subject: str) -> str:
    """예상문제를 파일로 저장"""
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"predicted_{institution}_{subject}_{timestamp}.json"
    filepath = os.path.join(DATA_DIR, filename)

    data = {
        "institution": institution,
        "subject": subject,
        "generated_at": datetime.now().isoformat(),
        "questions": questions,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def get_prediction_status() -> dict:
    """현재 예상문제 생성 현황"""
    status = {
        "existing_questions": {},
        "predicted_questions": {},
        "crawl_data_available": False,
    }

    # 기존 문제 수
    existing = load_existing_questions()
    for subject, qs in existing.items():
        status["existing_questions"][subject] = len(qs)

    # 예상문제 수
    for filename in os.listdir(DATA_DIR):
        if filename.startswith("predicted_") and filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                key = f"{data.get('institution', '')}_{data.get('subject', '')}"
                status["predicted_questions"][key] = len(data.get("questions", []))

    # 크롤링 데이터 유무
    analysis_path = os.path.join(DATA_DIR, "analysis_latest.json")
    status["crawl_data_available"] = os.path.exists(analysis_path)

    return status
