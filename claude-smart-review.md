# ReflexioAI/claude-smart 종합 검토 보고서

**검토 대상**: https://github.com/ReflexioAI/claude-smart (main 브랜치, v0.2.31)
**검토 일자**: 2026-05-21
**검토 범위**: 아키텍처/설계 · 코드 품질 · 성능/효율성 (보안 제외)
**검토 방식**: WebFetch 로 GitHub raw 파일을 읽어 정적 분석 (런타임 실행 없음)

---

## 1. 한눈에 보는 요약

### 이 프로젝트는 뭘 하는 건가요?

Claude Code 와 Codex CLI 에 **"학습 능력"** 을 붙여주는 플러그인입니다.
사용자가 "그렇게 하지 말고 이렇게 해" 라고 교정하면, 그 교정을 "다음에도 따를 규칙" 으로 자동 정제해서
나중 세션에서 Claude 가 알아서 적용하게 만듭니다.

- 단순 "메모리" 가 아니라 **"규칙(skill)" 으로 증류** 하는 것이 핵심 차별점
- 모든 데이터는 로컬에 저장 (`~/.reflexio/data/reflexio.db` 와 `~/.claude-smart/sessions/`)
- 외부 API 호출 없이 로컬 ONNX 임베딩으로 검색
- Next.js 기반 웹 대시보드 (`http://localhost:3001`) 제공

### 한 줄 평가

> **"실제 운영을 진지하게 고려한 매우 잘 설계된 플러그인."**
> 훅 라이프사이클을 깊이 이해하고 만든 흔적이 곳곳에 보입니다.
> 다만 설치 UX, 콜드스타트, 다중 호스트 통합 부분은 개선 여지가 명확합니다.

### Top 3 강점

1. **자기 자신을 호출했을 때 무한루프에 빠지지 않게 막는 설계** (`internal_call.py`)
   — Claude 가 Claude 를 호출하는 상황(claude-mem 같은 다른 플러그인 포함)까지 6가지 신호로 감지합니다.
2. **오프라인 우선(offline-first) 설계** — reflexio 백엔드가 죽어도 JSONL 버퍼에 쌓아두고
   다음번 훅에서 자동 복구. publish high-water mark 로 중복 발행도 방지.
3. **훅이 절대 사용자 세션을 망가뜨리지 않게 한 방어 코드** — 모든 핸들러가 예외를 흡수하고
   `emit_continue()` 로 안전하게 종료. 로그는 `~/.claude-smart/hook.log` 에 JSONL 로 남김.

### Top 3 리스크/개선 포인트

1. **SessionStart 가 매번 5개의 셸 명령을 실행** — 매 세션 시작마다 install 스크립트가
   다시 도는데, idempotent 하더라도 사용자 체감 지연이 큽니다.
2. **`project_id = git repo 폴더 이름`** — `playground`, `test`, `app` 같은 흔한 이름이면
   서로 다른 프로젝트의 학습이 섞일 위험이 있습니다.
3. **정적 분석 도구가 pyproject 에 설정되어 있지 않음** — pytest 만 설정되어 있고
   ruff/mypy/black 설정이 없습니다. 코드 자체는 깔끔하지만 회귀 방지 안전망이 부족합니다.

### 종합 등급

| 영역 | 등급 | 한 줄 평 |
|---|---|---|
| 아키텍처/설계 | A | 훅 라이프사이클을 잘 이해하고 만든 견고한 설계 |
| 코드 품질 | B+ | 모듈 분리·문서화는 우수하지만 정적 분석 미흡 |
| 성능/효율성 | B | 핫패스는 잘 최적화되어 있으나 콜드스타트·SessionStart 가 무거움 |

---

## 2. 아키텍처 및 설계

### 2.1 전체 그림 (Big Picture)

```
Claude Code / Codex (호스트)
        │
        │  ① 6개 라이프사이클 훅 발생
        ▼
plugin/hooks/hooks.json  (bash 셸 스크립트 와이어링)
        │
        │  ② hook_entry.sh → python -m claude_smart.hook <host> <event>
        ▼
plugin/src/claude_smart/hook.py  (디스패처)
        │
        │  ③ events/{session_start,user_prompt,pre_tool,post_tool,stop,session_end}.py
        ▼
이벤트 핸들러 ──┬── ~/.claude-smart/sessions/{id}.jsonl (로컬 버퍼)
                │
                └── reflexio_adapter.py → ReflexioClient(http://localhost:8071)
                                              │
                                              ├── SQLite (~/.reflexio/data/)
                                              ├── ChromaDB (벡터)
                                              └── ONNX 임베딩 (in-process)

별도 프로세스:
- backend-service.sh : reflexio 서버 (8071)
- dashboard-service.sh : Next.js 대시보드 (3001)
```

