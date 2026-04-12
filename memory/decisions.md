# decisions

Non-obvious choices and why. Append only. Date each note.

---

## 2026-04-12 — memory system is file-based, not MCP/vector
- Chose plain markdown in `memory/` instead of installing gbrain as MCP.
- Why: (1) no API keys needed, (2) avoids the prompt-injection surface the
  gbrain review in `reviews/gbrain.md` flagged, (3) scope was "fix session
  amnesia only," not "replicate gbrain."
- Source: user asked for minimum viable upgrade after reading gbrain review.
