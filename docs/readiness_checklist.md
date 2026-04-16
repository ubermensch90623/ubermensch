# 실행 준비 체크리스트 — 사용자 자료 수령 즉시 순차 가동

> 사용자 (윤종환) 가 자료를 채팅에 제공하면 이 순서대로 자동 진행.
> 각 단계에 **예상 소요 시간** 과 **수석위원 SC1/SC2 심사 경유** 표시.
> 실패 시 C-11 원칙에 따라 작게 자주 복구.

---

## 🎯 Step 0 — 자료 수령 & 즉시 분류 (≤ 5분)

**사용자가 공유할 자료 (M1/M2/M3 중 일부라도 OK):**

| 코드 | 자료 | 처리 대상 에이전트 |
|---|---|---|
| M1 | 2026 상반기 종합직(일반) **공고 PDF 본문** (스샷 OCR or 복붙 텍스트) | P1 공고분석 |
| M2 | **수험번호 1056** 직렬 매핑 (공고 별첨) | P1 + P2 (대행사) |
| M3 | 보유 **알라딘 이북 목록** (제목/출판사/판본) | P4 카탈로그 |
| (옵션) | M4 이북 일부 발췌 샘플 | corpus import → 샘플 적재 |

**분류 액션**:
1. 메인 세션 Claude 가 자료 유형 판별 (텍스트 vs 이미지 OCR 필요)
2. 해당 자료를 적절한 `docs/exam_reconstruction/.../<파일>.md` 로 저장 (C-9 기록관 경유)
3. 개인정보 (전체 수험번호·주민번호) 는 마스킹 처리

---

## 🚀 Step 1 — R3 Agent P1 투입 (5~10분)

**선행 조건**: M1 최소 일부 (공고 원문 1페이지 이상) 확보.

**실행**:
```
프롬프트: docs/agent_templates/P1_announcement_analyst.md 참조
입력: M1 원문 + M2 직렬코드 (있는 경우)
목표 출력: 10_official_facts.md (확정 팩트)
```

**검증**: SC1 (사실 검증) + SC2 (방법론 심사) 통과 필수.
- 둘 다 PASS → 10_snippets_low_confidence.md 의 MID 항목 재분류 (확정/반박/유지)
- GATED → 사용자 추가 자료 요청

**기대 효과**: NCS 3영역 / 전공 트랙 / 문항수·시간·배점 **HIGH 신뢰도 확정**.

---

## 🏢 Step 2 — R4 Agent P2 투입 (5~10분)

**선행 조건**: Step 1 완료 + 공고에 "채용대행" 명시 여부 확인.

**실행**:
```
프롬프트: docs/agent_templates/P2_outsourcer_analyst.md 참조
입력: M1 원문 + 나라장터 (g2b.go.kr) 공개 조회 + 6대 출제사 사이트
목표 출력: 15_outsourcer_analysis.md
```

**검증**: SC1/SC2. 업체 미식별 시 UNKNOWN 처리 (추측 금지 C-0).

**기대 효과**: 휴노/행과연/ORP/... 중 **어떤 업체가 KINFA 와 계약했는지** 확정 or UNKNOWN.

---

## 📚 Step 3 — R5 Agent P4 + 사용자 교재 승인 (10분)

**선행 조건**: Step 1 완료 → 직무 트랙(경영/경제/법) 확정.

**실행**:
1. P4 가 **확정 트랙 기준** 알라딘·교보 메타데이터 재조사 → `20_book_purchase_recommendation_final.md`
2. `20_book_purchase_recommendation.md` (예비, `c44d415`) 와 비교 → 업데이트
3. **경연(C-4) 소집**: 사용자에게 AskUserQuestion 으로 Tier S/A 구매 승인 요청

**기대 효과**: 사용자 교재 구매 리스트 확정 → 구매 주문.

---

## 🔍 Step 4 — R6 Agents P5 + P6 병렬 투입 (15~30분)

**선행 조건**: Step 1~3 완료.

**실행**:
```
P5 (후기 수집): 공준모/티스토리/네이버블로그/오르비/링커리어 등 공개 후기 검색
P6 (회의론): P5 산출물 전수 공격 → 살아남은 claim 추출
```

**파이프라인**:
```
P5 collect → P6 attack → claims_surviving → match.build_match_report
```

**검증**: SC1/SC2.

**기대 효과**: MID 신뢰도 2차 주장 → 🟢/🟡/🔴 분류 → match 모듈로 corpus 연결.

---

## 📖 Step 5 — 1차 Corpus 적재 (사용자 참여, 시간 가변)

