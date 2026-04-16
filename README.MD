# ubermensch — 서민금융진흥원 필기 복원·훈련·예측 프로젝트

> **사용자**: 윤종환 (서민금융진흥원 2026 상반기 종합직 일반 필기 응시 · 총점 58.09 / 커트라인 64.48 / 격차 -6.39)
> **목표**: 다음 회차 필기 시험장에서 **90% 인식률** (본 적 있는·훈련한 문제) 달성 + **숙련도 95%** 달성 → 합격.
> **원칙**: 팩트 없는 주장 절대 금지. 박사급+10년차 실무 이상만 기여. 에이전트 상호 의심·팩트체크 상시.

---

## 헌법 (C-0 ~ C-11) 요약 — `CLAUDE.md` 전문 참조

| 조항 | 요지 |
|---|---|
| ⭐ 북극성 | **시험 복원률 95%** 단 하나의 최종 목표 |
| C-0 | **스노우볼 연쇄 독트린**: 팩트 아니면 프로젝트 개박살. 데이터 하드 기준 4종 (출처 URL+원문 인용+게시일+독립 소스≥2) |
| C-1 | 모든 에이전트 실무 10년+ + 박사급 필수 |
| C-2 | 사용자 제시 답변은 박사 or 상위 1% 실무 입증 수준 |
| C-3 | 자연어 "조사해" → 박사급 다학제 팀 자동 편성 (7 페르소나) |
| C-4 | 중대사 결정은 경연(經筵) 거버넌스 |
| C-5 | 에이전트는 서로의 **생성 원리(reasoning mechanism)** 를 의심 |
| C-6 | 성과 메리토크라시 + Exit Interview + Best-Practice Share + 인기영합 절대 금지 |
| C-7 | 에이전트 진화 루프 (장점 계승, 단점 폐기, 신세대 생성) |
| C-8 | EPL 승강 대결 (매 라운드 최하위 5 퇴출 + 신규 5 진입, 15명 풀) |
| C-9 | 기록관 P10 — 모든 것이 기록됨 (GDrive 미연동, 로컬 운영 중) |
| C-10 | 태상위원 P11 — 최정점 메타 감찰자 · 주기적 재탄생 |
| C-11 | "한 번도 망하지 말자" 금지 · 현실 방해 상수 가정 · 작게 자주 망하라 |

---

## 에이전트 편제 (P1 ~ P11)

| ID | 역할 | 템플릿 |
|---|---|---|
| P1 | 공공기관 채용공고 분석 전문가 | `docs/agent_templates/P1_announcement_analyst.md` |
| P2 | 수의계약 채용대행업체 분석 | `P2_outsourcer_analyst.md` |
| P3 | NCS 10대 영역 출제 전문가 | (실 파견 시 작성) |
| P4 | 알라딘/교보 카탈로그 메타 수집 | `P4_aladin_catalog.md` |
| P5 | 공개 후기 스크리너 | (실 파견 시 작성) |
| P6 | 회의론자/교차 팩트체커 | (실 파견 시 작성) |
| P7 | 합성가 (synthesist) | (실 파견 시 작성) |
| P8 (SC1/SC2) | 수석위원 2중 심사 | `SC1_SC2_senior_chief.md` |
| P9 | 리버스 엔지니어링 (예상 문항) | `P9_reverse_engineering.md` |
| P10 | 기록관 (Archivist) | `P10_archivist.md` |
| P11 | 태상위원 (최정점 메타) | (실 재탄생 시 작성) |

---

## 자동 루틴 R1 ~ R12 진행 상태

| 단계 | 설명 | 상태 |
|---|---|---|
| R1 | audit 지적 코드 수정 (FABRICATION 제거) | ✅ `b8ef43e` |
| R2 | reconstruction-plan v3 재작성 | ✅ `1c6f22d` |
| R3 | 공식 공고 조사 | ⚠ 공개 웹 fetch 제약 (403) — 사용자 M1 대기 |
| R4 | 수의계약 채용대행업체 식별 | ⏸ M1 수령 후 |
| R5 | 알라딘 카탈로그 메타데이터 | ✅ 예비 교재 추천서 `20_book_purchase_recommendation.md` |
| R6 | 2차 소스 + 회의론 필터 | ⏸ M1 수령 후 |
| R_RE | 리버스 엔지니어링 P9 | ⏸ R3~R6 완료 후 |
| R7 | 사용자 구매 승인 대기 | ⏸ 교재 추천서 검토 후 |
| R8 | corpus 모듈 (models/storage/scoring/import/match/drill) | ✅ 6모듈 + CLI 통합 |
| R9 | 합성 (재탕 추정 블루프린트) | ⏸ R_RE 후 |
| R10 | drill 회독 시스템 + 숙련도 95% | ✅ 모듈 완성 / 회독 실행은 corpus 적재 후 |
| R11 | diagnose ↔ corpus 연계 | ⏸ corpus 적재 후 |

---

## 코드·모듈 개요

