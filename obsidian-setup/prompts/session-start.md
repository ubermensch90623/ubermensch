# Session Start — 컨텍스트 부팅 프롬프트

> 새 세션 열고 첫 메시지로 던지면 Claude가 vault에서 컨텍스트를 명시적으로 로드함.
> Custom Instructions가 자동으로 처리해주지만, 신뢰가 안 가거나 검증하고 싶을 때 사용.

---

세션 시작. 다음을 순서대로 실행하고 보고해줘:

1. `CLAUDE.md`를 읽고 내가 누구이고 뭘 하는지 요약 (3줄)
2. `inbox/session-bridge.md`를 읽고 직전 세션의 미완 thread를 나열
3. `inbox/action-tracker.md`의 Open Actions에서 가장 시급한 3개를 우선순위 순으로
4. `inbox/decisions.md`의 최신 3개 결정을 한 줄 요약씩

위 4개를 다 출력한 후, **이번 세션에서 무엇을 하면 좋을지** 너의 추천 1개를 제시.

만약 어느 파일이라도 못 읽으면 즉시 멈추고 "MCP 연결 실패 / 파일 미존재" 등 정확한 원인을 말할 것. 추측 답변 금지.
