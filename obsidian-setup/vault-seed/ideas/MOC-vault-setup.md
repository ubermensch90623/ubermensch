---
aliases:
  - vault setup MOC
  - setup hub
  - MOC vault
created: 2026-05-11
tags:
  - moc
  - status/budding
---

# MOC — Vault Setup & Claude Integration

> 이 vault의 셋업과 Claude 통합에 관한 모든 사고의 주제 허브.
> 다른 idea 노트들의 진입점. Graph View에서 이 노트가 가장 큰 노드여야 한다.

## 핵심 질문

- vault가 어떻게 인지 증폭기가 되는가? → [[cognition-vs-organization]]
- 어떤 아키텍처로 작동하는가? → [[4-layer-pkm-architecture]]
- 새 세션이 이전 세션과 어떻게 이어지는가? → [[session-bridge-mechanism]]
- Claude에게 본인 컨텍스트는 어떻게 전달하는가? → [[two-claude-md-pattern]]
- 왜 폴더가 5개만 있어야 하는가? → [[folder-simplicity-principle]]
- 어떻게 링크가 끊기지 않게 유지하는가? → [[linkrot-prevention]]

## 핵심 노트 (자동 수집)

```dataview
LIST
FROM #permanent
WHERE contains(file.outlinks, this.file.link) OR contains(this.file.outlinks, file.link)
SORT file.mtime DESC
```

## 외부 자료

- Nainsi Dwivedi — "Your Obsidian Vault Is Probably Dead"
- Fraser Cottrell — "Claude + Obsidian = A true AI employee"
- CyrilXBT — "Build an Obsidian Knowledge Vault That Gets Smarter Every Day"
- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) — Obsidian CEO 작품
- [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) — Karpathy LLM Wiki 패턴

## 핵심 결정사항 (백링크)

- [[decisions#2026-05-11 — PKM 방법론 = Zettelkasten 사고 + CyrilXBT 5폴더]]
- [[decisions#2026-05-11 — Seamless 메커니즘 = session-bridge.md + SESSION PROTOCOL]]
- [[decisions#2026-05-11 — Cowork = Claude Desktop의 기능]]
- 전체 결정 로그: [[decisions]]

## 미해결 질문

- AgriciDaniel 자동 wiki 시스템을 언제 도입할까? (1~2주 미니멀 후?)
- Web Clipper AI Interpreter의 prompt syntax는 실측에서 작동하는가?
- 멀티 디바이스 동기화 — Google Drive로 충분한가, Obsidian Sync로 갈아탈까?

## 인접 주제 (다른 MOC들)

<!-- vault가 자라면서 다른 MOC가 생기면 여기 추가 -->
- (예정) [[MOC-cognitive-routines]] — daily brief / weekly synthesis 운영 패턴
- (예정) [[MOC-capture-pipeline]] — Web Clipper + N8N + Whisper 통합
