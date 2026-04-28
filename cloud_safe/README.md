# jonghwan-ssot-cloud-safe

> 24/7 자율 분신 클라우드 측 인프라 — `cognitive-evolution-cloud` routine이 본격 4사이클 (PLAN→MONITOR→DIFF→DELIVERY) 수행하기 위한 PII-safe SSOT mirror.
>
> 헌법: `_SSOT/24_7_분신_헌법.md` C-0~C-7
> 박은 자: Claude (종환 명령 "미해결된 부분 해" 2026-04-28 20:20)
> Phase 3 (5/17 freeze 후) 본격 가동 예정. 그 전에는 메타데이터 보존만.

## PII 보호 (3중 차단)

1. **화이트리스트 강제** (`.gitignore`): 등록 파일만 push 허용
2. **블랙리스트 영구 차단**: 종환_*, 전세*, HUG_*, 임차*, 법원* 등 패턴
3. **Git history 진단**: pre-commit hook으로 PII 키워드 grep (TODO Phase 3)

## 영구 제외 (PII 위험)

- `종환_*_원본.md` (가치관·디지털프로파일·연대표·학생기록부·lived 경험)
- `ChatGPT_Gemini_종환아바타_운영가이드.md` (생일·동·경력 명시)
- `자율_메타학습_시스템.md` (보증금 액수 명시)
- 전세보증금·HUG·임차권·법원 매뉴얼 일체
- `세션_핸드오프_*.md` (시간순 발화 기록)
- `자기방어_*`, `한국사회_*`, `나같은_*`, `배신_*` (사적 분석)