**쉽게 말하면**: 셸 스크립트가 Python 모듈을 호출하고, Python 모듈이 또 다른 로컬 서버(reflexio)
에게 "이거 학습해줘" 또는 "이 상황에 맞는 규칙 줘" 라고 묻는 구조입니다.

### 2.2 6개 훅 분석 (`plugin/hooks/hooks.json`)

| 훅 | matcher | timeout | 하는 일 |
|---|---|---|---|
| **Setup** | `*` | 300s | smart-install.sh 실행 (의존성·환경 부트스트랩) |
| **SessionStart** | `startup\|clear\|compact\|resume` | 5단계 (각 10-300s) | install + ensure-plugin-root + session-start + backend 시작 + dashboard 시작 |
| **UserPromptSubmit** | (전체) | 15s | 프롬프트를 JSONL 에 버퍼링 + reflexio 검색해서 관련 규칙 주입 |
| **PreToolUse** | `Edit\|Write\|NotebookEdit\|Bash` | 10s | 도구 호출 직전, 도구 입력으로 검색 → 관련 규칙 주입 |
| **PostToolUse** | `*` | 15s | 도구 호출 결과를 JSONL 에 기록 (secret 마스킹 포함) |
| **Stop** | (전체) | 30s | 어시스턴트 턴 마무리 → reflexio 로 publish |
| **SessionEnd** | (전체) | 5단계 (각 10-300s) | 강제 추출(force_extraction=True) + 대시보드·백엔드 종료 |

#### 좋은 점

- **PreToolUse 의 matcher 가 좁다**: 모든 도구가 아니라 mutate 가 의심되는 4종(Edit/Write/NotebookEdit/Bash)에만 발동.
  Read/Grep/Glob 같은 가벼운 도구에서는 지연이 0입니다.
- **idempotent 디자인**: `published_up_to` watermark 덕분에 같은 턴을 두 번 publish 하지 않습니다 (`state.py:unpublished_slice`).
- **failure-tolerant**: 모든 핸들러가 예외를 잡고 `emit_continue()` 를 호출 — 훅이 사용자 세션을 절대 죽이지 않습니다.

#### 우려되는 점

- **SessionStart 가 너무 무겁다**: 매 세션 시작마다 다음 5개 명령이 sequential 하게 실행됩니다.
  ```
  ① smart-install.sh           (300s)
  ② ensure-plugin-root.sh      (10s)
  ③ hook_entry.sh session-start (300s)
  ④ backend-service.sh start    (300s)
  ⑤ dashboard-service.sh start  (300s)
  ```
  idempotent 라고 해도 매번 셸 스크립트가 5번 도는 건 체감이 큽니다. 백엔드가 이미 떠 있는 경우의 fast path 가 필요해 보입니다.

- **`Setup` + `SessionStart` 의 install 중복**: `Setup` 매처도 `*`, `SessionStart` 첫 블록도
  같은 `smart-install.sh` 를 호출합니다. 호스트마다 둘 중 하나만 트리거된다면 의도된 것이지만,
  주석이 없어서 명확하지 않습니다.

- **`_R` 폴백이 fragile**: 모든 명령이 `_R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/reflexioai/plugin"` 패턴을
  반복합니다. 헬퍼 셸 함수로 한 번만 정의하는 게 유지보수에 좋습니다.

### 2.3 계층 분리 (Separation of Concerns)

세 개의 큰 계층이 깔끔하게 나뉘어 있습니다:

```
┌─────────────────────────────────────────────────────┐
│ plugin/src/claude_smart/   (호스트 통합 어댑터)        │
│   - hook.py, events/*       : 훅 입출력 처리           │
│   - state.py                : JSONL 버퍼              │
│   - reflexio_adapter.py     : reflexio 클라이언트 래퍼 │
└─────────────────────────────────────────────────────┘
                         │
                         ▼ (HTTP)
┌─────────────────────────────────────────────────────┐
│ reflexio (별도 PyPI 패키지 reflexio-ai)              │
│   - 학습 엔진, 추출, 임베딩, 저장                      │
└─────────────────────────────────────────────────────┘
                         │
                         ▼ (HTTP, REST API)
┌─────────────────────────────────────────────────────┐
│ dashboard/   (Next.js + TypeScript)                  │
│   - 시각화 UI                                         │
└─────────────────────────────────────────────────────┘
```

