# Obsidian Web Clipper — 자동 Capture 레이어

> Readwise($8/월) 무료 대체. 클립 한 번에 Claude가 즉시 요약/태그 변환.
> 4-layer 아키텍처의 **Capture 레이어**를 완성한다.

## 설치

| 브라우저 | 스토어 |
|---|---|
| Chrome / Brave / Arc / Edge | [Chrome Web Store](https://chromewebstore.google.com/) — "Obsidian Web Clipper" |
| Firefox | [Firefox Add-ons](https://addons.mozilla.org/) — "Web Clipper for Obsidian" |
| Safari (macOS/iOS) | App Store |
| 공식 GitHub | https://github.com/obsidianmd/obsidian-clipper |

설치 후 브라우저 우상단 확장 아이콘 고정 권장.

## 기본 설정

확장 아이콘 우클릭 → **Options** 또는 설정 아이콘.

### General 탭
- **Vault**: `brain` (Obsidian이 인식하는 vault 이름)
- **Default folder**: `inbox/`
- **Default filename**: `{{date|date:"YYYY-MM-DD"}}-{{title|slugify}}`
- **Behavior**: "Create new note"

### Properties (Frontmatter) 기본값
```yaml
source: {{url}}
author: {{author}}
published: {{published}}
clipped: {{date|date:"YYYY-MM-DD"}}
tags:
  - literature
  - src/clipper
```

## 5가지 변수 종류

| 종류 | 예시 | 용도 |
|---|---|---|
| **Preset** | `{{title}}`, `{{url}}`, `{{content}}`, `{{description}}`, `{{author}}`, `{{published}}`, `{{date}}`, `{{highlights}}` | 기본 메타데이터 |
| **Prompt** (AI) | `{{"이 글의 핵심 3가지를 한국어 불릿으로"}}` | AI Interpreter가 LLM으로 변환 |
| **Meta** | `{{meta:author}}`, `{{meta:og:image}}` | HTML 메타태그 직접 추출 |
| **Selector** | `{{selector:.article-body}}`, `{{selector:#main}}` | CSS 선택자로 특정 영역 |
| **Schema.org** | `{{schema:NewsArticle:headline}}`, `{{schema:Recipe:ingredients}}` | 구조화된 데이터 |

## Filters (변수 후처리)

변수 뒤에 `|`로 체이닝:

| Filter | 예시 | 효과 |
|---|---|---|
| `slugify` | `{{title|slugify}}` | "Hello World!" → "hello-world" |
| `markdown` | `{{content|markdown}}` | HTML → Markdown |
| `lower` / `upper` | `{{title|lower}}` | 대소문자 |
| `date:"format"` | `{{date|date:"YYYY-MM-DD"}}` | 날짜 포맷 |
| `join:", "` | `{{tags|join:", "}}` | 배열 → 문자열 |
| `truncate:200` | `{{content|truncate:200}}` | 200자로 자르기 |
| `replace:"a","b"` | `{{title|replace:"&","and"}}` | 치환 |

체이닝: `{{content|markdown|truncate:500}}`

## ★ AI Interpreter — Anthropic API 키 셋업 (단계별)

> AI Interpreter가 활성화되면 클립 순간에 Claude가 글을 읽고 요약/태그/번역 등을 즉시 생성한다. 가장 강력한 기능.

### 1. Anthropic API 키 발급

1. [console.anthropic.com](https://console.anthropic.com) 접속
2. Sign up 또는 로그인 (Google/이메일)
3. 전화번호 인증 완료
4. 좌측 메뉴 → **API Keys** → **Create Key**
5. 키 이름: `obsidian-clipper` (식별용 — 나중에 어디서 쓰는지 알기 쉬움)
6. 생성된 `sk-ant-api03-...` 키를 **즉시 안전한 곳에 복사** (페이지 떠나면 다시 못 봄)
7. 1Password / Bitwarden / KeePass 등에 저장

### 2. 결제 수단 등록

1. 좌측 메뉴 → **Billing** → **Plans & Billing**
2. **Add credit card**
3. **Add credits**: 처음엔 $5~10 충전 권장 (이게 다 떨어지면 클립 안 됨)
4. **Auto-recharge** 옵션: 잔액이 일정 이하로 떨어지면 자동 충전 (선택)

### 3. 비용 한도 설정 (필수)

폭주 방지:
1. **Limits** 탭
2. **Monthly spend limit**: $10~20 (본인 사용량에 맞게)
3. **Email alerts**: 사용량 80% 시 알림 ON

### 4. Web Clipper에 키 등록

1. 확장 아이콘 우클릭 → **Options**
2. **Interpreter** 탭
3. **Enable interpreter**: ON
4. **Provider**: `Anthropic`
5. **Model** 선택:
   - **`claude-haiku-4-5`** — 빠르고 저렴 (글 1건 ~$0.005). 클립용 권장
   - **`claude-sonnet-4-6`** — 품질 우선 (글 1건 ~$0.02). 중요 자료용
6. **API Key**: 발급한 키 붙여넣기
7. **Save**
8. **Test connection** 버튼 → 성공 메시지 확인

### 5. Prompt 변수 활용 예시

템플릿에 다음을 그대로 넣으면 클립 시 자동 실행:

```markdown
## AI Summary
{{"이 글의 핵심 3가지를 한국어 불릿으로 (각 1줄)"}}

## Suggested Tags
{{"이 글에 적절한 태그 5개를 추천. 형식: #kebab-case, 공백으로 구분"}}

## Counter-argument
{{"이 글이 도전하는 통념과 그 근거를 1단락(3문장)"}}

## Strongest Rebuttal
{{"이 글의 핵심 주장에 대한 가장 강한 반론을 1단락"}}

## Actionable Steps
{{"이 글에서 내가 행동으로 옮길 수 있는 구체 단계 3개"}}
```

### 6. 비용 관리

- Haiku 4.5 기준: 평균 글 1건 약 $0.003~0.008
- 하루 10건 클립 = 약 $0.05/일 = 약 $1.5/월
- Console에서 Usage 탭으로 일/월 사용량 확인
- 매월 1일에 자동 리포트 이메일 받기 권장

### 7. 키 보안 (중요)

- ❌ 키를 vault 안에 평문 저장 금지 (CLAUDE.md 등에 절대 쓰지 말 것)
- ❌ Git 커밋에 키 포함 금지 → `.gitignore`로 확장 설정 폴더 제외
- ❌ 스크린샷에 노출 금지
- ✅ 브라우저 확장에 저장된 키는 동기화하지 않음 (그래서 안전)
- ✅ 분실/유출 시 Console에서 즉시 **Revoke** 후 재발급
- ✅ 정기적으로 (3~6개월) 키 로테이션 권장

## Smart Rules (도메인별 자동 템플릿)

특정 사이트에서 클립할 때 자동으로 다른 템플릿 적용:

| 도메인 패턴 | 템플릿 | 효과 |
|---|---|---|
| `*.twitter.com`, `*.x.com` | `twitter-thread.json` | 스레드 전체 캡처, 작성자 메타 |
| `*.youtube.com`, `youtu.be` | `youtube.json` | 자막 추출, 채널/조회수 |
| `*.github.com/*/README*` | `github-readme.json` | README 본문, 스타/언어 |
| `arxiv.org`, `*.nature.com` | `research-paper.json` | 초록, 저자, DOI |
| (그 외) | `default-article.json` | 기본 |

설정: Options → **Templates** → 각 템플릿의 **Triggers** 필드에 URL 패턴 입력.

이 키트의 `templates/webclipper-templates/`에 5개 JSON 제공 — Options → Templates → **Import**.

## Highlighter 모드

1. 글을 읽다가 단축키 `Alt+Shift+H` (커스텀) 또는 우클릭 메뉴
2. 형광펜처럼 텍스트 드래그하여 하이라이트
3. 여러 부분 하이라이트하면 자동 누적
4. 클립 버튼 한 번 → 하이라이트들이 `{{highlights}}` 변수로 vault에 저장

템플릿에 `## Highlights\n{{highlights}}` 추가하면 하이라이트만 따로 섹션화.

## 트러블슈팅

| 증상 | 해결 |
|---|---|
| 확장이 vault를 못 찾음 | Obsidian이 실행 중이어야 함. vault 이름 정확히 일치 |
| Interpreter "API key invalid" | 키 앞뒤 공백 제거, Console에서 키 활성 상태 확인 |
| 한글 깨짐 | properties type `text`로 명시 |
| 본문이 빈 채로 저장 | 사이트가 JS 렌더링. `{{selector:...}}`로 영역 직접 지정 |
| 클립 후 Obsidian이 새 노트를 안 보여줌 | Obsidian이 외부 파일 변경 감지하는지 확인 (자동 새로고침) |
| Interpreter가 느림 | Haiku 모델로 변경, 또는 Prompt 변수 개수 줄이기 |

## 권장 워크플로우

### 일일 클립 흐름
1. 글 읽다가 `Alt+Shift+O` → Web Clipper 열림
2. (옵션) Highlighter 모드로 핵심 문장 하이라이트
3. Smart Rules가 도메인 보고 템플릿 자동 적용
4. AI Interpreter가 요약/태그/반론 생성
5. Save → vault의 `inbox/2026-05-10-{slug}.md`에 저장
6. Obsidian에서 자동 감지하여 노트 표시

### 주간 정제 (15분, 월요일)
1. `inbox/`에서 지난 주 클립 훑어보기
2. 가치 있는 것 → `notes/`로 이동, `#literature` 태그
3. 영감 받은 것 → `ideas/{slug}.md`로 자기 언어로 재구성, `#permanent`
4. 가치 없는 것 → 삭제 (vault는 묘지가 아님)

## 참고 자료

- 공식: https://github.com/obsidianmd/obsidian-clipper
- 변수 문서: https://help.obsidian.md/web-clipper/variables
- 템플릿 문서: https://help.obsidian.md/web-clipper/templates
- 커뮤니티 템플릿: https://github.com/obsidian-community/web-clipper-templates