**선행 조건**: Step 3 교재 구매 + 이북 일부 발췌 공유.

**실행**:
1. 사용자가 이북에서 문항 발췌 (JSON 또는 간단 텍스트 포맷 — `corpus.import_` 스펙 참조)
2. `python -m exam_analyzer corpus import --from-json ./user_ebook.json --dry-run` 먼저 검증
3. `--dry-run` 제거하고 실제 반입
4. `python -m exam_analyzer corpus stats` 로 적재 확인

**기대 효과**: `~/.exam_corpus.json` 에 **HIGH 신뢰도 1차 문항** 등재.

**참고**: 저작권 민감 원본은 저장소 커밋 금지 (`.gitignore`). 홈 디렉터리만.

---

## 🧠 Step 6 — R_RE Agent P9 리버스 엔지니어링 (20~40분)

**선행 조건**: Step 1~5 완료 + corpus 최소 N개 문항 적재 (목표 ≥ 50개).

**실행**:
```
프롬프트: docs/agent_templates/P9_reverse_engineering.md 참조
입력: corpus (1차) + R4 대행사 정보 + R6 2차 후기 + 학술 논문 L4 (수리 성별차) 반영
출력: 50_reverse_engineered_predicts.md
```

**검증**: SC1 + SC2 + P11 태상위원 경보 확인 (필요 시).

**기대 효과**: **예상 문항 생성** (근거 체인 동반) → corpus 에 `kind="reverse_engineered"` 로 추가.

---

## 🎯 Step 7 — 회독 시스템 가동 (장기, 사용자 중심)

**실행**:
```
python -m exam_analyzer corpus list               # 전체 목록 확인
# 사용자 직접 회독 (drill CLI 인터랙션 or 자체 노트 회독)
# 시도마다 Attempt 기록을 JSON 으로 누적 입력
python -m exam_analyzer corpus mastery            # 숙련도 추적
```

**목표**: 숙련도 ≥ 95% (북극성 도달).

**재투입**: 매 라운드 후 P9 재호출 (새 후기·개정법령 반영), 약점 유형 drill 집중.

---

## 🏛 Step 8 — C-4 경연 (중대사 발생 시)

**트리거 조건** (자동 탐지):
- 외부 도구 설치 필요 (예: OCR 설치)
- 예산 추가 (책 추가 구매)
- 전략 전환 (예: 직무 트랙 변경)
- 개인정보 공유 방식 변경

**실행**: `docs/gyeongyeon/YYYY-MM-DD_주제.md` 안건서 작성 → AskUserQuestion 으로 사용자 판결 → 판결 기록.

---

## ⚠ 실패·중단 대응 (C-11)

| 상황 | 대응 |
|---|---|
| 사용자 자료 공유 실패 (용량·형식) | 대안 포맷 제안 (텍스트 복붙, 부분 스샷) |
| 에이전트 fetch 403 재발 | CLAUDE.md §2.2b fallback — 메인 세션에서 WebSearch 스니펫 마이닝 |
| 수석위원 PASS·REJECT 상충 | C-4 경연 회부 |
| 사용자 멘탈 흔들림 | C-11 §"완벽 못해도 괜찮다" 공간 제공, 데이터 무결성(C-0)만 유지 |
| 타임아웃 | 작은 단위로 재분할, 자주 commit (C-3 section 3) |

---

## 📊 최종 성공 지표 (북극성)

- **복원률 95%**: 시험장에서 "90%는 본 문제"로 느끼도록
- **숙련도 95%**: 회독 corpus 의 문항 중 3회독 연속 정답률 90%+ 비율
- **예상 문항 적중**: P9 생성 문항 중 실 시험 재출제 확인 비율

## 🌅 사용자 깨어나서 첫 액션 추천

```
1. git pull origin claude/fix-handwriting-recognition-J9xJq
2. README.MD 열람 (~3분)
3. docs/exam_reconstruction/.../00_meta.md 열람 (~2분)
4. 아래 중 가능한 것 순서대로 공유:
   (a) M1 공고 PDF 스샷 또는 복붙 텍스트
   (b) M2 직렬코드 매핑 (공고 별첨)
   (c) M3 보유 이북 목록 (제목만이라도)
5. 교재 구매 결정 (20_book_purchase_recommendation.md §5 의사결정 6단계 참조)
```

각 자료 주시면 Step 1~8 순차 가동합니다. 자료 없이는 "비팩트 → 스노우볼" (C-0) 을 유발하므로 추측으로 진행 금지.