#### 잘된 점

- **`reflexio_adapter.py` 가 진정한 anti-corruption layer**: reflexio 의 응답 형태(dict 또는 attribute object)
  를 모두 흡수하는 `_extract_items` 헬퍼와, 모든 메서드가 실패 시 빈 결과를 반환해서
  훅 핸들러는 절대 reflexio 의 변화에 영향받지 않습니다.
- **테스트 주입성**: `Adapter` 가 매 함수의 인자로 받을 수 있도록 설계되어 있어 (`adapter or Adapter()`)
  단위 테스트에서 mock 으로 갈아끼우기 쉽습니다.

#### 우려되는 점

- **대시보드와 Python 사이에 공유 타입이 없다**: 대시보드 URL 패턴 (`/skills/project/{id}`, `/preferences/project/{id}`,
  `/rules/{id}`) 이 `context_format.py:_dashboard_url` 과 `cs_cite.py:dashboard_url_token` 양쪽에
  하드코딩되어 있습니다. 한쪽이 바뀌면 다른 쪽이 깨지지만 컴파일 타임에 잡히지 않습니다.

### 2.4 스킬 분류 체계

reflexio 의 데이터 모델을 claude-smart 가 어떻게 매핑하는지가 중요한 설계 결정입니다.

| 개념 | reflexio 이름 | claude-smart 매핑 | 스코프 |
|---|---|---|---|
| 선호도 | `user_profile` | "Project preferences" | `user_id = project_id` (프로젝트별) |
| 프로젝트 스킬 | `user_playbook` | "Project-specific skills" | `user_id = project_id` (프로젝트별) |
| 공유 스킬 | `agent_playbook` | "Shared skills" | `agent_version = "claude-code"` (글로벌, 호스트 공통) |

**핵심 설계 결정**: `agent_version` 을 Claude Code 와 Codex 둘 다 `"claude-code"` 로 고정 (`runtime.py:agent_version`).
즉, "Codex 에서 배운 교훈도 Claude Code 에서 보이고, 그 반대도 마찬가지" 라는 의도된 설계입니다.

#### 평가
- **장점**: 사용자가 어떤 도구를 쓰든 학습이 따라옵니다. UX 면에서 강력.
- **단점**: 호스트별 quirk (예: Codex 만 가지는 prompt 형식) 가 다른 호스트에 노출됩니다.
  `internal_call.py:is_codex_internal_prompt` 같은 호스트별 필터로 이를 막고 있지만,
  완벽한 필터는 어렵습니다. 호스트별 namespace 분리가 v2 고민거리.

### 2.5 인상적인 설계 디테일

#### "자기 자신을 학습하지 않게 막는" 설계 (`internal_call.py`)

이 부분이 매우 잘 만들어졌습니다. **6가지 신호를 OR 로 묶어서 감지**합니다:

1. `CLAUDE_SMART_INTERNAL=1` 환경변수 (reflexio 가 명시적으로 설정)
2. `CLAUDE_CODE_ENTRYPOINT != "cli"` (headless `claude -p` 가 `sdk-cli` 로 설정)
3. `payload.cwd` 가 reflexio 서브모듈 내부 (수동 디버깅 케이스)
4. Codex 의 title-generation 프롬프트 fingerprint
5. Codex 의 suggestions 프롬프트 fingerprint
6. Codex 의 title-only 응답 형식 (`{"title": "..."}`)

claude-mem 같은 다른 플러그인이 `claude -p` 로 자기 일을 하다가 claude-smart 훅을 발동시키면
**시스템 프롬프트가 사용자 turn 으로 reflexio 에 기록되는 사고**가 생길 수 있는데,
이를 의식적으로 방어하고 있습니다. 실제 운영 경험이 녹아 있는 코드입니다.

#### Plan 모드 의사결정 학습 (`events/stop.py`)

Plan 모드에서 사용자가 "거부(rejection)" 한 경우를 transcript 에서 파싱해서
**synthetic User record** 로 만들어 reflexio 가 교정 신호로 학습하게 합니다.
이런 도메인 특화 로직은 단순 "메모리 도구" 들에는 거의 없는 디테일입니다.

#### 인용 시스템 (`cs_cite.py`)

