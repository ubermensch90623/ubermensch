# Obsidian × Claude Desktop × HTML 퀴즈 워크플로 — Windows 설치 가이드

> "노트로 퀴즈 만들어줘"가 한 줄로 끝나게 만드는 풀세트 설치.
> 소요 시간 약 **10~15분**.

---

## 무엇을 설치하는가

```
┌──────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│  Obsidian Vault  │ ←→ │  Claude Desktop     │ ←→ │  당신 (대화)     │
│  (Markdown 노트) │    │  + MCP 서버 2개     │    │                  │
└──────────────────┘    └─────────────────────┘    └──────────────────┘
        ↑                       │
        │   퀴즈 .html 저장 ←───┘
```

- **filesystem MCP** — Claude가 vault 폴더를 직접 읽고 `.html`을 씀
- **Obsidian Local REST API + MCP wrapper** *(선택)* — Obsidian 내부 검색·링크·태그까지 활용
- **prompt 템플릿 + 샘플 퀴즈 `.html`** — vault에 바로 떨어뜨려 쓸 자료

---

## 0. 사전 준비물

| 도구 | 확인 명령 (PowerShell) | 없으면 |
|---|---|---|
| Windows 10/11 | `winver` | — |
| Claude Desktop | 작업표시줄에서 실행 확인 | https://claude.ai/download |
| Obsidian | 작업표시줄에서 실행 확인 | https://obsidian.md |
| Node.js 20+ | `node -v` | `winget install OpenJS.NodeJS.LTS` |
| (선택) Python 3.11+ | `python --version` | `winget install Python.Python.3.12` |

**경로 메모해두기** — vault의 절대 경로 (예: `C:\Users\Daniel\Documents\ObsidianVault`). 이후 단계에서 여러 번 씁니다.

---

## 1. Obsidian "Local REST API" 플러그인 설치 *(MCP wrapper용)*

1. Obsidian 열기 → **Settings (Ctrl+,)** → **Community plugins** → **Turn on community plugins** 클릭 (한 번만)
2. **Browse** → "**Local REST API**" 검색 → 설치 → **Enable**
3. 플러그인 설정 패널 열어서 표시되는 **API Key**를 복사해두기 (예: `abc123def456...`)
4. **Encrypted (HTTPS) Server Port** = `27124`, **Non-encrypted (HTTP) Server Port** = `27123` 확인 (기본값 그대로 OK)

> 이 플러그인이 vault를 `https://127.0.0.1:27124`에서 로컬 API로 노출합니다. 외부엔 안 나갑니다.

---

## 2. MCP 서버 2개 설치

### 2-1. filesystem MCP (필수)

PowerShell에서 한 번 실행해 캐시 (실제 등록은 4번에서):

```powershell
npx -y @modelcontextprotocol/server-filesystem --help
```

> 처음 실행 시 패키지를 받느라 1~2분 걸립니다. 캐시되고 나면 Claude Desktop이 빠르게 띄웁니다.

### 2-2. Obsidian MCP wrapper (선택)

```powershell
# Python uvx 경로 (권장)
pip install uv
uvx --help

# 또는 Node 경로
npx -y mcp-obsidian --help
```

> `mcp-obsidian` 패키지 이름은 커뮤니티 버전이 여럿이라 시점에 따라 다를 수 있습니다. 본 가이드는 **filesystem MCP만으로도 충분히 작동**하도록 설계됐습니다. Obsidian MCP는 검색·태그·백링크가 필요해질 때 추가하세요.

---

## 3. `claude_desktop_config.json` 작성

1. **Win+R** → `%APPDATA%\Claude` → Enter
2. `claude_desktop_config.json` 파일 열기 (없으면 새로 만들기)
3. 본 저장소의 [`claude_desktop_config.example.json`](./claude_desktop_config.example.json)을 참고해 작성
4. 두 군데 치환:
   - `C:\\Users\\YOU\\Documents\\ObsidianVault` → 실제 vault 절대 경로 (역슬래시는 `\\`로 이스케이프)
   - `YOUR_OBSIDIAN_API_KEY_HERE` → 1번 단계에서 복사한 키

> **주의** — JSON이므로 마지막 항목 뒤에 쉼표 금지, 백슬래시는 `\\`로.

---

## 4. Claude Desktop 재시작 → 연결 확인

1. Claude Desktop 트레이 아이콘 우클릭 → **Quit** (완전 종료)
2. 다시 실행
3. 새 채팅 열고 입력창 좌측 하단의 **🔌 (플러그 아이콘)** 누르기 — `filesystem` (그리고 옵션으로 `obsidian`) 서버가 떠 있으면 성공
4. 테스트 한 줄:
   > vault 루트의 파일 목록을 보여줘

이게 작동하면 설치 끝.

---

## 5. 퀴즈 워크플로 — vault에 자료 넣기

본 저장소의 install 폴더에서 vault로 복사:

| 파일 | vault 내 위치 | 용도 |
|---|---|---|
| `quiz-prompt.md` | `Vault\Templates\quiz-prompt.md` | 매번 쓰는 프롬프트 본문 |
| `quiz-template.html` | `Vault\AI\templates\quiz-template.html` | Claude가 채워 넣을 빈 스켈레톤 |
| `sample-econ-quiz.html` | `Vault\AI\quizzes\sample-econ-quiz.html` | 완성된 참조용 (지금 바로 열어볼 수 있음) |

`AI/`와 `Templates/` 폴더가 없으면 Obsidian에서 우클릭 → New folder로 만듭니다.

---

## 6. 실전 사용

### 퀴즈 만들기

Claude Desktop에서:

```
@Vault\Macro\week-3.md 의 내용을 보고
Vault\Templates\quiz-prompt.md 의 형식을 따라
Vault\AI\quizzes\macro-week3-quiz.html 로 저장해줘.
```

> Claude가 `filesystem` MCP로 노트를 읽고 → 인터랙티브 HTML 퀴즈를 생성 → 지정 경로에 저장.

### 퀴즈 풀기

Obsidian에서 `Vault\AI\quizzes\macro-week3-quiz.html` 클릭 → 단축키 **`Ctrl+Shift+;`** (Open in default app) → 브라우저에서 풂.

### 결과 보관

퀴즈 끝나면 "Copy results JSON" 버튼이 나옵니다. JSON을 새 노트에 붙여넣어 `Vault\AI\results\` 폴더에 저장하면, Obsidian의 Dataview 플러그인으로 점수 추이도 추적 가능합니다.

---

## 문제 해결

| 증상 | 해결 |
|---|---|
| Claude Desktop이 MCP 서버를 "failed" 표시 | 로그 확인: `%APPDATA%\Claude\logs\mcp*.log` |
| `npx` 명령을 찾을 수 없음 | PowerShell 재시작 또는 Node.js 재설치 |
| vault 경로에 한글 포함 시 깨짐 | 절대 경로에 한글이 있으면 JSON에 그대로 두되, `\\`만 이스케이프 |
| Obsidian REST API 연결 실패 | 플러그인 활성화 여부 + 포트 27124 충돌 여부 확인 |
| 퀴즈 .html이 깨져 보임 | 단일 파일에 모든 CSS/JS inline 되어 있는지 확인 (Claude에 다시 "inline 처리" 요청) |

---

## 보안 메모

- `claude_desktop_config.json`은 평문 — API 키 들어 있음. **git에 커밋 금지**.
- Obsidian Local REST API는 기본적으로 localhost 바인딩 (외부 노출 X).
- filesystem MCP는 설정에 적은 경로만 접근 가능 — vault 외 다른 폴더는 보이지 않음.
