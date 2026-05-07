---
date: 2026-05-06
type: log
tags: [log, audit]
ai-first: true
---

## For future Claude

이 노트는 2026-05-06에 저장된 볼트 감사 기록이다. append-only. 의미 있는 쓰기마다 한 줄을 추가한다.
형식: `YYYY-MM-DD HH:MM | actor | summary`. actor는 `user`, `claude`, 또는 명명된 에이전트.

# 볼트 로그

<!-- 최신 항목이 위. -->

- 2026-05-07 00:35 | claude | scripts/fetch-claude-ai.py 추가 — sessionKey 쿠키로 claude.ai 내부 API 직접 호출해 대화 가져오기
- 2026-05-07 00:30 | claude | Stop hook 등록 (auto-import-sessions.sh) — 이제 세션 종료마다 자동 임포트
- 2026-05-07 00:25 | claude | 현재 세션 강제 임포트 — Sessions/에 3건 (5/5 + 5/6 초반 + 현재) 모두 들어감
- 2026-05-07 00:00 | claude | 과거 대화 임포터 2개 추가, Sessions/에 5/5+5/6 Claude Code 세션 2건 임포트
- 2026-05-06 00:20 | claude | scripts/quick-mcp-tunnel.sh 추가 (claude.ai 웹용 원격 MCP 터널)
- 2026-05-06 00:10 | claude | 한글 번역 + SYNC.md 추가
- 2026-05-06 00:00 | claude | 볼트 스켈레톤 초기화
