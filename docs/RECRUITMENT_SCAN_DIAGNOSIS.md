# recruitment-scan SKILL 19일 정체 진단

자가진화 제안 6 (severity 5, P0, 2026-05-24 채택)
- **관찰**: 5/5~5/24 19일간 cron 미발화. 분신 catch-up 부재. 신규 D-day 채널 완전 사망. 학습 동기 trigger 부재의 직접 원인.

## 4가지 후보 P4 독립 검증

GD `scheduled-tasks/recruitment-scanner/SKILL.md`(7KB) 코드 직접 read + MEMORY.md cron 목록 대조 결과:

| # | 후보 | 검증 결과 | 비고 |
|---|---|---|---|
| 1 | SKILL.md 트리거 조건 오류 (lastRun 비교 bug) | ❌ 무죄 | SKILL 본문에 lastRun 비교 로직 자체가 없음. 매뉴얼/cron 호출 전제 |
| 2 | **cron schedule 미등록** | ✅ **확정 — root cause #1** | MEMORY.md (2026-05-24) cron 5개 목록: `ab8935cf9923 / vault-sync-15m / vault-ingest-daily / screen-monitor-ncs / gd-mirror-30m`. **recruitment-scan 없음** |
| 3 | 잡알리오/자소설닷컴 사이트 구조 변경 | ⚠️ 미확정 | 이 클라우드 환경에서 외부 fetch 차단. 우선 #2·#4 fix 후 cron 발화되면 검증 가능 |
| 4 | **분신 자동 catch-up 룰 부재** | ✅ **확정 — root cause #2** | SKILL.md 어디에도 "마지막 fire 시각 N일 초과 시 자동 강제 발화" 룰 없음. cron 죽으면 영구히 침묵 |

## 단일 패치 (cron + catch-up 동시)

### 1. cron 등록 (PowerShell, 종환 PC)

```powershell
hermes cron create `
  --name recruitment-scan-daily `
  --schedule "0 6 * * *" `
  --skill recruitment-scanner `
  --prompt "오늘 recruitment-scanner SKILL 실행. 신규 공고만 보고. 없으면 '신규 공고 없음' 1줄."

hermes cron list                                # recruitment-scan-daily 표시 확인
```

### 2. catch-up 룰 추가 (SKILL.md 본문 prepend)

`C:\Users\윤상택\Desktop\.claude\skills\recruitment-scanner\SKILL.md` 최상단 (frontmatter 직후) 추가:

```markdown
## 자동 catch-up 룰 (헌법 잠금)

매 호출 시 자체 self-check:

1. vault `_SSOT/recruitment_scan_YYYY-MM-DD.md` 마지막 파일 mtime 확인
2. 마지막 fire 시각 > 3일이면 **catch-up 모드**:
   - 누락 기간 동안의 신규 공고 일괄 백필
   - 마감일 지난 공고는 표시만 ("3일 전 마감, 다음번 채용 D-?")
   - 백필 결과 vault `_SSOT/recruitment_catchup_YYYY-MM-DD.md` 별도 저장
3. 마지막 fire 시각 > 7일이면 **alert 강제**:
   - PushNotification + boot_state.md prepend 이중 fallback
   - 메시지: "⚠️ recruitment-scan {N}일 침묵 — cron 점검 필요"

위 catch-up이 끝난 뒤 평소 절차 진행.
```

### 3. 사이트 구조 변경 검증 (cron 발화 후 1일)

1번 cron 발화 후 vault `_SSOT/recruitment_scan_YYYY-MM-DD.md` 생성 시 confirm. 24시간 내 미생성이면 후보 #3(사이트 구조 변경)이 진짜 원인. fetch 실패 로그 확인:

```powershell
Get-Content C:\Users\윤상택\.hermes\logs\skills\recruitment-scanner.log -Tail 50
```

## 검증 (도입 후 3일)

| 시점 | 기대 | 액션 |
|---|---|---|
| Day 1 06:30 | `_SSOT/recruitment_scan_2026-05-26.md` 생성 | cron 정상 |
| Day 2 06:30 | 동상 | cron 안정 |
| Day 3 | hermes_daily 노트에 신규 공고 자동 노출 | 발견 채널 복구 |
| 미생성 시 | `recruitment-scanner.log` fetch 에러 → 후보 #3 패치 (selector 갱신) |

## 자가진화 패턴 등록

이 결함 패턴을 `인지진화_가중치.json`에 등록 (재발 방지):

```json
{
  "cron_silent_death": {
    "category": "infrastructure",
    "first_seen": "2026-05-05",
    "last_seen": "2026-05-24",
    "duration_days": 19,
    "severity": 5,
    "promote_threshold": 1,
    "examples": ["recruitment-scan 19일 침묵"],
    "trigger_words": ["cron 미발화", "마지막 fire", "N일 정체"],
    "self_check_rule": "모든 SKILL에 catch-up 룰 기본 포함",
    "weight": 0.95
  }
}
```
