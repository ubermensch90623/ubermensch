# Study Evolve

## 목적

이 시스템은 NCS + 경제학 시험 준비를 위한 개인 학습 진화 시스템입니다.
오답을 감정적 실패가 아니라 반복 가능한 버그 데이터로 기록하고, 다음 학습 방향을 추천합니다.

핵심 동작:

1. 푼 문제 데이터를 CSV에 저장한다.
2. 틀린 문제를 16종 실패 태그로 분류한다.
3. 반복되는 실패 패턴(3회 이상)을 자동 탐지한다.
4. 점수가 가장 빨리 오를 다음 학습을 추천한다.
5. 틀린 문제를 1일 / 3일 / 7일 뒤에 복습 대상으로 자동 등록한다.
6. 매일 저녁 5분 안에 학습 리뷰를 끝낼 수 있게 한다.

CLI 기반 Python 프로그램. 웹앱 / 로그인 / DB 없음. 점수 상승 엔진에 집중.

---

## 설치

```bash
pip install -r requirements.txt
```

Python 3.10 이상.

---

## 첫 실행 (5분)

```bash
python main.py init
python main.py sample        # 샘플 17건 자동 생성 (선택)
python main.py stats
python main.py recommend
```

`sample`을 실행하면 다음 패턴이 들어간 데이터가 생성됩니다.

- 경제학 조세 영역 — 공식 혼동 3회 이상
- NCS 자료해석 — 조건 누락 3회 이상
- NCS 의사소통 — 정답률 높음 (성공 경험용)
- 풀이 시간이 평균보다 긴 영역 포함
- 1일 / 3일 / 7일 복습 대상 자동 포함

---

## 명령어

| 명령 | 설명 |
| --- | --- |
| `python main.py init` | data 폴더와 CSV 파일을 생성. 이미 있으면 덮어쓰지 않음 |
| `python main.py add` | 인터랙티브 입력으로 학습 기록 추가 |
| `python main.py stats` | 전체 기간 통계 |
| `python main.py stats --days 7` | 최근 7일 통계 |
| `python main.py stats --days 30` | 최근 30일 통계 |
| `python main.py recommend` | 내일 학습 추천 + 행동 1개 |
| `python main.py review` | 오늘의 학습 리포트 |
| `python main.py due` | 오늘 복습할 문제 목록 |
| `python main.py done-review` | 복습 완료 처리 (번호 또는 `all`) |
| `python main.py export` | CSV 파일 경로 안내 |
| `python main.py sample` | 샘플 데이터 생성 |

---

## 하루 사용 루틴 (5분)

### 아침
```bash
python main.py recommend
```
→ 오늘 풀 영역 + 복습 대상 + 행동 1개 확인.

### 공부 직후 (문제마다)
```bash
python main.py add
```
→ 정답이면 결과만, 오답이면 실패 태그까지 기록.

### 저녁 (마무리)
```bash
python main.py review
```
→ 오늘 정답률·핵심 버그·내일 행동 확인.

### 복습 시간
```bash
python main.py due           # 복습 대상 확인
python main.py done-review   # 끝낸 항목 완료 처리
```

### 일요일
```bash
python main.py stats --days 7
```
→ 한 주 패턴 회고. 위험 신호(3회 이상 반복 태그) 확인.

---

## 데이터 구조

### `data/records.csv`

| 컬럼 | 설명 |
| --- | --- |
| id | 자동 증가 정수 |
| date | 문제 푼 날짜 (YYYY-MM-DD) |
| subject | NCS / 경제학 / 경영학 / 기타 |
| area | 과목별 세부 영역 |
| source | 출처 (예: 민경채 PSAT, 봉투모의고사, 전공기출) |
| problem_no | 문제 번호 (문자열 허용) |
| is_correct | 정답 여부 (True/False) |
| solve_time_sec | 풀이 시간 (초 단위 저장) |
| difficulty | 체감 난이도 1~5 |
| fail_tag | 오답 태그 (정답이면 빈칸) |
| memo | 짧은 메모 |
| review_1d / 3d / 7d | 복습 예정일 (정답이면 빈칸) |
| created_at | 기록 생성 시각 |

### `data/review_schedule.csv`

| 컬럼 | 설명 |
| --- | --- |
| record_id | records.csv의 id |
| review_date | 복습 예정일 |
| review_type | `1d` / `3d` / `7d` |
| is_done | 완료 여부 |
| done_at | 완료 시각 |

