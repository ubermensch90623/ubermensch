# .claude/agents/ — 프로젝트 서브에이전트 정의

Claude Code (데스크탑·CLI) 가 이 폴더를 자동 로드하여 Agent 도구의 `subagent_type` 으로 사용 가능.

## 편제 (11 페르소나, 파일 12개)

| 파일 | 페르소나 | 역할 | 상세 문서 |
|---|---|---|---|
| `p1-announcement-analyst.md` | P1 | 공공기관 채용공고 분석 | `docs/agent_templates/P1_announcement_analyst.md` |
| `p2-outsourcer-analyst.md` | P2 | 수의계약 채용대행업체 식별 | `docs/agent_templates/P2_outsourcer_analyst.md` |
| `p3-ncs-examiner.md` | P3 | NCS 10영역 출제 경향 분석 | — (간결) |
| `p4-aladin-catalog.md` | P4 | 알라딘·교보 카탈로그 메타 | `docs/agent_templates/P4_aladin_catalog.md` |
| `p5-review-screener.md` | P5 | 공개 후기 수집 | `docs/agent_templates/P5_P6_P7_review_skeptic_synthesist.md` |
| `p6-skeptic.md` | P6 | 회의론자·교차 팩트체크 | ↑ |
| `p7-synthesist.md` | P7 | 합성가 (통합 재구성) | ↑ |
| `p9-reverse-engineer.md` | P9 | 리버스 엔지니어링 예상 문항 | `docs/agent_templates/P9_reverse_engineering.md` |
| `p10-archivist.md` | P10 | 기록관 · C-9 전수 기록 | `docs/agent_templates/P10_archivist.md` |
| `p11-supreme-overseer.md` | P11 | 태상위원 · 재탄생 관조자 | — (간결) |
| `sc1-senior-chief.md` | SC1 | 수석위원 1 (사실 검증) | `docs/agent_templates/SC1_SC2_senior_chief.md` |
| `sc2-senior-chief.md` | SC2 | 수석위원 2 (방법론 심사) | ↑ |

## 자격 기준 (헌법 C-1, 모두 동일)

**박사급 + 실무 10년 이상 + 출제위원 경험 우선** (SC1/SC2/P11 은 실무 20년+ 출제위원장).

## 사용

Claude Code 에서 Agent 도구 호출 시 `subagent_type: p1-announcement-analyst` 로 지정.
프롬프트 본문은 파일의 frontmatter `---` 아래 시스템 프롬프트가 자동 삽입됨.

## 헌법 준수

모든 에이전트는 `../CLAUDE.md` §C-0 ~ §C-11 준수.
- **C-0**: 출처 없는 주장 금지 (ZERO-TOLERANCE)
- **C-2**: 답변이 박사급·상위1% 수준 미달이면 침묵
- **C-5**: 서로의 생성 원리 의심
- **C-6**: 인기영합 금지
- **C-11**: 완벽 환상 배격 · 작게 자주 망하라

## 호출 파이프라인 전형 예시 (readiness_checklist Step 1)

```
사용자 M1 공고 PDF 공유
 → Agent(subagent_type="p1-announcement-analyst", ...)
 → Agent(subagent_type="sc1-senior-chief", prompt: P1 산출물 심사)
 → Agent(subagent_type="sc2-senior-chief", prompt: 동일 산출물 방법론 심사)
 → 둘 다 PASS → docs/.../10_official_facts.md 확정 이관
 → Agent(subagent_type="p10-archivist", prompt: 라운드 기록)
```