규칙이 적용됐을 때 Claude 가 `✨ claude-smart rule applied: [규칙명](대시보드URL)` 형태의
마커 라인을 출력하게 유도하고, 그 라인을 다시 파싱해서 "어떤 규칙이 실제로 사용됐는지" 를
대시보드에 추적합니다.
- markdown 링크와 OSC 8 터미널 하이퍼링크 두 가지 스타일 지원
- 정규식 3종(`_OSC8_URL_RE`, `_MARKDOWN_LINK_RE`, `_RAW_DASHBOARD_URL_RE`)으로 견고하게 파싱
- 인용 ID 충돌 방지를 위해 4글자 fingerprint (`real_id` 해시) 를 접미사로 부착

매우 잘 만들어진 시스템입니다. **"학습된 규칙이 실제로 답변에 영향을 줬는가" 를 측정 가능하게 만든 점이 핵심.**

---

## 3. 코드 품질

### 3.1 모듈 구성 (`plugin/src/claude_smart/`)

총 16개 모듈 + `events/` 서브패키지. 모듈 크기와 책임이 잘 나뉘어 있습니다.

| 모듈 | 역할 | 평가 |
|---|---|---|
| `hook.py` | 디스패처 (~95줄) | 단순·명확. 책임 명확. ✅ |
| `runtime.py` | 호스트 상태 (~30줄) | 미니멀. 적절. ✅ |
| `state.py` | JSONL 버퍼 | flock·redact·watermark 로직이 한 곳에. ✅ |
| `reflexio_adapter.py` | reflexio 래퍼 | 정확한 anti-corruption 계층. ✅ |
| `context_format.py` | 마크다운 렌더링 | render/render_inline 4개 변형. 약간 중복. 🟡 |
| `context_inject.py` | 검색+주입 (~60줄) | 단일 책임. ✅ |
| `query_compose.py` | 쿼리 합성 | 결정론적·짧음. ✅ |
| `publish.py` | publish 오케스트레이션 | 단일 함수, 세 호출자가 공유. ✅ |
| `internal_call.py` | self-invocation 감지 | 매우 깊이 있게 만들어짐. ✅✅ |
| `hook_log.py` | 구조화 로그 | flock + 회전 자체 구현. ✅ |
| `cs_cite.py` | 인용 파싱 | 정규식 다소 복잡하지만 잘 정리. ✅ |
| `ids.py` | project_id 결정 | git toplevel basename. 단순. 🟡 |
| `cli.py` | CLI (큰 모듈) | 다기능. 분리 여지 있음. 🟡 |
| `optimizer_assistant.py` | 외부 CLI 호출 | claude/codex CLI 를 read-only 로 실행. 흥미. ✅ |
| `publish.py`, `internal_call.py` 등 | (위 참조) | |
| `stall_banner.py` | UI 배너 | (미열람) |
| `hook_log.py` | (위 참조) | |
| `events/*.py` | 6개 핸들러 | 각 모듈이 매우 작고 명확. ✅ |

#### 잘된 점

- **docstring 이 매우 좋다**: 거의 모든 함수에 동기·트레이드오프·실패 모드까지 적힌
  Google-style docstring. 특히 `state.py:_truncate_tool_data_field` 처럼
  "왜 top-level string 만 자르는가" 를 길게 설명한 부분이 인상적입니다.
- **주석이 "왜" 에 집중**: "what" 이 아닌 "why" 를 설명하는 주석이 많습니다.
  예: `internal_call.py` 의 6가지 신호 각각의 이유 설명.
- **타입 힌트가 일관적**: `from __future__ import annotations` 와 함께 PEP 604 (`X | None`) 사용.
- **함수가 짧다**: 대부분 30줄 이하. `state.unpublished_slice` 정도가 좀 김.

#### 우려되는 점

##### 1. **정적 분석 도구가 설정되어 있지 않음**

`pyproject.toml` 을 보면:
```toml
[tool.pytest.ini_options]
testpaths = ["../tests"]

[dependency-groups]
dev = ["pytest>=9.0.3"]
```

**ruff, mypy, black 설정이 전부 없습니다.** 코드는 이미 깔끔해 보이지만,
- 향후 컨트리뷰터가 스타일을 깨도 자동으로 잡히지 않음
- 타입 힌트가 있는데 mypy 가 없어서 실제로 검증되지 않음
- `# noqa: BLE001` 주석이 곳곳에 있는데, ruff 설정이 없으면 강제 검사도 안 됨

CI 가 있는지는 못 봤지만, 적어도 다음은 추가 권장:
```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "BLE", "RUF", "UP", "SIM", "PTH"]

[tool.mypy]
python_version = "3.12"
strict = true
```

##### 2. **`context_format.py` 의 함수 중복**

`render` / `render_with_registry` / `render_inline` / `render_inline_with_registry`
4개가 거의 같은 일을 합니다. `render` 와 `render_inline` 은 각각의 `*_with_registry`
함수를 호출해서 markdown 만 반환합니다.

