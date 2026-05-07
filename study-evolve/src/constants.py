"""Domain constants — subjects, areas, fail tags, review intervals, CSV schemas."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RECORDS_CSV = DATA_DIR / "records.csv"
SCHEDULE_CSV = DATA_DIR / "review_schedule.csv"

SUBJECTS = ["NCS", "경제학", "경영학", "기타"]

AREAS_BY_SUBJECT = {
    "NCS": [
        "자료해석", "의사소통", "수리", "문제해결", "자원관리", "정보능력",
    ],
    "경제학": [
        "미시경제", "거시경제", "조세", "시장구조", "독점", "독점적 경쟁",
        "게임이론", "국민소득", "IS-LM", "AD-AS", "국제경제",
    ],
    "경영학": [
        "조직행동", "인사관리", "마케팅", "재무관리", "생산관리", "전략경영",
    ],
    "기타": [],
}

FAIL_TAGS = [
    "개념 미흡",
    "조건 누락",
    "계산 지연",
    "계산 실수",
    "선지 판단 오류",
    "시간 초과",
    "그래프 해석 오류",
    "표 해석 오류",
    "공식 혼동",
    "문제 접근 실패",
    "너무 오래 붙잡음",
    "찍기 실패",
    "멘탈 흔들림",
    "쉬운 문제 과소평가",
    "복습 부족",
    "기타",
]

REVIEW_INTERVALS = [1, 3, 7]
REVIEW_TYPES = ["1d", "3d", "7d"]

RECORDS_HEADER = [
    "id", "date", "subject", "area", "source", "problem_no",
    "is_correct", "solve_time_sec", "difficulty", "fail_tag", "memo",
    "review_1d", "review_3d", "review_7d", "created_at",
]

SCHEDULE_HEADER = [
    "record_id", "review_date", "review_type", "is_done", "done_at",
]

ACTION_RULES = {
    "조건 누락": "문제를 읽은 뒤 조건 2개를 먼저 적고 계산을 시작한다.",
    "계산 지연": "계산을 시작하기 전, 어림산/비율/차이 비교 중 하나를 먼저 선택한다.",
    "계산 실수": "마지막 답을 적기 전에 단위·부호 검산 한 줄을 강제한다.",
    "공식 혼동": "문제 풀이 전 관련 공식 1개를 빈 종이에 쓰고 시작한다.",
    "시간 초과": "90초가 지나도 풀이 방향이 안 보이면 표시하고 넘어간다.",
    "선지 판단 오류": "선지를 보기 전 내가 구해야 할 값을 한 줄로 정의한다.",
    "개념 미흡": "오답 직후 해당 개념을 1장 카드로 정리하고 다음 슬롯 시작에 1번 읽는다.",
    "멘탈 흔들림": "처음 3문제는 쉬운 문제로 워밍업하고 타이머를 켠다.",
}
DEFAULT_ACTION = "문제 풀이 후 실패 태그를 반드시 1개만 선택한다."
