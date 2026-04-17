# 서민금융진흥원 2026 상반기 종합직 일반 — 조사 메타 (R3 진행 중)

## 조사 대상 식별
- **기관**: 서민금융진흥원 (Korea Inclusive Finance Agency / KINFA)
- **회차**: 2026년 상반기 신규채용
- **직렬**: 종합직 (사용자는 "금융일반" 으로 표현 — 직렬명인지 전공과목명인지 검증 필요)
- **사용자 수험번호**: 1056-115716 (앞 1056 이 직렬 코드로 추정)
- **필기 시행일**: 2026-04 초·중순 (정확일 미확정)
- **결과 통보일**: 2026-04-17 (사용자 공식 결과화면 스크린샷 제시)
- **사용자 실점수**: 직업기초 19.33/40 (48.3%), 직무 38.76/60 (64.6%), 총점 58.09, 커트 64.48, **격차 -6.39**
- **결정적 약점**: 직업기초(NCS) 48.3% ← 직무(64.6%) 대비 16.3%p 낮음. 복원·대비 가중치는 NCS 쪽에 더 실려야 함.
- **북극성 직접 증거**: 이 결과 화면이 본 프로젝트(복원률 95%) 존재 이유. C-0 팩트 판정 통과 (공식 결과 화면 원문, 2026-04-17, 사용자 1차 증거).

## 조사 상태 (2026-04-16 기준)
- **확정 팩트**: 0건 (공식 공고 원문 접근 실패)
- **저신뢰 스니펫**: 여러 건 (`10_official_facts_snippets.md` 참조. 검증 전 사용 금지)
- **접근 실패 소스**: 많음 (아래 §접근 실패 목록)

## 환경 제약 (2026-04-16 확인)
- WebFetch: 한국 채용/커뮤니티 도메인 다수에서 HTTP 403 (봇 차단)
- Bash curl: sandbox allowlist 차단 ("Host not in allowlist")
- Wayback Machine (web.archive.org): 차단
- 영향: 공식 공고 PDF·후기 원문 직접 취득 어려움. WebSearch 스니펫에 의존해야 하나 **ZERO-TOLERANCE 규칙** 상 스니펫 단독은 팩트로 쓸 수 없음 (출처 확정성 부족).

## 접근 실패 URL 목록
- https://www.kinfa.or.kr/notificationPromotion/recruitmentNotice.do (공식 공고) — 403
- https://recruit.incruit.com/kinfa — 403
- https://kinfa.scout.co.kr/jobinfo/ — 403
- https://www.jobkorea.co.kr/recruit/co_read/recruit/c/c-038020 — 403
- https://www.alio.go.kr/information/informationRecruitDtl.do?seq=254114&pageNo=1 — 403
- https://www.catch.co.kr/Comp/RecruitInfo/HU2145 — 403
- https://community.linkareer.com/written_test/1658952 — 403
- https://linkareer.com/activity/227941 — 403
- https://457deep.com/community/success-story/detail/cmdprlxpb001hx1pqlv8i2u2c — 403
- https://public.conects.com/review/pass/view/2089625 — 403
- https://jasoseol.com/companies/4498/careers — 403
- https://ko.wikipedia.org/wiki/서민금융진흥원 — 403
- https://en.wikipedia.org/wiki/Korea_Inclusive_Finance_Agency — 403
- https://namu.wiki/w/서민금융진흥원 — 403
- https://www.data.go.kr/data/15074498/openapi.do — 403
- https://web.archive.org/* — Claude Code 차단

## 다음 시도 방향 (아이디어 풀 — 에이전트 회의 결과)
1. Google Scholar / KRIVET / 학술 DB: 한국 공기업 채용 구조·NCS 측정 연구 논문 (영문 포함 가능 → 덜 차단)
2. GitHub repo 검색: 서민금융진흥원·KINFA·공기업 NCS 관련 OSS 데이터셋
3. 공공데이터포털 API 직접 (JSON 응답형) — WebFetch JSON 은 허용될 가능성
4. 영문 뉴스 (Yonhap, Korea Herald) 에서 KINFA 언급
5. 사용자 직접 제공 (스샷, 원문 복붙) — §요청 추가 자료 참조

## 요청 추가 자료 (필수, 공개 소스로 확보 불가한 범주)
다음 정보는 공개 웹에서 직접 추출 실패. 사용자 협조 필요:
1. **2026년 상반기 서민금융진흥원 종합직(일반) 채용공고 PDF** 의 본문 (스샷 또는 복붙)
   - 시험 영역·문항수·시간·배점 명시 페이지
   - 자격요건·우대가점·합격배수 명시 페이지
   - 채용대행사 명시 여부
2. 사용자 수험번호 앞자리 `1056` 의 **직렬 매핑표** (공고상 직렬-코드 표)
3. 필기 시행일 확정 (사용자 수기 기록)

## 진행률 (Phase 0 → R3)
- Phase 0 ✓ (직렬: 종합직 일반, 필기일 2026-04 초·중순)
- R1 ✓ b8ef43e (audit 수정)
- R2 ✓ 1c6f22d (plan v3)
- R3 ⚠ 공식 공고 확보 실패. 추가 자료 요청 발송 중.
- R5 (예비) ✓ c44d415 (교재 구매 추천서 Tier S/A/B/X)
- R8 ✓ corpus 모듈 + CLI 통합 + 67 unittest 통과 (2130a4f)

## 2026-04-16 사용자 수면 중 완료 사항

사용자가 6시간 수면 선언. 사전 작업 진행:
- 헌법 C-0~C-11 + C-3 확장 (학술 논문 조사 의무) 제정 완료
- 에이전트 프롬프트 템플릿 P1/P2/P4/P9/P10/SC1_SC2 완성 (P3/P5/P6/P7/P11 은 실 투입 시점에 맞춤 작성)
- corpus 모듈 6종 구현 + CLI stats/list/import/mastery 통합
- 교재 구매 추천서 (20_book_purchase_recommendation.md) — 사용자 깨어나 구매 가능
- 학술 자료 인덱스 (30_academic_literature.md) — KRIVET L1/L2/L3, 조성준·박찬균 (2020) L4, KIF L5, 공정채용 L7 등 8건
- audit-v3 전수 정합성 점검 (헌법 ↔ 코드 ↔ 문서 혈통 OK)
- README.MD 전면 갱신 (사용자 재개 가이드 포함)
- 총 ~38 커밋, 67 unittest 전부 통과

## 사용자 깨어나서 즉시 확인 필요
1. `README.MD` — 최신 구조 · 재개 가이드
2. `docs/exam_reconstruction/.../99_required_materials.md` — M1/M2/M3 요청
3. `docs/exam_reconstruction/.../20_book_purchase_recommendation.md` — 교재 구매 계획
4. `docs/exam_reconstruction/.../30_academic_literature.md` — 학술 자료 8건

**블로커**: M1 공고 PDF / M2 직렬코드 / M3 보유 이북 목록 — 이 3개만 주시면 R3~R6~R_RE 연쇄 재개.