차이가 (a) 헤더 유무, (b) 섹션 제목("Project-specific" vs "Relevant project-specific") 정도입니다.
파라미터 하나(`inline: bool`)로 합치는 게 더 깔끔해 보입니다.

##### 3. **`cli.py` 는 너무 큼**

WebFetch 요약만으로 확인한 바로는 다음을 다 처리합니다:
- install/update/uninstall (Claude Code, Codex 양쪽)
- 백엔드·대시보드 서비스 관리
- show/learn/restart/clear-all/clear-user 명령
- TOML 설정·심볼릭링크·환경변수 관리
- Codex JSON-RPC 통신

서브커맨드별로 `cli/` 패키지로 분리하면 테스트도 쉽고 가독성도 좋아질 것입니다.

##### 4. **버전 정책이 불명확**

`version = "0.2.31"` 으로 SemVer 의 0.x 범주입니다. CHANGELOG.md 가 있는지 확인 못 했으나,
v0.2.x 범주에서 31번째 패치라는 점은 변경이 잦다는 신호입니다.
의존성 `reflexio-ai>=0.2.22` 도 핀이 느슨해서 호환성이 깨질 수 있습니다.

### 3.2 테스트

```
tests/
├── conftest.py             (3개 autouse fixture)
├── integration/
├── test_adapter.py
├── test_cli_clear_all.py
├── test_cli_clear_user.py
├── test_cli_install.py
├── test_cli_learn.py
├── test_cli_restart.py
├── test_codex_support.py
├── test_context_format.py
├── test_cs_cite.py
├── test_events.py
├── test_hook_log.py
├── test_ids.py
├── test_install_scripts.py
├── test_internal_call.py
├── test_optimizer_assistant.py
├── test_query_compose.py
├── test_stall_banner.py
├── test_stall_in_session_start.py
└── test_state.py
```

#### 잘된 점

- **모듈 1:1 매핑**: 거의 모든 모듈에 대응하는 테스트 파일이 있습니다.
- **isolation 잘 됨**: `conftest.py` 의 `autouse` fixture 들이 환경변수·상태를
  매 테스트마다 정리합니다 (`session_dir`, `clear_optimizer_opt_in`, `reset_runtime_host`).
- **CLI 테스트가 명령별로 분리**: `test_cli_clear_all.py`, `test_cli_install.py` 등.

#### 우려되는 점

- **`testpaths = ["../tests"]`**: pyproject 가 `plugin/` 안에 있고 tests 가 `plugin/../tests`
  를 가리키는 구조입니다. 작동은 하지만 모노레포 구조가 헷갈립니다.
  보통 `pyproject.toml` 과 `tests/` 가 같은 레벨에 있는 게 표준입니다.
- **dev 의존성이 pytest 뿐**: coverage, ruff, mypy, hypothesis 같은 도구가 없습니다.

### 3.3 의존성 위생

```toml
dependencies = [
    "reflexio-ai>=0.2.22",
    "chromadb>=0.5",     # ONNX 임베딩용
    "einops>=0.8.0",
]
```

- **chromadb≥0.5**: 무겁습니다. 설치 시 100MB+. ONNX runtime + tokenizers + chromadb 자체.
  주석에 "the ~80 MB ONNX model itself is downloaded on first use" 라고 적혀 있어 의식은 하고 있음.
- **einops≥0.8**: 일반적으로 모델 텐서 변형에 사용. 명시적인 사용처는 확인 못 함 (claude-smart 에서 직접 import 하는지 transitive 인지).
- 의존성 핀이 lower-bound 만 있어 (`>=`), 미래 깨짐 가능. `uv.lock` 이 있어서 재현은 가능하지만,
  PyPI 사용자에게는 매번 latest 가 설치됨.

### 3.4 대시보드 (`plugin/dashboard/`)

- Next.js (`next.config.ts`), TypeScript (`tsconfig.json`)
- shadcn/ui 로 보임 (`components.json`)
- App Router (`app/` 디렉토리)
- 자체 `eslint.config.mjs`, `postcss.config.mjs`

Python 백엔드와 별도 패키지/빌드입니다. 자세한 컴포넌트는 검토하지 않았지만,
modern Next.js 스택으로 보입니다.

---

## 4. 성능 및 효율성

### 4.1 핫 패스 (Hot Path) 분석

훅이 발동되는 빈도를 기준으로 분류해보면:

