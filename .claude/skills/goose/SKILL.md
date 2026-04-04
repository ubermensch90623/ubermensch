---
name: goose
description: >-
  Goose AI 에이전트 관리, 레시피 실행, NCS 학습 자동화.
  "Goose 설치", "레시피 실행", "Goose로 공부", "학습 에이전트" 등의 요청에 사용.
argument-hint: "<setup|recipe|session|status> [레시피명|세션명] [--param key=value]"
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
---

# Goose AI 에이전트 스킬

[Goose](https://github.com/block/goose)를 관리하고 레시피를 실행하는 스킬입니다.

## 서브커맨드

`$ARGUMENTS`에서 서브커맨드를 파싱합니다:

### 1. `setup` — Goose 설치

```bash
bash "$CLAUDE_PROJECT_DIR/scripts/setup-goose.sh"
```

선택적 인자:
- `--provider <이름>`: LLM 제공자 (openai, anthropic, google 등)
- `--api-key <키>`: API 키

### 2. `recipe <이름>` — 레시피 실행

사용 가능한 레시피:
- `ncs-study-assistant` — NCS 문제풀이, 오답복습, 학습계획, 취약분석
- `catchme-memory-review` — CatchMe 기록 기반 학습 리뷰

```bash
cd "$CLAUDE_PROJECT_DIR" && python -m goose_bridge.runner recipe <이름> [--param key=value]
```

또는 직접:
```bash
goose run --recipe "$CLAUDE_PROJECT_DIR/recipes/<이름>.yaml" --param subject=수리 --param count=5
```

### 3. `session [이름]` — 대화 세션 관리

```bash
cd "$CLAUDE_PROJECT_DIR" && python -m goose_bridge.runner session [이름]
```

세션은 대화형이므로 사용자에게 실행할 명령어를 안내합니다.

### 4. `status` — 상태 확인

```bash
cd "$CLAUDE_PROJECT_DIR" && python -m goose_bridge.status
```

### 5. `list` — 레시피 목록

```bash
cd "$CLAUDE_PROJECT_DIR" && python -m goose_bridge.runner list
```

## NCS 학습 연동 예시

사용자가 "Goose로 수리 문제 내줘" 라고 하면:
```bash
goose run --recipe "$CLAUDE_PROJECT_DIR/recipes/ncs-study-assistant.yaml" \
  --param subject=수리 --param count=5 --param mode=quiz
```

사용자가 "오답 복습해줘" 라고 하면:
```bash
goose run --recipe "$CLAUDE_PROJECT_DIR/recipes/ncs-study-assistant.yaml" \
  --param mode=review
```

사용자가 "이번 주 학습 계획 짜줘" 라고 하면:
```bash
goose run --recipe "$CLAUDE_PROJECT_DIR/recipes/ncs-study-assistant.yaml" \
  --param mode=plan
```

## 출력 규칙

- 모든 출력은 **한국어**로
- 기술 용어 사용 금지
- 레시피 실행 결과를 요약하여 전달
- 에러 시 사용자가 이해할 수 있는 안내 제공
