# 큐레이션된 Obsidian GitHub 레포 20선

> 최근(2025~2026) 활발하게 관리되는 유용한 Obsidian 관련 레포 20개.
> 카테고리별로 정리. 별점/유용도는 필요할 때 추가.

## MCP / Claude 통합 (5)

### 1. [obsidianmd/obsidian-clipper](https://github.com/obsidianmd/obsidian-clipper)
공식 Web Clipper. Chrome/Firefox/Safari/Edge. AI Interpreter로 Claude 통합. 이 키트의 핵심 Capture 레이어.
- 셋업 가이드: `05-web-clipper.md`

### 2. [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) ⭐30k
Obsidian CEO Stephan Ango의 Claude Code 에이전트 스킬 팩. 5개 스킬(`obsidian-markdown`, `obsidian-bases`, `json-canvas`, `obsidian-cli`, `defuddle`). **이 키트의 필수 통합 레이어**.
- 설치: `/plugin marketplace add kepano/obsidian-skills`

### 3. [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
Karpathy LLM Wiki 패턴 기반 자동 wiki 시스템. `/wiki`, `ingest`, `/save`, `/autoresearch`, `lint the wiki` 명령. **풀스택 옵션**.
- 셋업 가이드: `06-agricidaniel-wiki.md`

### 4. [MarkusPfundstein/mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian)
가장 널리 쓰이는 Obsidian MCP 서버. Local REST API 기반. Claude Desktop/Code/Cursor에서 vault 직접 read/write.
- 설치: `npx -y mcp-obsidian` (mcp.json 설정)

### 5. [jacksteamdev/obsidian-mcp-tools](https://github.com/jacksteamdev/obsidian-mcp-tools)
시맨틱 검색 + Templater 프롬프트 통합 MCP. Local REST API보다 강력. 고급 사용자용.

## AI 플러그인 (3)

### 6. [brianpetro/obsidian-smart-connections](https://github.com/brianpetro/obsidian-smart-connections)
로컬 임베딩으로 의미 기반 노트 연결/채팅. **API 키 없이 작동** (zero-setup). Claude/Gemini/ChatGPT/Llama 3 모두 지원.
- 특히 vault가 커진 후(500+ 노트) 진가 발휘

### 7. [logancyang/obsidian-copilot](https://github.com/logancyang/obsidian-copilot)
"THE Copilot in Obsidian". Vault 전체 QA, 커스텀 프롬프트, 로컬 모델 지원. 가장 인기 있는 AI 플러그인.

### 8. [infiolab/infio-copilot](https://github.com/infiolab/infio-copilot)
Cursor IDE 스타일 자동완성 + 선택 노트 채팅. 글쓰기에 강함.

## 필수 플러그인 (3)

### 9. [SilentVoid13/Templater](https://github.com/SilentVoid13/Templater)
JS 실행 가능한 강력한 템플릿 엔진. 동적 변수, 시스템 명령, 사용자 프롬프트. **모든 vault의 필수 도구**.

### 10. [blacksmithgu/obsidian-dataview](https://github.com/blacksmithgu/obsidian-dataview)
Vault를 DB처럼 쿼리. SQL-like 문법. 대시보드, MOC, 자동 리스트 필수.

### 11. [iansinnott/obsidian-claude-code-mcp](https://github.com/iansinnott/obsidian-claude-code-mcp)
Claude Code ↔ Obsidian WebSocket 자동 연결. Claude Code 사용자라면 MarkusPfundstein 대안으로 고려.

## Zettelkasten / PKM 스타터 키트 (4)

### 12. [groepl/Obsidian-Zettelkasten-Starter-Kit](https://github.com/groepl/Obsidian-Zettelkasten-Starter-Kit)
가장 인기 있는 Zettelkasten 스타터. 폴더/태그/템플릿 모두 포함. **본 키트의 보완용**으로 참고 가치 있음.

### 13. [groepl/Obsidian-Templates](https://github.com/groepl/Obsidian-Templates)
groepl의 Zettelkasten 전용 Templater 스크립트. atomic note 생성, ID 관리 등.

