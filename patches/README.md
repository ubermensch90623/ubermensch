# claude-smart 검토 후속 patch

`claude-smart-review.md` 의 발견 사항을 [ReflexioAI/claude-smart](https://github.com/ReflexioAI/claude-smart) 의 v0.2.31 main 브랜치 (commit `087e71e`) 에 적용한 patch 파일들입니다.

업스트림에 PR 로 제출하시려면 `git am` 또는 `git apply` 로 적용하시면 됩니다.

## 적용 방법

```bash
git clone https://github.com/ReflexioAI/claude-smart.git
cd claude-smart
git checkout -b feature/review-fixes
git apply /path/to/patches/01-onnx-warmup.patch
git apply /path/to/patches/02-static-analysis.patch
git apply /path/to/patches/03-project-id-remote-aware.patch
```

각 patch 마다 commit 하시고 (제 환경에서 서명 서버 이슈로 commit 자체는 못 만들었습니다), PR 로 제출.

## Patch 목록

### `01-onnx-warmup.patch` — ONNX 임베딩 콜드스타트 완화

**대상**: `plugin/scripts/backend-service.sh`

**문제**: 백엔드의 `/health` 엔드포인트는 임베딩 모델을 로드하지 않습니다.
따라서 PreToolUse 훅이 처음으로 `/api/search` 를 호출할 때 ONNX MiniLM-L6
모델 (~80MB) 을 그제서야 메모리에 올립니다. 10초 timeout 안에 못 끝나면
스킬 주입이 조용히 skip 됩니다.

**해결**: 백엔드가 `/health` 응답을 시작한 직후, dummy `/api/search` 쿼리를
백그라운드로 fire-and-forget. 응답은 버리고 모델 로드만 트리거합니다.

- `CLAUDE_SMART_DISABLE_WARMUP=1` 로 opt-out 가능
- curl `--max-time 30` 으로 bounded

### `02-static-analysis.patch` — 정적 분석 도구 설정 추가

**대상**: `plugin/pyproject.toml`

**문제**: pyproject 에 pytest 만 있고 ruff, mypy, coverage 설정이 전혀
없습니다. 코드 자체는 깔끔하지만 신규 컨트리뷰터의 회귀를 자동으로 잡을
안전망이 부족합니다.

**해결**:
- `[tool.ruff]` + `[tool.ruff.lint]` 추가 (E, F, W, I, B, BLE, UP, SIM, PTH, RUF)
  - `BLE` 는 keep (기존 `# noqa: BLE001` 패턴과 호환)
  - tests/* 에 BLE 면제
- `[tool.mypy]` strict 모드 + reflexio/chromadb 는 ignore_missing_imports
- `[tool.coverage]` 기본 설정
- dev deps 에 ruff, mypy, coverage 추가

### `03-project-id-remote-aware.patch` — project_id 충돌 완화

**대상**: `plugin/src/claude_smart/ids.py`

**문제**: `resolve_project_id` 가 git toplevel basename 만 사용합니다.
`playground`, `test`, `app` 같은 흔한 이름의 서로 다른 repo 들이
reflexio 의 같은 `user_id` 에 매핑되어 선호도·프로젝트 스킬이 섞입니다.

**해결**: `CLAUDE_SMART_PROJECT_ID_STYLE` 환경변수 도입.
- `basename` (default, 기존 동작 유지)
- `remote-aware` (opt-in): basename + `-` + git remote URL 의 sha1 6자리
  → 예: `my-repo-a1b2c3`

기본값은 backwards-compatible 하게 유지. opt-in 으로 전환 시 기존 데이터가
orphan 되므로 docstring 에 마이그레이션 가이드 포함.

## 적용되지 않은 항목

### Fix #1 — SessionStart fast-path

**원래 권고**: SessionStart 의 5개 셸 명령에 fast-path 추가

**검토 후 결론**: **이미 거의 구현되어 있음**. 원본 검토에서 과대평가했습니다.

근거:
- `plugin/scripts/smart-install.sh:102-114` 에 `install_complete()` 함수가
  fingerprint 기반 fast-path 제공. line 362 에서 호출되어 일치하면 즉시
  `emit_continue` + `exit 0`.
- `plugin/scripts/backend-service.sh:190` 에 `is_our_backend_running()` 가
  같은 패턴으로 short-circuit.
- `plugin/scripts/ensure-plugin-root.sh` 는 readlink 한 번이라 fast.

남은 cost 는 bash 인터프리터 5회 spawn (~수백 ms) + `hook_entry.sh
session-start` 의 Python 부팅 1회 (~500ms) 정도입니다. 그렇게 무겁지 않습니다.

원본 `claude-smart-review.md` 의 P0 #1 권고는 이 노트로 정정합니다.

## 참조

- 검토 보고서: `../claude-smart-review.md`
- 대상 저장소: https://github.com/ReflexioAI/claude-smart
- 적용 기준: main 브랜치, commit `087e71e` (v0.2.31 + Pause hook retries during provider stalls #39)
