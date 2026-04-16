# 데스크탑(로컬 PC) 설치 · 적용 가이드

> 웹 세션에서 완료된 모든 작업이 `claude/fix-handwriting-recognition-J9xJq` 브랜치에 푸시되어 있음.
> 이 문서는 로컬 데스크탑에서 동일 환경으로 **즉시 이어가기** 위한 최소 명령.

## 0. 필수 조건

- Git 설치됨
- Python **3.9 이상** (`python --version` 또는 Windows `py -3 --version`)
- 외부 의존성 없음 (stdlib only)

## 1. 저장소 받기

### 새로 clone 하는 경우
```bash
git clone https://github.com/ubermensch90623/ubermensch.git
cd ubermensch
git fetch origin claude/fix-handwriting-recognition-J9xJq
git checkout claude/fix-handwriting-recognition-J9xJq
```

### 이미 clone 되어 있는 경우 (pull)
```bash
cd ubermensch
git fetch origin claude/fix-handwriting-recognition-J9xJq
git checkout claude/fix-handwriting-recognition-J9xJq
git pull origin claude/fix-handwriting-recognition-J9xJq
```

## 2. 동작 확인

```bash
# 전체 테스트 (67개 전부 통과해야 정상)
python -m unittest discover tests

# 점수 분석 (사용자 실제 점수)
python -m exam_analyzer analyze \
  --agency "서민금융진흥원" --date 2026-04-15 \
  --section "직업기초능력평가:19.33:40:40" \
  --section "직무수행능력평가:38.76:60:60" \
  --cutoff 64.48

# 정밀 원인 분석
python -m exam_analyzer diagnose \
  --agency "서민금융진흥원" --date 2026-04-15 \
  --section "직업기초능력평가:19.33:40:40" \
  --section "직무수행능력평가:38.76:60:60" \
  --cutoff 64.48

# corpus 상태 (아직 비어 있음)
python -m exam_analyzer corpus stats
```

### Windows PowerShell 사용 시
```powershell
# 줄바꿈은 ` 기호 대신 한 줄로 입력하거나, ^ 대신 `
python -m exam_analyzer analyze `
  --agency "서민금융진흥원" --date 2026-04-15 `
  --section "직업기초능력평가:19.33:40:40" `
  --section "직무수행능력평가:38.76:60:60" `
  --cutoff 64.48
```

### Windows 콘솔에서 한글 깨짐
```
chcp 65001
```
UTF-8 코드페이지로 전환 후 재실행.

## 3. 데이터 파일 위치 (로컬 보관, 저장소 커밋 금지)

| 파일 | 위치 | 용도 | `.gitignore` |
|---|---|---|---|
| `~/.exam_history.json` | 홈 디렉터리 | 점수 이력 (`analyze --save` 로 축적) | ✓ |
| `~/.exam_corpus.json` | 홈 디렉터리 | 기출 문항 DB (이북 발췌 반입) | ✓ |

Windows 에서 `~` = `C:\Users\<사용자명>`.
macOS/Linux 에서 `~` = `$HOME`.

환경변수로 오버라이드 가능:
```bash
export EXAM_HISTORY_FILE=/path/to/other.json
export EXAM_CORPUS_FILE=/path/to/corpus.json
```

## 4. Claude Code 로 이어가기

### Claude Code 데스크탑 앱 (권장)
1. 앱에서 **이 저장소 폴더** 를 열기
2. 새 세션 시작
3. 앱이 자동으로 `CLAUDE.md` 읽음 → 모든 헌법/컨텍스트 복구
4. 첫 메시지 예시:
   ```
   이 저장소의 CLAUDE.md 와 docs/readiness_checklist.md 를 읽고
   현재 상태 파악한 뒤, M1 (공고 PDF) 공유할 테니 Step 1 진행.
   ```

### Claude Code CLI
```bash
cd ubermensch
claude
# 세션 시작 후 CLAUDE.md 자동 읽음
```

## 5. 세션 컨텍스트 즉시 복구 (읽을 문서 순서)

Claude 에게 처음 이것을 알려주세요:
```
다음 순서로 문서 읽고 현재 상태 파악해:
1. CLAUDE.md (헌법 C-0~C-11 + 에이전트 프로토콜)
2. docs/audit-v3.md (정합성 점검)
3. docs/reconstruction-plan.md (R1~R12 루틴)
4. docs/readiness_checklist.md (Step 0~8 실행 시퀀스)
5. docs/exam_reconstruction/서민금융진흥원_2026_상반기_종합직_일반/00_meta.md
6. docs/agent_performance.md
```

## 6. 설정 파일 (선택)

이 저장소는 프로젝트별 `.claude/` 디렉터리 없음. 대신 `CLAUDE.md` 로 충분.

로컬 Claude Code 설정(전역) `~/.claude/settings.json` 은 기존 사용자 설정 그대로.
이 프로젝트는 외부 MCP 서버나 skill 추가 설치 요구 없음 (경연 판결 옵션 A 보수 반영).

## 7. 사용자 자료 공유 후 즉시 가동 (데스크탑·웹 공통)

`docs/readiness_checklist.md` 의 Step 1~8 순서로 진행됨:

```
M1 공고 PDF   →  Agent P1 공고분석 (10분)
M2 직렬코드    →  P1 매핑 + P2 대행사 (10분)
M3 이북 목록   →  P4 카탈로그 + 경연 (10분)
이북 발췌 샘플 →  corpus import + 회독 가동
```

## 8. 오프라인 작업 가능 범위

데스크탑 오프라인 상태여도 아래는 동작:
- 모든 unittest
- `analyze`, `diagnose`, `corpus stats/list/mastery`
- 이미 적재된 corpus 로 회독

WebSearch/WebFetch 가 필요한 작업 (R3/R4/R5/R6 에이전트 파견) 은 인터넷 필수.

## 9. 충돌 발생 시 (혹시 로컬에도 커밋 있으면)

```bash
# 로컬 변경 내용을 잠시 보관
git stash

# 원격 pull
git pull origin claude/fix-handwriting-recognition-J9xJq

# 보관 내용 복원
git stash pop

# 충돌 파일 수동 머지 후
git add <파일>
git commit
```

## 10. 진행 이력 요약 (2026-04-16)

- 42커밋 누적
- 67 unittest 전부 통과
- 헌법 C-0 ~ C-11 (12조)
- 에이전트 편제 P1~P11 + 템플릿 9종
- corpus 모듈 6종 + CLI 통합
- audit-v1/v2/v3
- 교재 구매 추천서 + 학술 자료 인덱스 + readiness 체크리스트

---

**C-11 상기**: 완벽한 이행이 아니어도 괜찮습니다. 로컬 세팅 중 문제 발생하면 세션에서 구체 에러 메시지만 알려주시면 디버그 가능. 작게 자주 망하며 복구.
