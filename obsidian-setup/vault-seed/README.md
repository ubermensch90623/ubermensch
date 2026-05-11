# vault-seed — 오늘 세션의 영구 기억

> 2026-05-11 세션에서 발생한 모든 결정/액션/사고를 **vault에 영구 저장될 형태**로 만든 시드.
> 로컬 PC에서 vault 셋업할 때 이 파일들을 vault에 복사하면 **첫날부터 두꺼운 컨텍스트와 살아있는 Graph View**를 갖춘 상태로 시작.

## 사용법

체크리스트 5번에서 `inbox-init/` 대신 (또는 추가로) 이 폴더를 복사:

```powershell
$KIT = "$env:USERPROFILE\ubermensch\obsidian-setup"
$VAULT = "$env:USERPROFILE\Google Drive\Vault\brain"

# inbox-init은 텅 빈 헤더만 — vault-seed는 실제 내용 포함
robocopy "$KIT\vault-seed\inbox" "$VAULT\inbox"
robocopy "$KIT\vault-seed\ideas" "$VAULT\ideas"
```

`inbox-init/`(빈 템플릿)과 `vault-seed/`(오늘 세션 내용) 중 하나만 선택. 후자 권장 — 이미 결정/액션/idea 노트들이 들어있어 Graph View가 첫날부터 살아있음.

## 포함된 것

### inbox/

- `decisions.md` — 오늘 내려진 결정 15개 (Cowork Global Instructions부터 PKM 방법론 선택까지)
- `action-tracker.md` — 로컬 PC에서 사용자가 실행해야 할 12개 액션
- `session-bridge.md` — 오늘 세션 전체 요약. **다음 세션이 첫 read로 가져가는 단기 기억**

### ideas/

6개의 영구 노트. 서로 `[[wikilink]]`로 촘촘히 연결됨. Graph View에서 클러스터를 형성:

- `MOC-vault-setup.md` — 주제 허브. 모든 idea 노트의 진입점
- `4-layer-pkm-architecture.md` — Capture/Pipeline/Memory/Intelligence
- `cognition-vs-organization.md` — Vault의 진짜 목적
- `session-bridge-mechanism.md` — Seamless의 핵심 메커니즘
- `two-claude-md-pattern.md` — 두 CLAUDE.md 파일의 분리
- `folder-simplicity-principle.md` — 복잡한 폴더 구조가 무너지는 이유

## 다음 세션이 이걸 읽었을 때

session-bridge.md가 첫 read로 들어가면, 새 Claude 세션이 즉시:
- "어제 셋업 키트를 만들었고, Cowork 검증까지 완료됨"
- "현재 사용자는 로컬 PC 셋업 대기 중"
- "다음 단계: PC에서 체크리스트 따라 셋업 → 13.5 Seamless 테스트"

이걸 자동으로 인지하고 시작.