| 훅 | 발동 빈도 | 평균 작업 | 잠재 병목 |
|---|---|---|---|
| PostToolUse | **매우 높음** (모든 도구) | JSONL append + flock + redact | 디스크 I/O |
| UserPromptSubmit | 높음 | Python 부팅 + reflexio 검색 + 임베딩 + 마크다운 렌더 | **임베딩 콜드스타트** |
| PreToolUse | 중간 (Edit/Write/NotebookEdit/Bash 만) | 같음 | 같음 |
| Stop | 낮음 (턴마다) | transcript 파싱 + publish | 네트워크 |
| SessionStart | 매우 낮음 (세션당 1회) | 5단계 셸 | **백엔드·대시보드 부팅** |
| SessionEnd | 매우 낮음 (세션당 1회) | 강제 추출 | **LLM 호출** |

#### 4.2 임베딩 콜드스타트가 가장 큰 위험

- `chromadb` + `onnxruntime` + ONNX MiniLM-L6 모델 (~80MB) 이 메모리에 올라와야 첫 검색이 시작됩니다.
- 첫 사용 때 모델 다운로드까지 들어가면 수 초 ~ 수십 초가 걸릴 수 있습니다.
- PreToolUse 의 timeout 은 **10초**입니다. 이 안에 못 끝내면 Claude Code 는 추가 컨텍스트 없이 그냥 진행합니다.
- 좋은 의미로는: 실패해도 사용자 경험은 안 깨짐. 나쁜 의미로는: 첫 몇 세션에서는 학습 효과가 안 보일 수 있음.

**개선 제안**:
- SessionStart 에서 백엔드를 시작할 때 dummy embedding 한 번을 미리 돌려서 warm-up 시킬 것
- 또는 backend-service.sh 안에서 자동 warm-up

#### 4.3 PostToolUse 의 디스크 I/O

```python
# events/post_tool.py: 매 도구 호출마다
state.append(session_id, record)
# → 내부적으로:
# 1. path.parent.mkdir (idempotent)
# 2. json.dumps
# 3. fcntl.flock(LOCK_EX)
# 4. fh.write
```

- `flock` 은 동일 머신에서 두 Python 프로세스가 동시에 같은 JSONL 에 쓸 때를 막기 위함입니다.
- 도구 호출 1회당 디스크 sync 1번. 100번 도구를 쓰면 100번의 fsync (실제로는 append 라서 매번 fsync 는 아니지만).
- **현재 구조에서는 합리적**. 다만 reflexio publish 가 어차피 Stop 시점에서 일어나므로,
  더 공격적인 in-memory buffering 도 가능했을 텐데 안전 우선으로 disk-first 를 택한 듯합니다.

#### 4.4 검색 효율 (`reflexio_adapter.py:search_all`)

- 통합 `/api/search` 엔드포인트로 **1회 라운드트립에 3종(user_playbook, agent_playbook, profiles) 전부 가져옴**.
- `fetch_all` (`/show` 명령용) 은 `ThreadPoolExecutor(max_workers=3)` 으로 3개 엔드포인트 병렬 호출.
- search_mode: `"hybrid"` (BM25 + Vector RRF).
- `top_k=3` (inline injection), `top_k=10` (audit view) — 적절합니다.

**잘 설계되어 있습니다.** 굳이 더 줄일 곳이 없어 보입니다.

#### 4.5 SessionStart 가 너무 느릴 수 있음

```bash
# 매 세션마다 sequential 하게:
smart-install.sh                  # 설치 검증 (300s timeout)
ensure-plugin-root.sh             # 심볼릭링크 (10s)
hook_entry.sh session-start       # Python 부팅 + reflexio 컨피그 적용 (300s)
backend-service.sh start          # uvicorn 부팅 (300s)
dashboard-service.sh start        # Next.js 부팅 (300s)
```

5개 명령이 직렬입니다. 각각이 idempotent 하더라도:
- bash 부팅 5회
- Python interpreter 부팅 1회 (session-start)
- 노드 프로세스 확인 2회 (backend, dashboard)

**개선 제안**:
- 백엔드·대시보드 시작은 백그라운드로 fire-and-forget (이미 그렇게 되어 있을 수 있음 — 미확인)
- "이미 떠 있나?" 체크를 가장 먼저 두고, 떠 있으면 나머지 단계 skip
- `Setup` 매처와 `SessionStart` 의 install 호출 중복 제거

#### 4.6 SessionEnd 의 force_extraction

```python
# events/session_end.py 요약에 따르면:
# - 강제 추출(force_extraction=True) 호출
# - 즉, reflexio 가 즉시 LLM 추출을 동기적으로 실행
```

