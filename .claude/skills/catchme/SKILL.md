---
name: catchme
description: >-
  CatchMe AI 메모리 시스템 관리 및 활동 조회.
  디지털 활동 기록 조회, 설치/설정/시작 자동 처리, NCS 학습 추천.
  "아까 뭐 했지?", "CatchMe 켜줘", "활동 기록", "메모리", "공부 추천" 등의 요청에 사용.
argument-hint: "<setup|ask|status|study-recommend> [질문]"
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
---

# CatchMe AI 메모리 시스템 스킬

CatchMe(https://github.com/HKUDS/CatchMe)를 관리하고 활용하는 스킬입니다.

## 서브커맨드

`$ARGUMENTS`에서 서브커맨드를 파싱합니다:

### 1. `setup` — CatchMe 설치

```bash
bash "$CLAUDE_PROJECT_DIR/scripts/setup-catchme.sh"
```

설치가 완료되면 결과를 한국어로 요약합니다.
설치 중 에러가 발생하면 원인을 파악하여 사용자에게 알려줍니다.

선택적 인자:
- `--provider <이름>`: LLM 제공자 (ollama, openrouter, anthropic 등)
- `--api-key <키>`: API 키
- `--model <모델>`: 모델 이름

### 2. `ask <질문>` — 활동 기록 질의

```bash
cd "$CLAUDE_PROJECT_DIR" && python -m catchme_bridge.ask "<질문>"
```

또는 직접:
```bash
conda run -n catchme catchme ask -- "<질문>"
```

결과를 한국어로 자연스럽게 요약하여 사용자에게 전달합니다.
기술적인 출력은 절대 그대로 보여주지 않습니다.

### 3. `status` — 시스템 상태 확인

```bash
cd "$CLAUDE_PROJECT_DIR" && python -m catchme_bridge.status
```

RAM 사용량, 디스크 사용량, LLM 비용을 한국어로 요약합니다.

### 4. `study-recommend` — NCS 학습 추천

```bash
cd "$CLAUDE_PROJECT_DIR" && python -m catchme_bridge.study
```

CatchMe 활동 기록과 학습 진도를 교차 분석하여 추천 과목을 제시합니다.

## 실행 전 확인 사항

1. CatchMe 설치 여부 확인:
   ```bash
   conda run -n catchme catchme --help 2>/dev/null
   ```
   실패하면 사용자에게 설치를 제안합니다.

2. CatchMe 실행 여부 확인:
   ```bash
   conda run -n catchme catchme ram 2>/dev/null
   ```
   실행 중이 아니면 자동으로 시작합니다:
   ```bash
   nohup conda run -n catchme catchme awake > ~/catchme-install/logs/awake.log 2>&1 &
   ```

## 출력 규칙

- 모든 출력은 **한국어**로 합니다
- 기술 용어를 사용하지 않습니다
- CLI 출력을 그대로 보여주지 않고, 핵심만 요약합니다
- 에러 시 사용자가 이해할 수 있는 안내를 제공합니다

## 웹 대시보드

사용자가 대시보드를 요청하면:
```bash
conda run -n catchme catchme web -p 8765 &
```
"브라우저에서 http://127.0.0.1:8765 를 열어주세요"라고 안내합니다.

## 트러블슈팅

| 증상 | 해결 |
|------|------|
| "conda를 찾을 수 없음" | `bash scripts/setup-catchme.sh`로 재설치 |
| "catchme 명령을 찾을 수 없음" | `conda run -n catchme pip install -e ~/catchme-install` |
| "데이터가 없음" | CatchMe가 실행 중인지 확인, 최소 몇 분 기록 후 재시도 |
| "LLM 오류" | `~/.catchme/config.json`에서 API 키/모델 확인 |
| "응답 시간 초과" | LLM 제공자 연결 상태 확인, 로컬(Ollama) 전환 고려 |
