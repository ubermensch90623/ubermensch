# decisions

Non-obvious choices and why. Append only. Date each note.

---

## 2026-04-12 — memory system is file-based, not MCP/vector
- Chose plain markdown in `memory/` instead of installing gbrain as MCP.
- Why: (1) no API keys needed, (2) avoids the prompt-injection surface the
  gbrain review in `reviews/gbrain.md` flagged, (3) scope was "fix session
  amnesia only," not "replicate gbrain."
- Source: user asked for minimum viable upgrade after reading gbrain review.

## 2026-04-12 — memory protocol is hook-enforced, not discipline-based
- Added `SessionStart` and `Stop` hooks in `.claude/settings.json`.
  - `SessionStart`: auto-injects `memory/README.md` so the index is always
    in context without Claude having to remember to Read it.
  - `Stop`: on the first stop of each cycle, blocks with a `decision:block`
    + reason telling Claude to review the session for memory-worthy notes.
    Uses `stop_hook_active` guard to prevent loops — second stop passes
    through silently.
- Why: user explicitly rejected the "relies on Claude's discipline"
  framing. Hooks are harness-executed, not model-executed, so they fire
  regardless of whether the model remembers the protocol.
- Source: user, "자동으로 발동되는 방식을 원한다고".
