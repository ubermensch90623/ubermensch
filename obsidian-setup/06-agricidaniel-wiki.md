# AgriciDaniel/claude-obsidian — 자동 Wiki 시스템 (옵션)

> kepano/obsidian-skills가 "스킬 팩"이라면, [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)은 "풀스택 자동 vault 시스템".
> Karpathy의 LLM Wiki 패턴 기반. `/wiki`, `ingest`, `/autoresearch` 등 자동 명령으로 vault가 스스로 자라남.

## 언제 도입할까

- ❌ **첫 1~2주는 건너뛰기** — 미니멀 키트로 vault에 익숙해진 후
- ✅ inbox가 정제되지 않은 자료로 쌓이기 시작할 때
- ✅ "이 PDF 50개를 정리해야 하는데..." 같은 일이 생길 때
- ✅ 한 주제를 깊게 파야 하는 리서치 작업이 잦을 때

## 제공 명령

| 명령 | 기능 | 예시 |
|---|---|---|
| `/wiki` | Vault 부트스트랩 (이미 셋업했으면 스킵) | `/wiki` → vault 초기화 |
| `ingest <file>` | 자료(PDF/링크/노트)를 읽어 wiki 페이지 생성 + 인덱스 업데이트. 중복 자동 머지 | `ingest ~/Downloads/book.pdf` |
| 질문하기 | 인덱스 검색 → 관련 페이지 → 인용 포함 답변 | "JTBD에 대해 내가 뭘 알고 있지?" |
| `/save` | 현재 Claude 대화를 wiki 노트로 저장 | `/save "JTBD 적용 토론"` |
| `/autoresearch <topic>` | 3라운드 자율 리서치 (gap-filling 포함) | `/autoresearch "B2B 가격 jobs-to-be-done"` |
| `lint the wiki` | 헬스 체크 (고립 노트, 죽은 링크, 오래된 주장) | `lint the wiki` |

## 설치 옵션

### 옵션 A: 별도 vault로 안전하게 (권장)

기존 brain vault와 분리되어 실험 가능. 부담 없음.

```powershell
# Windows PowerShell
cd %USERPROFILE%
git clone https://github.com/AgriciDaniel/claude-obsidian
cd claude-obsidian
bash bin/setup-vault.sh
# (Git Bash 또는 WSL 필요)
```

그 다음:
1. Obsidian → File → "Open folder as vault" → `claude-obsidian` 폴더
2. Claude Code에서: `/wiki`
3. 부트스트랩 완료 후 사용 시작

### 옵션 B: 기존 vault에 머지 (고급)

이미 사용 중인 brain vault에 skills/agents/templates만 추가.

```powershell
cd "%USERPROFILE%\Google Drive\Vault\brain"

# 임시 폴더에 클론
git clone https://github.com/AgriciDaniel/claude-obsidian "%TEMP%\cobs"

# 필요한 부분만 복사
xcopy /E /I "%TEMP%\cobs\skills" "skills"
xcopy /E /I "%TEMP%\cobs\agents" "agents"
xcopy /E /I "%TEMP%\cobs\_templates" "templates\agricidaniel"
copy "%TEMP%\cobs\CLAUDE.md" "CLAUDE.agric.md"
```

그 다음 본인 `CLAUDE.md`에 한 줄 추가:
```
# Additional skills
Also load skills from ./skills and agents from ./agents.
Reference CLAUDE.agric.md for the autonomous wiki commands
(/wiki, ingest, /save, /autoresearch, lint the wiki).
```

## 선결 조건

- Python 3.9+ (autoresearch 등에서 사용)
- Claude Code 또는 Claude.ai
- (옵션) Obsidian Local REST API 플러그인 — MCP 직접 vault 접근용

확인:
```powershell
python --version  # 3.9 이상
claude --version
```

## 기존 셋업과 충돌 가능 지점

| 영역 | 충돌 가능성 | 해결 |
|---|---|---|
| `templates/` 폴더 | `_templates/`의 파일이 기존 템플릿을 덮어쓸 수 있음 | 옵션 B에서 `templates/agricidaniel/`로 분리 |
| `CLAUDE.md` | 본인 CLAUDE.md와 합쳐지면 충돌 | `CLAUDE.agric.md`로 분리, 본인 파일에서 import 지시 |
| 사전 시드 vault | `wiki/concepts/`, `wiki/entities/`, `wiki/sources/` 추가 | 그대로 두거나 본인 `starter-notes/`와 통합 |
| Plugins | `Calendar`, `Thino`, `Banners` 등 자동 설치 권장 | 본인 환경과 맞으면 OK, 충돌 시 비활성화 |

## 활용 시나리오

### 1. 책 한 권 정리
```
ingest ~/Downloads/competing-against-luck.pdf
```
→ 자동으로 다음 생성:
- `wiki/sources/2026-05-10-competing-against-luck.md` (메타데이터)
- `wiki/concepts/jobs-to-be-done.md` (핵심 개념)
- `wiki/entities/clayton-christensen.md` (저자)
- 인덱스에 자동 추가
- 기존 노트 중 관련된 것 자동 wikilink

### 2. 깊이 있는 리서치
```
/autoresearch "B2B SaaS 가격 책정에 JTBD 적용"
```
→ 3라운드 자동 진행:
1. **Round 1**: 알려진 것 정리 (vault 검색)
2. **Round 2**: gap 식별 → 외부 검색
3. **Round 3**: 종합 + 본인 컨텍스트(CLAUDE.md) 기반 적용 방안
→ 결과를 `wiki/research/2026-05-10-saas-pricing-jtbd.md`로 저장

### 3. 정기 헬스 체크
```
lint the wiki
```
→ 출력 예시:
- 고아 노트 12개 (어디에도 링크 안 됨)
- 죽은 wikilink 3개 (`[[xxx]]`인데 xxx 파일 없음)
- 6개월 이상 안 본 stale 노트 24개
- 중복 가능성: `notes/A.md`와 `notes/A-summary.md` 95% 유사

## 우리 키트와의 통합 권장 흐름

```
주차    | 사용 내용
--------|-------------------------------------------------
1~2주   | 우리 키트만 (5폴더 + 시드 5개 + Web Clipper)
3~4주   | 옵션 B로 skills/agents만 머지. lint 시작
5~6주   | ingest 명령 사용해서 책/PDF 정리
7주+    | autoresearch 본격 활용, 또는 옵션 A로 풀스택 vault 비교
```

## 트러블슈팅

| 증상 | 해결 |
|---|---|
| `/wiki` 명령이 인식 안 됨 | `claude-obsidian` 폴더가 Claude Code의 working directory인지 확인 |
| `ingest`에서 Python 에러 | `pip install -r requirements.txt` 실행 |
| autoresearch가 너무 느림/비쌈 | `skills/autoresearch/references/program.md`에서 round 수 줄이기 |
| 기존 vault와 wikilink 충돌 | `_templates/`의 파일명 패턴이 본인 것과 일치하는지 확인 |
| lint가 의도된 stale 노트를 깨움 | `#status/evergreen` 태그 붙이면 lint가 무시 |

## 커스터마이징

`skills/autoresearch/references/program.md` 편집하여:
- 선호하는 출처 (예: ArXiv, Nature)
- 신뢰도 규칙
- 도메인 제약 (특정 주제만)
- 출력 형식

## 참고

- 공식 레포: https://github.com/AgriciDaniel/claude-obsidian
- Karpathy의 LLM Wiki 원본 패턴: https://karpathy.bearblog.dev/the-art-of-the-llm-wiki/
- 커뮤니티 토론: Obsidian Forum의 "claude-obsidian" 태그