```
exam_analyzer/
├── __init__.py
├── __main__.py
├── cli.py               # argparse 전체 (analyze / diagnose / corpus …)
├── models.py            # Section · ExamRecord (점수 분석용)
├── analyzer.py          # 수학적 분석 (격차 분해 · 합격 시나리오)
├── storage.py           # ~/.exam_history.json 원자적 쓰기
├── i18n.py              # 한국어 UI 문자열
└── corpus/              # 기출 DB · 회독 시스템 (R8)
    ├── __init__.py
    ├── models.py        # Question · Choice · Attempt · ReviewRound · Provenance
    ├── storage.py       # ~/.exam_corpus.json (저작권 민감 — 저장소 커밋 금지)
    ├── scoring.py       # 숙련도 계산 (북극성 측정)
    ├── import_.py       # JSON / 간단 텍스트 반입 (provenance 필수 C-0)
    ├── match.py         # 2차 후기 ↔ 1차 corpus 키워드 매핑
    └── drill.py         # 회독 세션 (sequential / random / weakest_first)

tests/                   # 67 unittest 전부 통과
├── test_analyzer.py     # 39건 (analyze/diagnose + 수학 회귀 방지)
├── test_corpus.py       # 11건 (corpus models/storage)
└── test_corpus_import_match_drill.py  # 17건

docs/
├── PLAN.md              # exam_analyzer 원 설계 스냅샷
├── reconstruction-plan.md  # 루틴 R1~R12 (v3)
├── audit-v1.md          # R1 전 FABRICATION 전수조사
├── audit-v2.md          # 환경 제약(403) 확인 후 재감사
├── audit-v3.md          # 헌법 C-0~C-11 반영 후 정합성
├── gyeongyeon/          # 경연(중대사 결정) 기록
├── agent_templates/     # P1/P2/P4/P9/P10/SC1_SC2 프롬프트 템플릿
├── honors/              # 에이전트 호칭 기록
├── meta_overseer/       # P11 태상위원 rebirth diff
├── agent_performance.md # C-6 성과 지표 축적
└── exam_reconstruction/서민금융진흥원_2026_상반기_종합직_일반/
    ├── 00_meta.md
    ├── 10_snippets_low_confidence.md  # MID 신뢰 (격리)
    ├── 20_book_purchase_recommendation.md
    └── 99_required_materials.md       # 사용자 요청 자료 목록
```

---

## CLI 사용법 (Python 3.9+ stdlib-only)

### 점수 분석·진단

```bash
python -m exam_analyzer analyze \
  --agency "서민금융진흥원" --date 2026-04-15 \
  --section "직업기초능력평가:19.33:40:40" \
  --section "직무수행능력평가:38.76:60:60" \
  --cutoff 64.48 --save

python -m exam_analyzer diagnose --from-id <기록ID>
```

### 기출 corpus 관리 (R8)

```bash
# 숙련도 통계
python -m exam_analyzer corpus stats

# 문항 목록
python -m exam_analyzer corpus list --area NCS

# JSON 파일 반입 (provenance 필수)
python -m exam_analyzer corpus import --from-json ./my_book_excerpts.json --dry-run
python -m exam_analyzer corpus import --from-json ./my_book_excerpts.json

# 숙련도 리포트 (북극성 95% 측정)
python -m exam_analyzer corpus mastery --min-consecutive 3 --required-accuracy 0.9
```

### 환경변수

- `EXAM_HISTORY_FILE` · `EXAM_CORPUS_FILE` — 파일 경로 override
- `NO_COLOR` — ANSI 색상 비활성 ([no-color.org](https://no-color.org))

---

## 테스트

```bash
python -m unittest discover tests -v
# 67 tests, all pass
```

---

## 사용자 재개 가이드 (수면 후 또는 새 세션)

1. `CLAUDE.md` 상단 §0 순서대로 문서 읽기
2. `docs/audit-v3.md` 로 현재 상태 파악
3. `docs/reconstruction-plan.md` 에서 현 Phase 확인
4. Phase 0 블로커 해소 — **사용자 자료 M1/M2/M3** 제공:
   - M1: 2026 상반기 종합직(일반) **공고 PDF 본문** (스샷 or 복붙)
   - M2: 수험번호 `1056` 직렬 매핑
   - M3: 보유 알라딘 이북 목록 (제목/출판사/판본)
5. 자료 수령 즉시 R3 재개. Agent P1 파견 → 공식 팩트 확정 → R4/R5/R6/R_RE/R8(적재)/R10(회독) 순차.

## 데스크탑(로컬 PC)에서 이어가기

`docs/desktop_setup.md` — 클론/풀 → 테스트 → Claude Code 재개 가이드.
요약 3단계:
```bash
git clone https://github.com/ubermensch90623/ubermensch.git && cd ubermensch
git checkout claude/fix-handwriting-recognition-J9xJq
python -m unittest discover tests   # 67 전부 통과 확인
```
그 다음 Claude Code 앱/CLI 로 이 폴더 열고 `CLAUDE.md` 읽힘 확인 → 자료 공유 시작.

---

## 데이터 파일 위치

- `~/.exam_history.json` — 점수 이력 (분석용)
- `~/.exam_corpus.json` — 기출 corpus (저작권 민감, **저장소 커밋 금지**, `.gitignore` 에 패턴)

---

## 라이선스 / 저작권

- 본 코드: 개인 용도
- 기출 원본: 사용자 구매 이북 기반. 공개 저장소에 본문 커밋 금지.
- 2차 소스 인용: 짧은 인용 + 출처 URL 필수.

---

## 현실 방해 대비 (C-11)

이 프로젝트는 **"한 번도 망하지 말자" 환상 배격**. 현실은 방해한다. 관료 지연·공고 변경·가족사·건강·멘탈. 작게 자주 망하고, 기록 남기고 (C-9), 재개하라. 데이터 무결성만 타협하지 않는다 (C-0).