---

## 실패 태그 16종

`add` 명령에서 오답이면 번호로 선택:

```
 1) 개념 미흡          9) 공식 혼동
 2) 조건 누락         10) 문제 접근 실패
 3) 계산 지연         11) 너무 오래 붙잡음
 4) 계산 실수         12) 찍기 실패
 5) 선지 판단 오류    13) 멘탈 흔들림
 6) 시간 초과         14) 쉬운 문제 과소평가
 7) 그래프 해석 오류  15) 복습 부족
 8) 표 해석 오류      16) 기타 (직접 입력)
```

---

## 추천 알고리즘 (recommender.py)

`generate_recommendations(records_df, schedule_df)`

1. 최근 30일만 필터링
2. 영역별 통계 계산 (total / wrong / accuracy / avg_solve)
3. 실패 태그 빈도 계산
4. 약점 영역 선정:
   - `wrong >= 2` 그리고 `accuracy <= 0.7`
   - 또는 `avg_solve >= 전체 평균 × 1.2`
   - 또는 같은 영역에서 fail_tag 3회 이상 반복
5. 복습 대상: `review_date <= today` 그리고 `is_done == False`
6. 성공 경험 영역: `accuracy >= 0.75` 그리고 `total >= 3`
7. 내일 행동 1개: 가장 빈번한 fail_tag → `constants.ACTION_RULES` 매핑

### 행동 규칙 (`constants.ACTION_RULES`)

| 가장 많은 fail_tag | 내일 행동 |
| --- | --- |
| 조건 누락 | 문제를 읽은 뒤 조건 2개를 먼저 적고 계산을 시작한다. |
| 계산 지연 | 계산 시작 전 어림산/비율/차이 비교 중 하나를 먼저 선택한다. |
| 공식 혼동 | 문제 풀이 전 관련 공식 1개를 빈 종이에 쓰고 시작한다. |
| 시간 초과 | 90초 지나도 풀이 방향이 안 보이면 표시하고 넘어간다. |
| 선지 판단 오류 | 선지를 보기 전 내가 구해야 할 값을 한 줄로 정의한다. |
| 멘탈 흔들림 | 처음 3문제는 쉬운 문제로 워밍업하고 타이머를 켠다. |
| (기본) | 문제 풀이 후 실패 태그를 반드시 1개만 선택한다. |

---

## 분석 알고리즘 (analyzer.py)

- `load_recent_records(df, days=None)`
- `calculate_overall_stats(df)`
- `calculate_subject_stats(df)`
- `calculate_area_stats(df)`
- `calculate_fail_tag_stats(df)`
- `detect_risk_signals(df, threshold=3)` — fail_tag 단독 + (subject, area, fail_tag) 조합

---

## 풀이 시간 입력 형식

`add` 명령에서 다음 형식 모두 허용:
- `90` → 90초
- `1:30` → 90초
- `2m` → 120초
- `1m30s` → 90초
- `45s` → 45초

내부 저장은 항상 초(int) 단위.

---

## 폴더 구조

```
study-evolve/
├── main.py
├── README.md
├── requirements.txt
├── data/
│   ├── records.csv          # init 시 자동 생성
│   └── review_schedule.csv  # init 시 자동 생성
└── src/
    ├── __init__.py
    ├── constants.py         # 과목/영역/실패 태그/행동 규칙
    ├── models.py            # StudyRecord dataclass
    ├── storage.py           # CSV I/O + 샘플 시더
    ├── analyzer.py          # 통계/위험 신호
    ├── recommender.py       # 추천 알고리즘
    ├── review.py            # 일일 리포트
    ├── cli.py               # 인터랙티브 흐름
    └── utils.py             # 입력 검증/시간 파싱/표 출력
```

---

## 주의

- 빈 데이터일 때 안내 문구를 출력하고 종료. 에러 X.
- 잘못된 입력은 다시 받음 (y/n, 1~5, 날짜, 풀이 시간 모두).
- 정답이면 fail_tag·review_*는 자동으로 빈칸.
- 같은 날 같은 문제를 두 번 추가해도 막지 않음 (각각 별 id로 저장).
- CSV 직접 편집 가능 — 단, 헤더는 유지할 것.
