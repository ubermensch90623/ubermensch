# 필기전형 점수 분석 도구 — 설계 플랜 (스냅샷)

> 이 문서는 `/root/.claude/plans/valiant-toasting-raven.md` 에 작성된 플랜의
> 저장소 내부 스냅샷입니다. 로컬 PC 에서 Claude Code 새 세션으로 이어서 작업할 때
> 컨텍스트를 빠르게 복구하기 위한 용도입니다.

## Context (배경)

서민금융진흥원 필기전형에서 아쉽게 탈락 (총점 58.09 / 커트라인 64.48, 격차 -6.39).
이 경험을 계기로 공공기관 필기전형 점수를 체계적으로 관리·분석할 수 있는
**개인용 Python CLI 도구**를 만든다. 다음 시험을 준비할 때 부족한 영역을 수치로
파악하고, 여러 시험 결과를 누적 관리하여 합격 가능성을 높이는 것이 목표.

## 확정 요구사항

1. 점수 입력 및 합격 여부 판정
2. 커트라인과의 격차 분석
3. 복수 시험 이력 관리 (JSON 저장)
4. 가중치 기반 환산 (백분율/100점 만점 변환)

## 현재 구현 상태 (MVP 완료)

이 스냅샷 작성 시점 기준:

| 파일 | 상태 |
|---|---|
| `exam_analyzer/models.py` | ✓ Section / ExamRecord dataclass + to/from_dict |
| `exam_analyzer/analyzer.py` | ✓ compute_total / compute_gap / judge_pass / normalize_weights / convert_to_scale / analyze |
| `exam_analyzer/storage.py` | ✓ 원자적 쓰기 JSON 저장소 + ID 접두사 검색 |
| `exam_analyzer/cli.py` | ✓ analyze / save / list / show / delete / convert / stats 서브커맨드 |
| `exam_analyzer/i18n.py` | ✓ 한국어 UI 문자열 |
| `exam_analyzer/__main__.py` | ✓ `python -m exam_analyzer` 진입점 |
| `tests/test_analyzer.py` | ✓ 27개 unittest (서민금융진흥원 골든 픽스처 포함) |
| `README.MD` | ✓ 한국어 사용법 |
| `.gitignore` | ✓ |

## 골든 픽스처 (절대 회귀시키지 말 것)

서민금융진흥원 2026-04 필기:
- 직업기초능력평가 19.33 / 40, weight 40
- 직무수행능력평가 38.76 / 60, weight 60
- cutoff 64.48
- 기대 총점: **58.09**, 격차: **-6.39**, 판정: **불합격**, 취약 영역: **직업기초능력평가 (48.32%)**

CLI 확인:
```bash
python -m exam_analyzer --no-color analyze \
  --agency "서민금융진흥원" --date 2026-04-15 \
  --section "직업기초능력평가:19.33:40:40" \
  --section "직무수행능력평가:38.76:60:60" \
  --cutoff 64.48
# 종료 코드 1 (EXIT_FAIL)
```

## 로컬 PC 에서 작업 재개 절차

### A. 환경 준비

1. **Python 3.9+** 설치 확인 (`python --version` 또는 Windows `py -3 --version`).
2. 저장소 클론/풀:
   ```bash
   git clone https://github.com/ubermensch90623/ubermensch.git
   cd ubermensch
   git fetch origin claude/fix-handwriting-recognition-J9xJq
   git checkout claude/fix-handwriting-recognition-J9xJq
   git pull origin claude/fix-handwriting-recognition-J9xJq
   ```
3. 외부 의존성 없음 — `pip install` 불필요.

### B. 동작 점검

```bash
python -m unittest discover tests -v
python -m exam_analyzer --help
```

### C. Claude Code 세션 컨텍스트 복구

로컬에서 새 Claude 세션 시작 시 다음 자료를 참조하게 하면 된다:

- 이 문서 (`docs/PLAN.md`)
- `README.MD`
- `tests/test_analyzer.py` (기대 동작을 스펙 문서처럼 읽을 수 있음)

### D. 크로스플랫폼 유의사항 (이미 코드에 반영됨)

- 경로는 `pathlib.Path`, 홈 디렉터리는 `Path.home()` 로 처리.
- JSON 은 `encoding="utf-8"` + `ensure_ascii=False` 로 한글 보존.
- 원자적 쓰기: 임시파일 + `os.replace` (Windows 포함 동작).
- ANSI 색상: `sys.stdout.isatty()` + `NO_COLOR` + Windows 판정 로직으로 자동 관리.
- Windows 콘솔에서 한글 깨지면 `chcp 65001` 안내 (README 기재).

## 향후 확장 후보 (MVP 이후, 로컬에서 추가 여지)

- 기관별 커트라인/일정 사전 등록 (`~/.exam_agencies.json`)
- 목표 점수 역산 (회귀 분석)
- CSV 내보내기 (`--export csv`)
- `rich` / `textual` 기반 TUI (외부 의존성 도입 필요)
- matplotlib 영역별 성장 추이 그래프
- SessionStart 훅으로 웹/로컬 간 환경 정합성 자동 점검

## 주요 트레이드오프 (기록용)

- **패키지 분리 vs 단일 파일**: 책임별 5 모듈. 약 600 LOC 미만.
- **데이터 파일**: `~/.exam_history.json` 기본, `--data-file` / `EXAM_HISTORY_FILE` override.
- **record ID**: sha1(agency|date|total)[:8] — 안정적 식별자.
- **가중치 의미**: "100점 만점에 대한 절대 기여도" (공공기관 관례).
- **Python floor**: 3.9 (`typing.Optional` / `typing.List` 사용).
- **색상**: ANSI raw (외부 라이브러리 없음).
