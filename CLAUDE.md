# 프로젝트 규칙 — CatchMe AI 메모리 연동

## 사용자 이해도 (최우선 규칙)

- 37세, IT 비전공자, 개발 경험 없음
- 한국어만 사용 (기술 용어 사용 금지)
- NCS 기반 공기업 시험 준비 중 (근로복지공단, 건강보험공단, 서민금융진흥원)
- 하루 공부 시간: 출퇴근 2시간 (출근 1시간 + 퇴근 1시간)
- 사용 중인 AI 도구: Gemini, NotebookLM, Notion, Google Keep
- Claude Max 구독 중, API 비용에 민감
- 컴퓨터/코딩 완전 초보 → 모든 것을 자동으로 처리해야 함

## 의도 해석 규칙

1. 사용자의 말을 액면 그대로 받지 말고 **진짜 의도**를 파악할 것
2. "그거 좀 해줘" = 조사 + 실행 + 결과 보고까지 전부 처리
3. 질문하기 전에 먼저 현재 상태를 조사할 것
4. 끝까지 완료하고 결과만 보여줄 것 (중간 과정 설명 금지)

## Claude의 행동 규칙

- 절대로 사용자에게 명령어를 실행하라고 하지 말 것
- 절대로 코드 블록을 보여주며 "이걸 실행하세요"라고 하지 말 것
- 기술 용어 사용 금지 — 일상 언어와 비유로 설명
- 결과를 간결하게 보여줄 것
- 파일을 읽어서 요약해줄 것 (사용자에게 열어보라고 하지 말 것)

## CatchMe 메모리 시스템

### CatchMe란?

사용자의 디지털 활동을 자동으로 기록하고 기억하는 AI 메모리 시스템.
화면, 키보드, 마우스, 클립보드, 알림 등을 백그라운드에서 기록하고,
계층적 활동 트리 (일 → 세션 → 앱 → 위치 → 동작)로 자동 정리함.
벡터 DB 없이 LLM이 트리를 탐색하여 자연어 질문에 답변.

- GitHub: https://github.com/HKUDS/CatchMe
- 개발: 홍콩대학교 데이터지능연구소 (HKUDS)
- 라이선스: Apache 2.0

### CatchMe 사용 규칙

| 사용자가 말하는 것 | Claude가 하는 것 |
|---|---|
| "CatchMe 설치해줘", "기록 시스템 깔아줘" | `bash scripts/setup-catchme.sh` 실행 |
| "CatchMe 켜줘", "기록 시작" | `conda run -n catchme catchme awake` 실행 |
| "아까 뭐 했지?", "방금 뭐 했어?" | `python catchme_bridge/ask.py "최근 활동 요약"` 실행 |
| "오늘 공부 뭐 했어?" | `python catchme_bridge/ask.py "오늘 학습 활동 요약"` 실행 |
| "기록 얼마나 쌓였어?" | `python catchme_bridge/status.py` 실행 → 한국어 요약 |
| "비용 얼마 들었어?" | `conda run -n catchme catchme cost` 실행 → 한국어 요약 |
| "공부 추천해줘" | `python catchme_bridge/study.py` 실행 → 맞춤 추천 |
| "CatchMe 상태" | `python catchme_bridge/status.py` 실행 |

### CatchMe + NCS 공부 연동

1. "공부하자"라고 하면:
   - CatchMe에서 최근 학습 활동 조회
   - 오래 안 한 과목, 취약 유형 파악
   - 가장 필요한 과목을 자동 선택하여 추천

2. CatchMe 기록 + study/progress/tracker.json 교차 분석:
   - 어떤 과목을 얼마나 공부했는지 (CatchMe 기록)
   - 어떤 문제를 틀렸는지 (tracker.json)
   - 두 데이터를 합쳐서 최적 학습 추천

## 파일 구조

```
ubermensch/
├── CLAUDE.md                          # 이 파일 (프로젝트 규칙)
├── README.MD                          # 프로젝트 설명
├── requirements.txt                   # 의존성
├── scripts/
│   └── setup-catchme.sh               # CatchMe 자동 설치
├── catchme_bridge/                    # CatchMe 연동 모듈
│   ├── __init__.py
│   ├── config.py                      # 설정 관리
│   ├── ask.py                         # 질의 래퍼
│   ├── status.py                      # 상태 집계
│   └── study.py                       # NCS 학습 추천
└── .claude/
    ├── settings.json                  # Claude Code 설정
    └── skills/
        └── catchme/
            └── SKILL.md               # /catchme 스킬
```
