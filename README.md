# Insane Search

**Claude Code의 WebSearch/WebFetch를 강화하는 MCP 플러그인.**

트위터는 402, 레딧은 봇 차단, 스택오버플로우는 도메인 블락, 네이버 블로그는
iframe 감옥 — Claude Code가 기본으로 못 가져오는 사이트들을 플랫폼별 우회
전략으로 해결합니다. API 키도, 인증도, 별도 설정도 필요 없습니다.

## 왜 필요한가

- "트위터 반응 좀 봐줘" 했는데 402 뜨고 끝남
- 레딧 데이터 필요할 때마다 브라우저 열어서 복붙하고 있음
- API 키 발급, OAuth 설정, 환경변수 세팅 — 그런 거 하기 싫음
- 네이버 블로그, 긱뉴스, 클리앙도 AI로 그냥 읽고 싶음

## 지원 플랫폼

| 플랫폼          | 우회 전략                                                           |
| --------------- | -------------------------------------------------------------------- |
| Twitter / X     | `cdn.syndication.twimg.com` 공식 위젯 JSON + nitter 폴백             |
| Reddit          | `www.reddit.com/comments/<id>.json` + 데스크톱 UA 위장               |
| StackOverflow   | `api.stackexchange.com` 무인증 API (IP 당 하루 300 req)              |
| Naver Blog      | `m.blog.naver.com` / `PostView.naver` 로 iframe 풀기                 |
| 그 외           | 데스크톱 크롬 헤더로 GET + HTML → Markdown 변환                      |

## 설치

```bash
pip install -e .
```

또는 uv:

```bash
uv pip install -e .
```

## Claude Code 에 등록

```bash
claude mcp add insane-search -- insane-search
```

또는 프로젝트 루트의 `.mcp.json` 에 직접 넣어도 된다:

```json
{
  "mcpServers": {
    "insane-search": {
      "command": "insane-search"
    }
  }
}
```

등록하면 Claude Code 에서 다음 도구를 쓸 수 있다:

- `insane_fetch(url)` — URL 을 플랫폼 우회 전략으로 가져와 Markdown 으로 반환
- `insane_search(query, platform?, limit?)` — 무인증 DuckDuckGo 기반 웹 검색
- `insane_detect(url)` — 주어진 URL 이 어떤 전략을 타는지 미리 확인 (디버그용)

## 예시

```
> 이 트윗 좀 요약해줘: https://x.com/sama/status/1800000000000000000
(Claude 가 insane_fetch 호출 → syndication.twimg.com 에서 직접 가져옴)

> /r/LocalLLaMA 에서 올해 가장 많이 언급된 벤치마크가 뭐야?
(Claude 가 insane_search 로 서브레딧 탐색 → insane_fetch 로 각 포스트 가져옴)

> 이 SO 답변 한국어로 설명해줘: https://stackoverflow.com/questions/…
(Claude 가 Stack Exchange API 로 질문 + 답변을 한번에 가져옴)

> 이 네이버 블로그 본문만 보여줘: https://blog.naver.com/someblog/223…
(iframe 을 풀어서 본문만 깔끔하게 반환)
```

## 개발

```bash
pip install -e ".[dev]"
pytest
```

## 설계 원칙

1. **인증 금지** — API 키, OAuth, 쿠키 모두 쓰지 않는다. 설정 없이 그냥 돌아야 한다.
2. **공개 엔드포인트만** — 각 사이트가 이미 공개해둔 임베드/JSON/모바일 뷰를 사용한다.
3. **품질 우선** — 원본 HTML 을 던지는 대신 항상 깨끗한 Markdown 으로 정리해서 반환한다.
4. **폴백** — 주 경로가 막히면 보조 경로 (nitter, old.reddit) 로 재시도.

## 라이선스

MIT
