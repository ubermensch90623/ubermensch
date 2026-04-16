"""한국어 UI 문자열 (추후 다국어 확장 여지)."""

STRINGS = {
    "pass": "합격",
    "fail": "불합격",
    "pending": "판정불가",
    "cutoff": "커트라인",
    "total": "총점",
    "gap": "격차",
    "verdict": "판정",
    "section": "영역",
    "score": "점수",
    "max": "만점",
    "weight": "가중치",
    "percentage": "백분율",
    "weighted": "환산점수",
    "strongest": "강점 영역",
    "weakest": "취약 영역",
    "agency": "기관",
    "date": "일자",
    "exam_name": "시험",
    "notes": "메모",
    "no_cutoff": "커트라인 미지정",
    "recommend_focus": "집중 보완 권장",
    "record_id": "기록 ID",
    "weight_rescaled": "가중치 합이 100이 아니어서 자동 재조정되었습니다",
    "saved": "저장되었습니다",
    "deleted": "삭제되었습니다",
    "not_found": "기록을 찾을 수 없습니다",
    "empty_history": "저장된 기록이 없습니다",
    "analysis_header": "분석 결과",
    "pass_rate": "합격률",
    "avg_gap": "평균 격차",
    "total_records": "기록 수",
}


def t(key: str) -> str:
    """i18n 문자열 조회."""
    return STRINGS.get(key, key)