이는 LLM 호출 (`claude` CLI subprocess) 을 동반하므로 매우 느릴 수 있습니다.
다행히 timeout 이 300초로 넉넉하지만, 사용자가 세션을 닫고 나서도 백그라운드에서
무거운 작업이 돌고 있다는 의미입니다.

`session-end` 매처에 둘 셸 명령에 `&` 를 붙여 백그라운드로 보낼 수도 있을 텐데
(이미 그러는지 셸 스크립트 안을 봐야 정확), 검토 대상이 아니어서 미확인.

#### 4.7 토큰 효율

- 인용된 규칙 1개당 형식: `- [cs:s1-abcd] 규칙 내용 (when: 트리거) — why: 이유 (open: URL)`
- top_k=3 으로 inline injection — 최대 3개의 규칙만 주입
- 각 규칙은 트리거+이유까지 합쳐도 보통 100토큰 이하
- → **인라인 주입 1회 = 약 300토큰 이하**

이 부분도 잘 절제되어 있습니다. README 의 "측정된 토큰 vs 수천 토큰" 주장은 사실로 보입니다.

### 4.8 ChromaDB 의 scale 특성

- ChromaDB 는 single-process embedded 모드입니다.
- 스킬 수가 수천 건 이상으로 늘어나면 SQLite + chromadb 의 검색 지연이 증가할 수 있음.
- 하지만 claude-smart 의 스킬 수는 현실적으로 한 프로젝트당 수십~수백 건 수준일 것이므로
  실제로 문제될 가능성은 낮습니다.

---

## 5. 보안 관련 메모 (검토 범위 외이지만 발견된 항목)

검토 범위에서 보안은 제외했지만 코드를 읽다가 발견한 항목 몇 가지:

- ✅ **PostToolUse 의 secret 마스킹** (`post_tool.py:_mask_secrets`):
  `KEY=value` 형태에서 value 가 20자 이상이고 mixed-case+digit 이면 `<redacted:N>` 으로 치환.
  Heuristic 이라 완벽하지 않지만 합리적.
- ✅ **optimizer_assistant 의 sandbox**: `claude` 호출 시 `permission_mode=plan`, `disallowedTools=Edit,Write,...`,
  Codex 는 `--sandbox=read-only`. read-only 보장.
- 🟡 **`ids.py:resolve_project_id`** 에서 `git rev-parse --show-toplevel` 을 subprocess 로 호출.
  `cwd` 가 사용자가 제어하는 값이라 path injection 가능성은 없지만, 호출 빈도가 높음.
  (매 훅마다 git 호출 → 캐싱 여지 있음)
- 🟡 **`~/.claude-smart/sessions/{id}.jsonl`** 에 사용자 코드/명령이 평문 저장.
  Secret 마스킹이 있지만 heuristic. 민감 정보가 저장될 수 있음을 사용자에게 명시 필요.

---

## 6. 권장 사항 (우선순위 순)

### 🔴 P0: 즉시 검토 가치 있음

1. **SessionStart 의 install·체크 5단계 fast-path 추가**
   - 위치: `plugin/hooks/hooks.json` 의 SessionStart 블록
   - 제안: 백엔드가 이미 살아 있는지를 가장 먼저 확인하는 단일 스크립트로 묶고,
     이미 떠 있으면 나머지 단계 skip. 첫 세션은 무거워도 두 번째부터는 빠르게.

2. **임베딩 콜드스타트 warm-up**
   - 위치: `plugin/scripts/backend-service.sh` (미열람) 또는 `events/session_start.py`
   - 제안: 백엔드 부팅 후 dummy query 1회를 background 로 발사. PreToolUse 의 첫 10초 timeout 안에서
     실패하는 일을 줄임.

### 🟡 P1: 다음 분기 단위

3. **정적 분석 도구 추가**
   - 위치: `plugin/pyproject.toml`
   - 제안: `ruff` (lint+format), `mypy --strict`, `coverage` 추가 + CI 에서 강제.

4. **`project_id` 충돌 위험 완화**
   - 위치: `plugin/src/claude_smart/ids.py:resolve_project_id`
   - 제안: git remote URL 의 host+path 를 부수적으로 포함하거나, 사용자 설정 가능한 alias 도입.
     현재는 `playground`, `test`, `app` 같은 흔한 이름의 다른 repo 들이 학습을 공유함.

5. **`context_format.py` 의 render 함수 4개를 2개로 통합**
   - 위치: `plugin/src/claude_smart/context_format.py`
   - 제안: `render(inline: bool, ...)` 와 `render_with_registry(inline: bool, ...)` 로 통합.

