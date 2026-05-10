# Windows 단축키 치트시트

## 필수 단축키 (기본)

| 단축키 | 기능 |
|---|---|
| `Ctrl+P` | Command Palette (가장 중요. 모든 명령 검색) |
| `Ctrl+O` | Quick Switcher (파일 빠른 열기) |
| `Ctrl+N` | 새 노트 |
| `Ctrl+E` | 편집/미리보기 전환 |
| `Ctrl+G` | Graph View |
| `Ctrl+,` | Settings |
| `Ctrl+Shift+F` | Vault 전체 검색 |
| `Ctrl+F` | 현재 파일 내 검색 |
| `Ctrl+H` | 현재 파일 찾기/바꾸기 |
| `Alt+←` / `Alt+→` | 뒤로/앞으로 (탭 히스토리) |
| `Ctrl+W` | 현재 탭 닫기 |
| `Ctrl+Shift+T` | 닫은 탭 복원 |
| `Ctrl+Tab` | 다음 탭 |

## 편집 단축키

| 단축키 | 기능 |
|---|---|
| `[[` | 위키링크 자동완성 시작 |
| `Ctrl+B` | **굵게** |
| `Ctrl+I` | *기울임* |
| `Ctrl+K` | 링크 삽입 |
| `Ctrl+L` | 라인 선택 |
| `Ctrl+/` | 코멘트 토글 |
| `Ctrl+]` / `Ctrl+[` | 들여쓰기/내어쓰기 |
| `Ctrl+Shift+K` | 라인 삭제 |
| `Alt+↑` / `Alt+↓` | 라인 위/아래 이동 |
| `Ctrl+D` | 다음 같은 단어 선택 (multi-cursor) |

## 뷰/네비게이션

| 단축키 | 기능 |
|---|---|
| `Ctrl+\` | 사이드바 토글 (왼쪽) |
| `Ctrl+Shift+\` | 사이드바 토글 (오른쪽) |
| `Ctrl+클릭` (링크) | 새 탭에서 열기 |
| `Ctrl+Shift+클릭` (링크) | 옆 패널에서 열기 |
| `Ctrl+Enter` (Quick Switcher 안) | 옆 패널에서 열기 |
| `Ctrl+1~9` | 헤더 레벨 1~6 (편집 모드) |

## Daily Note / Periodic Notes

| 단축키 | 기능 |
|---|---|
| (커스텀) `Ctrl+Shift+D` | 오늘 Daily Note 열기 (Settings → Hotkeys에서 바인딩 필요) |
| (커스텀) `Ctrl+Shift+W` | 이번 주 Weekly Note (Periodic Notes 플러그인) |

## Templater (플러그인)

| 단축키 | 기능 |
|---|---|
| `Ctrl+T` (커스텀) | "Open Templater Modal" — 템플릿 선택해서 삽입 |
| `Ctrl+Shift+T` (커스텀) | "Insert Template" — 자주 쓰는 템플릿 |

> Templater 단축키는 Settings → Hotkeys → Templater에서 바인딩.

## Excalidraw (플러그인)

| 단축키 | 기능 |
|---|---|
| (커스텀) `Ctrl+Shift+E` | 새 Excalidraw 캔버스 |
| Excalidraw 안: `1~9` | 도구 변경 (선택/사각형/원 등) |

## Web Clipper (브라우저 확장)

| 단축키 | 기능 |
|---|---|
| `Alt+Shift+O` | Web Clipper 열기 (현재 페이지 캡처) |
| `Alt+Shift+H` | Highlighter 모드 토글 |

> 브라우저별 확장 설정에서 단축키 바인딩 가능.

## Claude Code (터미널)

| 단축키 | 기능 |
|---|---|
| `Ctrl+C` (한 번) | 입력 취소 |
| `Ctrl+C` (두 번) | 종료 |
| `Esc` | 현재 작업 중단 |
| `Shift+Tab` | 모드 전환 (plan/normal) |
| `/` | 슬래시 명령 |
| `@` | 파일 첨부 |

## 추천 커스텀 바인딩

Settings → Hotkeys에서 다음을 추가 권장:

| 명령 | 추천 키 | 이유 |
|---|---|---|
| Open today's daily note | `Ctrl+Shift+D` | 매일 1번 이상 누름 |
| Templater: Open template modal | `Ctrl+T` | 노트 종류 빠른 선택 |
| Toggle Reading view | `Ctrl+E` (기본) | 자주 전환 |
| Toggle Edit view | (기본) | |
| Open graph view | `Ctrl+G` (기본) | |
| Open quick switcher | `Ctrl+O` (기본) | |
| Show debug info | (선택) | 트러블슈팅용 |

## 워크플로우 단축키 흐름

### 글 읽고 정리하는 흐름
1. 브라우저에서 `Alt+Shift+O` → Web Clipper로 vault에 캡처
2. Obsidian에서 `Ctrl+O` → 방금 캡처한 파일 열기
3. `Ctrl+E` → 읽기 모드로 전환하여 빠르게 훑기
4. 핵심 발견 시 `[[ ` 입력하여 관련 노트와 연결
5. 가치 있으면 → 파일을 `notes/`로 이동 (`Ctrl+P` → "Move file")

### Claude와 대화하면서 일하는 흐름
1. 터미널에서 `claude` 실행
2. `/mcp` 로 vault MCP 연결 확인
3. 질문 입력 — Custom Instructions 덕에 자동 vault 검색
4. Claude가 새 노트 작성하면 Obsidian에서 `Ctrl+P` → "Reload app without saving" 또는 자동 새로고침

### Daily Brief 실행 흐름
1. Claude Code에서 `prompts/daily-brief.md` 내용 붙여넣기
2. 산출물이 `inbox/brief-{date}.md`로 자동 저장
3. Obsidian에서 `Ctrl+O` → `brief-` 검색 → 오늘 자 열기
4. 읽고 가치 있는 노트는 `ideas/`로 이동
