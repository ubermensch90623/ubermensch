# Ubermensch — CatchMe AI 메모리 + Goose AI 에이전트 연동

## 이 프로젝트는 뭐하는 거야?

두 가지 AI 도구를 NCS 공부에 연결합니다:

1. **[CatchMe](https://github.com/HKUDS/CatchMe)** — 디지털 활동을 자동 기록하고 자연어로 조회
2. **[Goose](https://github.com/block/goose)** — 레시피 기반 AI 에이전트로 학습 자동화

## 어떻게 쓰나요?

Claude에게 말하면 됩니다:

### CatchMe (활동 기록 & 메모리)

| 말하기 | 결과 |
|--------|------|
| "CatchMe 설치해줘" | 자동 설치 |
| "아까 뭐 했지?" | 활동 기록 조회 |
| "오늘 공부 뭐 했어?" | 학습 활동 요약 |
| "공부 추천해줘" | CatchMe 기록 기반 맞춤 과목 추천 |
| "기록 얼마나 쌓였어?" | 저장 용량, 이벤트 수 확인 |

### Goose (학습 자동화 에이전트)

| 말하기 | 결과 |
|--------|------|
| "Goose 설치해줘" | 자동 설치 |
| "문제 내줘", "Goose로 공부" | NCS 맞춤 문제 출제 |
| "오답 복습해줘" | 틀린 문제 유형 재학습 |
| "학습 계획 짜줘" | 이번 주 학습 계획 생성 |
| "취약 과목 분석해줘" | 과목별/유형별 정답률 분석 |
| "CatchMe 기록으로 분석해줘" | 활동 기록 + 진도 교차 분석 |

## CatchMe란?

홍콩대학교 데이터지능연구소(HKUDS)가 개발한 오픈소스 AI 메모리 시스템.

- 6개 백그라운드 레코더가 화면, 키보드, 마우스, 클립보드, 알림을 자동 기록
- 계층적 활동 트리 (일 → 세션 → 앱 → 위치 → 동작)로 자동 정리
- 벡터 DB 없이 LLM이 트리를 탐색하여 자연어 질의에 응답
- 모든 데이터는 로컬에 저장 (개인정보 보호)
- 경량: 메모리 ~0.2GB, 디스크 ~200MB/2시간

## Goose란?

Block(구 Square)이 개발한 오픈소스 AI 에이전트.

- 코드 작성, 실행, 디버깅, 워크플로우 자동화를 독립적으로 수행
- 레시피(YAML)로 반복 작업을 패키징하여 재사용 가능
- MCP 서버 3,000개 이상과 통합 가능
- 25개 이상의 LLM 제공자 지원
- 데스크톱 앱 + CLI 모두 제공

## Goose 레시피

| 레시피 | 용도 |
|--------|------|
| `ncs-study-assistant` | NCS 문제풀이, 오답복습, 학습계획, 취약분석 |
| `catchme-memory-review` | CatchMe 활동 기록 기반 학습 리뷰 |

## 파일 구조

```
├── CLAUDE.md                          # 프로젝트 규칙
├── scripts/
│   ├── setup-catchme.sh               # CatchMe 자동 설치
│   └── setup-goose.sh                 # Goose 자동 설치
├── catchme_bridge/                    # CatchMe 연동 모듈
├── goose_bridge/                      # Goose 연동 모듈
├── recipes/                           # Goose 레시피 (YAML)
└── .claude/skills/                    # Claude Code 스킬
```

## 참고

- CatchMe GitHub: https://github.com/HKUDS/CatchMe
- Goose GitHub: https://github.com/block/goose
- PyTorch Korea 소개글: https://discuss.pytorch.kr/t/catchme-ai-feat-hkuds/9515
- 라이선스: Apache 2.0