6. **`cli.py` 분리**
   - 위치: `plugin/src/claude_smart/cli.py`
   - 제안: `cli/install.py`, `cli/service.py`, `cli/data.py`, `cli/codex.py` 로 분리.

### 🟢 P2: 여유 있을 때

7. **대시보드 URL 패턴의 단일 출처 정의**
   - 위치: `context_format.py:_dashboard_url`, `cs_cite.py:dashboard_url_token`
   - 제안: URL 패턴을 한 곳에 정의(상수 또는 작은 모듈), 양쪽에서 참조.

8. **CHANGELOG.md 도입**
   - 의존성 핀 정책과 함께 사용자가 업그레이드 의사결정을 할 수 있도록.

9. **호스트별 namespace 옵션 추가**
   - Claude Code 와 Codex 의 공유 학습이 부담스러운 경우를 위한 환경변수 옵션.

---

## 7. 종합 평가

claude-smart 는 **"훅 시스템을 실전에서 운영해본 사람" 이 만든 코드** 입니다.
다음과 같은 디테일이 단순 데모용 코드와는 격이 다릅니다:

- 자기 호출 무한루프 방어 (`internal_call.py`)
- 오프라인 버퍼링 + idempotent publish (`state.py`, `publish.py`)
- 모든 핸들러의 예외 흡수 + 구조화된 hook 로그
- secret 마스킹·필드 절단·flock 동시성 제어
- Plan 모드 거부를 학습 신호로 변환
- 인용을 통한 "규칙이 실제로 사용됐는가" 측정

코드 품질, 모듈 분리, 문서화 모두 우수합니다. 주요 개선 영역은 **사용자 경험(SessionStart 무게,
콜드스타트)** 과 **개발 인프라(static analysis 부재, 버전 핀)** 두 가지입니다.

오픈소스 플러그인으로서 **참고 가치가 매우 높은 프로젝트** 입니다.
훅 시스템을 만들 때 어떻게 견고하게 만들어야 하는지 배울 점이 많습니다.

---

## 부록 A: 검토 시 참조한 파일

### 직접 읽은 파일 (전체 코드)
- `plugin/hooks/hooks.json`
- `plugin/src/claude_smart/hook.py`
- `plugin/src/claude_smart/runtime.py`
- `plugin/src/claude_smart/state.py`
- `plugin/src/claude_smart/reflexio_adapter.py`
- `plugin/src/claude_smart/context_format.py`
- `plugin/src/claude_smart/context_inject.py`
- `plugin/src/claude_smart/query_compose.py`
- `plugin/src/claude_smart/publish.py`
- `plugin/src/claude_smart/internal_call.py`
- `plugin/src/claude_smart/hook_log.py`
- `plugin/src/claude_smart/cs_cite.py`
- `plugin/src/claude_smart/ids.py`
- `plugin/src/claude_smart/events/pre_tool.py`
- `plugin/src/claude_smart/events/post_tool.py`

### 요약·구조만 확인한 파일
- `plugin/src/claude_smart/cli.py`
- `plugin/src/claude_smart/events/session_start.py`
- `plugin/src/claude_smart/events/session_end.py`
- `plugin/src/claude_smart/events/stop.py`
- `plugin/src/claude_smart/events/user_prompt.py`
- `plugin/src/claude_smart/optimizer_assistant.py`
- `tests/conftest.py`
- README.md, ARCHITECTURE.md
- `plugin/dashboard/` 구조
- `plugin/skills/claude-smart/SKILL.md`
- `plugin/pyproject.toml`
- `tests/` 디렉토리 목록

### 미열람 항목 (참고)
- `plugin/scripts/*.sh` — 설치·서비스 스크립트
- `plugin/src/claude_smart/stall_banner.py`
- `plugin/src/claude_smart/publish.py` 의 호출 흐름 endpoint
- `plugin/dashboard/` 의 React 컴포넌트
- 개별 테스트 케이스
- reflexio 본체 (별도 패키지)
- CHANGELOG.md (존재 여부 미확인)

## 부록 B: 검토 방법

- 모든 자료는 `https://raw.githubusercontent.com/ReflexioAI/claude-smart/main/...` 에서 가져온 main 브랜치 기준
- 런타임 실행, 설치, 동작 확인은 하지 않음 (정적 분석만)
- 보안 검토는 사용자 요청에 따라 범위 외 (다만 코드 중 눈에 띈 항목은 5장에 메모)
