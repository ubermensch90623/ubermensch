# Ubermensch — CatchMe AI 메모리 연동

## 이 프로젝트는 뭐하는 거야?

[CatchMe](https://github.com/HKUDS/CatchMe)라는 AI 메모리 시스템을 NCS 공부에 연결합니다.

컴퓨터에서 하는 모든 활동을 자동으로 기록하고, 나중에 자연어로 물어볼 수 있습니다.
NCS 시험 준비와 연동하여 맞춤형 학습 추천도 받을 수 있습니다.

## 어떻게 쓰나요?

Claude에게 말하면 됩니다:

| 말하기 | 결과 |
|--------|------|
| "CatchMe 설치해줘" | 자동 설치 |
| "아까 뭐 했지?" | 활동 기록 조회 |
| "오늘 공부 뭐 했어?" | 학습 활동 요약 |
| "공부 추천해줘" | CatchMe 기록 기반 맞춤 과목 추천 |
| "기록 얼마나 쌓였어?" | 저장 용량, 이벤트 수 확인 |
| "비용 얼마 들었어?" | LLM 토큰 사용량 확인 |

## CatchMe란?

홍콩대학교 데이터지능연구소(HKUDS)가 개발한 오픈소스 AI 메모리 시스템입니다.

- 6개 백그라운드 레코더가 화면, 키보드, 마우스, 클립보드, 알림을 자동 기록
- 계층적 활동 트리 (일 → 세션 → 앱 → 위치 → 동작)로 자동 정리
- 벡터 DB 없이 LLM이 트리를 탐색하여 자연어 질의에 응답
- 모든 데이터는 로컬에 저장 (개인정보 보호)
- 경량: 메모리 ~0.2GB, 디스크 ~200MB/2시간

## 파일 구조

```
├── CLAUDE.md                  # 프로젝트 규칙
├── scripts/setup-catchme.sh   # 자동 설치 스크립트
├── catchme_bridge/            # CatchMe 연동 모듈
│   ├── config.py              # 설정 관리
│   ├── ask.py                 # 질의 래퍼
│   ├── status.py              # 상태 집계
│   └── study.py               # NCS 학습 추천
└── .claude/skills/catchme/    # Claude Code 스킬
```

## 참고

- CatchMe GitHub: https://github.com/HKUDS/CatchMe
- PyTorch Korea 소개글: https://discuss.pytorch.kr/t/catchme-ai-feat-hkuds/9515
- 라이선스: Apache 2.0
