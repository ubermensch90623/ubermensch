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
| `python main.py obsidian-export --vault PATH` | Obsidian vault에 마크다운 트리 생성 |
| `python main.py sync-vault --vault PATH` | study-evolve + lab 둘 다 한 vault에 통합 |
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

---

## Obsidian 통합

`records.csv`와 `review_schedule.csv`를 Obsidian vault의 마크다운 트리로 자동 변환한다. wiki-link, YAML frontmatter, dataview 호환.

### 사용법

```bash
# vault 경로 직접 지정
python main.py obsidian-export --vault ~/Documents/MyVault

# 또는 환경변수로
export OBSIDIAN_VAULT=~/Documents/MyVault
python main.py obsidian-export

# 정답까지 노트로 만들기 (기본은 오답만)
python main.py obsidian-export --vault ~/Documents/MyVault --include-correct
```

### 생성되는 vault 구조

```
{vault}/StudyEvolve/
├── index.md                              # 통계 + 영역/태그/일일 인덱스 (dataview 예시 포함)
├── records/<id>-<date>-<problem>.md      # 오답 1건 = 노트 1개 (frontmatter + 복습 일정 + wiki-link)
├── by-area/<과목>__<영역>.md              # 영역별 오답 누적 + 태그 카운트
├── by-failtag/<태그>.md                   # 실패 태그별 발생 기록
└── daily/<YYYY-MM-DD>.md                 # 일일 학습 노트 (정답률 + 풀이 기록 + 태그)
```

### 멱등성과 안전성

- **멱등**: 같은 데이터로 두 번 실행해도 SHA256 동일. 매일 cron으로 돌려도 vault git diff 노이즈 없음.
- **사용자 노트 보호**: vault의 다른 파일/폴더(`MyDailyJournal.md`, `OtherFolder/`)는 절대 건드리지 않음. `StudyEvolve/` 서브트리만 영향.
- **stale 파일 자동 정리**: 직전 export 후 records.csv에서 행이 삭제되면 다음 export에서 해당 노트도 사라짐.
- **한글 파일명**: `독점적 경쟁` → `경제학__독점적_경쟁.md` (공백 → `_`, 슬래시·콜론 등 OS 무효 문자 제거).

### 자동화 — `sync-vault` + `STUDY_EVOLVE_AUTO_SYNC` (권장)

`sync-vault`는 study-evolve와 personal_intelligence_lab을 **하나의 vault**로 통합:

```bash
python main.py sync-vault --vault ~/Documents/MyVault
# → vault/StudyEvolve/  (CSV → 마크다운)
# → vault/PersonalIntelligenceLab/ (lab 디렉터리 미러)
```

옵션:
- `--no-lab` — study-evolve만, lab은 건너뜀
- `--symlink` — lab을 미러 대신 심볼릭 링크 (POSIX, 양방향 작동)
- `--lab PATH` — lab 경로 명시 (기본은 자동 탐지 / `LAB_PATH` 환경변수)

**완전 자동 (매번 sync 명령 안 쳐도 됨)**:

```bash
# ~/.zshrc 또는 ~/.bashrc
export OBSIDIAN_VAULT=~/Documents/MyVault
export STUDY_EVOLVE_AUTO_SYNC=1
```

이제 `add` / `done-review` / `sample` 명령이 끝나는 즉시 vault가 자동 갱신된다. 사용자가 export 명령을 따로 칠 필요 없음. 실패해도 메인 명령 종료 코드는 영향 없음 (warning만 stderr에).

### 자동화 — cron (구식 / fallback)

매일 한 번:

```bash
# crontab -e
0 22 * * *  cd ~/study-evolve && python main.py sync-vault --vault ~/Documents/MyVault >/dev/null
```

### Obsidian에서 활용

- **Backlinks**: 자동 작동. `[[경제학__조세]]` 클릭 → 영역 노트로 이동, 역링크로 모든 오답 확인.
- **Dataview** (플러그인 설치 시): `index.md`에 예시 쿼리 포함. 난이도별/태그별 필터링 가능.
- **Tags**: 모든 노트가 `#study-evolve` + 유형 태그(`#wrong`, `#area-index` 등). Obsidian Tags pane에서 한눈에.

---

## 안전성 노트 (Redteam Hardening)

이 시스템은 매일 사용할 학습 데이터를 다루므로 다음 방어 장치가 들어가 있다.

| 위험 | 방어 |
| --- | --- |
| Excel/Sheets에서 메모의 `=SUM(...)`이 수식으로 실행됨 | `_sanitize_cell` — `= + - @ \t \r`로 시작하는 값에 `'` prefix 자동 부착 |
| 두 셸에서 동시 `add` → 같은 ID 생성 | POSIX `fcntl.flock` 기반 `_exclusive_lock` (Windows는 잠금 없는 fallback) |
| `mark_review_done` 도중 SIGTERM → schedule.csv 손상 | tempfile + `os.replace` 원자적 교체 |
| `sample` 재실행 → 데이터 누적 오염 | 기본 차단, 재실행은 `--force` 명시 필요 |
| `parse_solve_time(0)` / `parse_solve_time(99999)` | 1초~3600초 범위 강제 |
| `parse_date("2099-12-31")` | 오늘+1일까지만 허용 |
| `parse_date("2024-1-1")` 형식 변형 | 정규식으로 `YYYY-MM-DD` (zero-padded) 강제 |
| `1m70s` 등 60초 이상 초 단위 | 초 칸은 0~59만 허용 |
| `done-review` 입력 `1,1,2` 중복 | `dict.fromkeys`로 순서 보존 dedupe |
| Ctrl+C 도중 부분 쓰기 | append 1행 단위 + 원자적 mark_review_done. main에서 KeyboardInterrupt → exit 130 |

### 테스트 실행

```bash
python -m unittest discover tests -v
```

전체 57 테스트 (CSV 주입, 파싱 경계, 동시성 50개 워커, 원자성, 멱등성, 추천 엣지, 풀 사이클, Obsidian 트리·frontmatter·한글 파일명·stale 정리, vault sync 미러·심볼릭·auto-trigger·사용자 노트 보호).
