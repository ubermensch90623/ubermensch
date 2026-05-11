# Session End — 상태 저장 의식

> 세션 끝낼 때 마지막 메시지로 던짐. Claude가 vault에 이 세션 결과를 모두 박아둠.
> Custom Instructions가 자동으로 처리하지만, "꼭 저장됐는지" 확인하고 싶을 때 사용.

---

세션 종료. 다음을 모두 vault에 영구 저장하고 한 줄씩 보고해줘:

1. **`inbox/session-bridge.md` 완전히 덮어쓰기**
   - Last Session Summary: 이번 세션 핵심 3줄
   - Open Threads: 미완 사고/결정/질문
   - Decisions Made: 이번 세션 결정들의 [[wikilink]]
   - Actions Added: 이번 세션 추가 액션 개수
   - Files Created/Modified: 모든 변경 파일 [[wikilink]]
   - frontmatter `updated:` 필드에 현재 시각

2. **`inbox/decisions.md`** — 이번 세션 결정이 아직 안 들어갔다면 지금 append. 각 결정에 프로젝트 태그 포함

3. **`inbox/action-tracker.md`** — 이번 세션 액션 모두 추가됐는지 확인. 미완료된 액션은 Open Actions에

4. **모든 새 파일 생성 확인** — notes/, ideas/, projects/에 만든 파일이 실제로 디스크에 있는지

다 끝나면:
- 다음 세션이 이 다리(session-bridge)를 받고 시작할 수 있는지 자체 검증
- "🌙 session bridged. N개 결정 / M개 액션 / K개 노트 저장. 다음 세션 시 [[session-bridge]]를 자동 읽음." 한 줄 보고
