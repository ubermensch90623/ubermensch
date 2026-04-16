# exam_analyzer

공공기관 필기전형 점수를 입력/분석/누적 관리하는 Python CLI 도구.

- **의존성 없음** (Python 3.9+ 표준 라이브러리만 사용)
- 합격 여부 판정 · 커트라인 격차 분석
- 복수 시험 이력을 JSON 으로 저장 (기본: `~/.exam_history.json`)
- 영역별 가중치 환산 (100점 만점 스케일)
- 전 영역 한국어 UI · UTF-8 보존

## 빠른 시작

```bash
git clone https://github.com/ubermensch90623/ubermensch.git
cd ubermensch

# 도움말
python -m exam_analyzer --help
python -m exam_analyzer analyze --help
```

## 서민금융진흥원 예시 (Unix 쉘)

```bash
python -m exam_analyzer analyze \
  --agency "서민금융진흥원" --date 2026-04-15 \
  --section "직업기초능력평가:19.33:40:40" \
  --section "직무수행능력평가:38.76:60:60" \
  --cutoff 64.48 --save
```

### Windows PowerShell/CMD

```powershell
python -m exam_analyzer analyze ^
  --agency "서민금융진흥원" --date 2026-04-15 ^
  --section "직업기초능력평가:19.33:40:40" ^
  --section "직무수행능력평가:38.76:60:60" ^
  --cutoff 64.48 --save
```

Windows 콘솔에서 한글이 깨진다면 먼저 `chcp 65001` 실행.

### 출력 예시

```
[서민금융진흥원] 필기전형 분석 결과 (2026-04-15)
────────────────────────────────────────────────────────────
  직업기초능력평가            19.33 / 40     (48.32%)  → 환산 19.33점
  직무수행능력평가            38.76 / 60     (64.60%)  → 환산 38.76점
────────────────────────────────────────────────────────────
  총점:     58.09 / 100
  커트라인:  64.48
  격차:     -6.39점
  판정:    불합격

  취약 영역: 직업기초능력평가 (48.32%) — 집중 보완 권장
  기록 ID: f344b92e
```

종료 코드: `0` = 합격, `1` = 불합격, `2` = 사용법 오류, `3` = IO 오류.

## 서브커맨드

| 명령 | 용도 |
|---|---|
| `analyze` | 점수 입력 → 분석 출력, 선택적 `--save` |
| `save` | 분석 출력 없이 저장만 (`--from-json` 도 가능) |
| `list` | 이력 표 (`--sort date\|gap\|total`, `--passed-only`, `--failed-only`, `--agency`) |
| `show <id>` | 기록 상세 (ID 접두사 가능) |
| `delete <id>` | 기록 삭제 |
| `convert --score --max --to` | 점수 환산 유틸 |
| `stats [--agency]` | 누적 통계 (합격률 · 평균 격차 · 영역별 평균) |
| `diagnose` | 정밀 원인 분석 (격차 기여도 분해 · 합격 시나리오 · 추천 전략 · 체크리스트) |

### 전역 플래그

- `--data-file PATH` — 이력 JSON 경로 지정 (기본: `~/.exam_history.json`)
- `--no-color` — ANSI 색상 비활성
- `--json` — 머신 판독 가능 JSON 출력

### 환경변수

- `EXAM_HISTORY_FILE` — 기본 이력 경로 override (`--data-file` 보다 우선순위 낮음)
- `NO_COLOR` — 색상 비활성 ([no-color.org](https://no-color.org) 표준)

## 섹션 입력 포맷

```
NAME:SCORE:MAX:WEIGHT
```

- `WEIGHT` 는 100점 만점 기준 절대 기여도 (예: 40점 + 60점 = 100점)
- 가중치 합이 100이 아니면 자동 비례 재조정 + 경고 표시

## 대화형 모드

```bash
python -m exam_analyzer analyze --agency "한국OO공사" --date 2026-05-01 --cutoff 70 -i
```

## 정밀 원인 분석 (`diagnose`)

단순한 합격/불합격 판정을 넘어, 왜 그 결과가 나왔는지 수학적으로 분해해주는 기능.

```bash
python -m exam_analyzer diagnose \
  --agency "서민금융진흥원" --date 2026-04-15 \
  --section "직업기초능력평가:19.33:40:40" \
  --section "직무수행능력평가:38.76:60:60" \
  --cutoff 64.48
```

또는 이미 저장된 기록에서:

```bash
python -m exam_analyzer diagnose --from-id f344b92e
```

### 분석 항목

1. **결과 요약** — 총점 / 커트라인 / 격차
2. **영역별 격차 기여도 분해**
   - 커트라인을 가중치 비율로 안분 → 각 영역의 "기대 환산점수" 계산
   - `기여 = 실제 환산점수 - 기대 환산점수`
   - 기여의 합 = 격차 (수학적 항등성)
3. **합격 시나리오 3종**
   - A. 한 영역만 개선했을 때 필요한 원점수
   - B. 다른 영역만 개선했을 때 필요한 원점수
   - C. 모든 영역을 균등하게 백분율 상승시켰을 때의 목표
   - 각 시나리오에 현실성 평가 (높음/보통/낮음)
4. **추천 전략** — 약점 영역 집중 (학습 효과 가장 큰 구간)
5. **다음 시험 준비 체크리스트** — 영역별 목표 원점수/백분율 포함

JSON 출력도 지원 (`--json`).

## 테스트

```bash
python -m unittest discover tests -v
```

27개 테스트 중 핵심은 서민금융진흥원 실제 점수를 골든 픽스처로 잡고 있어
총점 58.09, 격차 -6.39, 불합격 판정이 회귀 없이 유지됩니다.

## 데이터 파일 구조

`~/.exam_history.json`:

```json
{
  "version": 1,
  "records": [
    {
      "record_id": "f344b92e",
      "agency": "서민금융진흥원",
      "exam_name": "필기전형",
      "date": "2026-04-15",
      "sections": [
        {"name": "직업기초능력평가", "score": 19.33, "max_score": 40, "weight": 40},
        {"name": "직무수행능력평가", "score": 38.76, "max_score": 60, "weight": 60}
      ],
      "cutoff": 64.48,
      "notes": ""
    }
  ]
}
```

쓰기는 `파일.tmp` 작성 후 `os.replace` 로 원자적 교체 → 인터럽트 시 손상 방지.

## 프로젝트 구조

```
exam_analyzer/
├── __init__.py     # 버전 상수
├── __main__.py     # python -m 진입점
├── models.py       # Section / ExamRecord dataclass + (de)serialization
├── analyzer.py     # 순수 계산 함수 (합격 판정, 격차, 가중치 환산)
├── storage.py      # JSON 이력 저장소 (원자적 쓰기)
├── cli.py          # argparse 서브커맨드 디스패치
└── i18n.py         # 한국어 UI 문자열
tests/
└── test_analyzer.py
docs/
└── PLAN.md         # 설계 플랜 스냅샷 (로컬 PC 재개용)
```

## 로컬 PC 로 작업 이어가기

- 웹 세션에서 `claude/fix-handwriting-recognition-J9xJq` 브랜치로 푸시해두면
  로컬에서 `git pull` 후 바로 실행 가능합니다.
- 추가 고려사항은 `docs/PLAN.md` 의 "로컬 PC에서 작업 재개 시나리오" 섹션 참조.

## 라이선스

Personal use.