### 14. [ballred/obsidian-claude-pkm](https://github.com/ballred/obsidian-claude-pkm)
**가장 유사한 키트**. Claude + Obsidian PKM 스타터. 가이드형 온보딩(이름/리뷰일/목표 묻고 자동 셋업).

### 15. [berteaux/obsidian-vault-template](https://github.com/berteaux/obsidian-vault-template)
Zettelkasten + PARA 하이브리드. 본 키트는 PARA 미사용이지만 비교 가치 있음.

## Templates / 스니펫 (2)

### 16. [juanchiparra/obsidian-dataview-custom](https://github.com/juanchiparra/obsidian-dataview-custom)
Dataview용 CSS 스니펫 모음. 테이블/리스트/태스크 시각화 개선. `.obsidian/snippets/`에 복사.

### 17. [dmscode/Obsidian-Templates](https://github.com/dmscode/Obsidian-Templates)
Dataview/Templater/QuickAdd 통합 템플릿 컬렉션. 중국어 주석이지만 코드는 만국 공통.

## Publish / Static Site (1)

### 18. [jackyzha0/quartz](https://github.com/jackyzha0/quartz) ⭐
"a fast, batteries-included static-site generator". Obsidian vault → 디지털 가든. Graph View, 백링크, 전문 검색 보존. **블로그/디지털 가든 시작점**.

## Awesome Lists / 디렉터리 (2)

### 19. [kmaasrud/awesome-obsidian](https://github.com/kmaasrud/awesome-obsidian)
큐레이션된 awesome 리스트. 플러그인/테마/리소스 종합.

### 20. [obsidianmd/obsidian-releases](https://github.com/obsidianmd/obsidian-releases)
공식 플러그인/테마 마스터 목록. JSON 파일로 모든 community 플러그인 메타데이터. **새 플러그인 발견 시 첫 확인 장소**.

---

## 부가 추천 (즉시 도입 가치)

이 20개 외에 즉시 가치 있는 것들:

| 이름 | 용도 |
|---|---|
| Calendar (liamcain) | Daily/Weekly notes 시각화 |
| Periodic Notes (liamcain) | Daily/Weekly/Monthly notes 통합 |
| Excalidraw | 다이어그램/마인드맵 |
| Style Settings | 테마 세부 커스터마이징 |
| Tag Wrangler | 태그 일괄 리네임/머지 |
| Advanced Tables | 마크다운 테이블 편집 강화 |
| Outliner | 불릿 노트 강화 |
| Kanban | 칸반 보드 (마크다운 백킹) |
| Tasks | 태스크 쿼리/필터 |
| Obsidian Git | 자동 git 백업 |

## 사용 추천 흐름

```
1주차: 필수 (Templater + Dataview + Obsidian Git + Web Clipper)
2주차: AI 1개 도입 (Smart Connections 또는 Copilot — 둘 다 X)
3주차: MCP 셋업 (MarkusPfundstein/mcp-obsidian)
4주차: 시각화 (Excalidraw + Calendar + Style Settings)
1개월+: 옵션 (AgriciDaniel for 자동 wiki, Quartz for publish)
```

## 레포 평가 기준

이 20개 선정 기준:
- ✅ 2025년 이후 활발한 커밋
- ✅ 명확한 README와 사용법
- ✅ 다른 도구와 잘 통합됨 (특히 Claude/MCP)
- ✅ 본 키트의 철학(인지 증폭, 마찰 0)과 정합
- ❌ 단순 토이 프로젝트는 제외
- ❌ Obsidian Sync 같은 유료 서비스 의존은 제외

## 더 찾고 싶다면

- [Obsidian Plugin Stats](https://www.obsidianstats.com) — 2750+ 플러그인 검색
- GitHub 토픽: [obsidian-plugin](https://github.com/topics/obsidian-plugin), [obsidian-vault](https://github.com/topics/obsidian-vault)
- Obsidian Forum의 Share & Showcase 카테고리
