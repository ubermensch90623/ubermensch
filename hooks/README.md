# hooks/

종환 윈도우 PC `Desktop/.claude/hooks/`에 박을 자가진화 hook 모음.

## 등록

`C:\Users\윤상택\Desktop\.claude\settings.json`(또는 프로젝트 settings)에:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python C:\\Users\\윤상택\\Desktop\\.claude\\hooks\\auto_morning_desktop_popup.py"
          }
        ]
      }
    ]
  }
}
```

## 목록

| 파일 | 트리거 | 역할 | 자가진화 출처 |
|---|---|---|---|
| `auto_morning_desktop_popup.py` | Stop hook (새벽 catch-up 종료 시) | PowerShell MessageBox 띄워서 종환 1클릭 → MVP 자동 오픈. 발견 채널 결함 직격 | 제안 1 (severity 5, P0, 2026-05-24) |
| `hermes_mvp_vault_sync.js` | MVP `<script>` 한 줄 + 우상단 [↓ Vault Export] 버튼 | localStorage 전체 → `HERMES_YYYY-MM-DD.md` export. 21시 이후 1회 자동 prompt. 데이터 증발 차단 | 제안 5 (severity 5, 5/23 carry-over) |
| `jaso_validator.py` | Stop hook (자소서 .md mtime 변동 시) | 자소서 5단계 자동 검증 (글자수·금지어 23종·자격증/경력 누락·소제목 1개 룰). vault `_SSOT/자소서_피드백_누적.md`에 ✅/⚠️ append | 제안 3 (severity 4, 2026-05-24) |

## 동작 조건

`auto_morning_desktop_popup.py`:

- **시각 윈도우**: 04:30~07:00 KST (그 외 skip)
- **하루 1회**: `auto_morning_ack.log` 확인, 중복 발화 skip
- **catch-up 종료 신호**: Stop hook payload의 `stop_reason` + transcript에 `catch-up 종료` 패턴
- **P0 추출 소스**: `vault\_SSOT\hermes_daily\YYYY-MM-DD*.md` 첫 P0 라인
- **OK 클릭 시**: `hermes_mvp.html`을 OS 기본 브라우저로 자동 오픈 + ack 로그
- **Cancel/timeout(10분)**: dismiss 로그 → 다음 cycle 강도 ↑

## 환경 변수 (선택)

| 변수 | 기본값 |
|---|---|
| `HERMES_LOG_DIR` | `C:\Users\윤상택\.hermes\logs` |
| `HERMES_VAULT_DAILY` | `C:\Users\윤상택\Desktop\작업\ObsidianVault\_SSOT\hermes_daily` |
| `HERMES_MVP_PATH` | `C:\Users\윤상택\Desktop\HERMES\hermes_mvp.html` |

## 검증 (도입 후 3일)

`auto_morning_ack.log`:
- 3일 연속 OK = 발견 채널 복구
- 3일 연속 DISMISS = 시각 윈도우 조정 (`ALLOWED_HOUR_RANGE`) 또는 메시지 강도 ↑
- 3일 연속 fire 0건 = catch-up 종료 신호 조건 점검 (transcript 패턴)
