# AI 도구 도입 로드맵 — freeze 5/16 이후

> freeze: 2026-05-16까지 신규 프레임워크 도입 금지 (CLAUDE.md §10 또는 boot_state)
> 도입 일정: 5/17 ~ 5/31 우선순위 + 6월 안정화
> 기준: 종환 lived 도메인 적용 가능 + Tier 1·2 출처 검증된 도구만

---

## 도입 우선순위 (5/17~5/31)

| 우선 | 도구 | 영역 | 출처 (검증됨) | 설치 명령 |
|---|---|---|---|---|
| 1 | **faster-whisper** | 자막 없는 영상 음성→텍스트 | [GitHub](https://github.com/faker2048/youtube-faster-whisper) | `pip install faster-whisper yt-dlp` |
| 2 | **YouTube Data API v3** + `python-youtube` | 채널 검증 (subscriber·verified) | [PyPI python-youtube](https://pypi.org/project/python-youtube/) + [Google 공식](https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.channels.html) | `pip install python-youtube` + Google Cloud Console API Key |
| 3 | **ffmpeg + vid2slides** | 영상 슬라이드 추출 → OCR | [vid2slides GitHub](https://github.com/patrickmineault/vid2slides) | winget/scoop install ffmpeg + clone vid2slides |
| 4 | **Playwright + promptwright** | 브라우저 자동화 (Grok·ChatGPT·Gemini) | [promptwright GitHub](https://github.com/testronai/promptwright) | `pip install playwright promptwright` + `playwright install chromium` |
| 5 | **ChatGPT Atlas** (대안) | OpenAI 자체 agentic browser | [OpenAI 2025-10 발표](https://openai.com/atlas) | 종환 직접 다운 (ChatGPT Plus 활용) |

---

## 도입 후 가동 시나리오

### 시나리오 1 — 종환이 "유튜브 자료 찾아" 발화

```
1. WebSearch로 영상 검색
2. YouTube Data API로 채널 verified·subscriber·업로드일 검증
3. Tier 1·2 통과 영상만 유지
4. 자막 있으면 youtube-transcript-api
5. 자막 없으면 faster-whisper로 음성→텍스트
6. 슬라이드·차트 있으면 vid2slides + PaddleOCR
7. Claude가 transcript·OCR 결과 요약
8. _AI진화일지/유튜브_학습_YYYY-MM-DD.md 박제
9. 종환 케이스에 cross-link
```

→ 종환 1줄 발화 → 위 9단계 자동 실행.

### 시나리오 2 — "Grok·ChatGPT·Gemini로 자료 긁어와"

```
1. promptwright (또는 Playwright)로 Chrome 자동화
2. 종환 ChatGPT Plus 세션 활용 (이미 로그인된 상태)
3. 프롬프트 자동 생성 (자료 검색 + 종환 케이스 컨텍스트)
4. 응답 캡처 → 박제
5. 응답 검증 (Claude 자체 fact-check)
```

→ 종환이 직접 입력 안 해도 됨.

### 시나리오 3 — 정기 자율 학습 (cron 23:45 확장)

기존 world-learning-loop에 phase 2 추가:
```
phase 2:
  - 종환 활성 케이스 (전세·면접·필기·자소서) 키워드 자동 추출
  - YouTube 검색 + Tier 1·2 영상 1편 추출
  - transcript 학습 + 박제
  - 다음 날 종환 깨어났을 때 1줄 요약 보고
```

---

## 비용 (확인)

| 도구 | 비용 |
|---|---|
| faster-whisper | 무료 (오픈소스, 로컬 실행) |
| YouTube Data API | 무료 (일 10,000 unit, 채널 조회 1 unit) |
| ffmpeg + vid2slides | 무료 |
| Playwright + promptwright | 무료 |
| ChatGPT Atlas | 종환 ChatGPT Plus 포함 |

→ **추가 비용 0원**. 다 오픈소스 또는 종환 기존 구독 활용.

---

## 도입 후 종환 부담

종환이 직접 해야 할 것 (1회만):
1. Google Cloud Console에서 YouTube Data API Key 발급 (5분)
2. ChatGPT Atlas 다운로드 (선택)
3. 그 외 Claude(나) 자율 설치·운영

→ **5/17 (월) 30분 이내** 종환 부담 종결.

---

## 위험 평가

| 위험 | 평가 | 완화 |
|---|---|---|
| Whisper 한국어 정확도 | 95%+ (large-v3 기준) | 부정확 부분 transcript와 cross-check |
| Playwright 차단 (anti-bot) | 일부 사이트 차단 가능 | Chrome MCP 우회·종환 직접 진행 |
| YouTube Data API 일 할당량 | 10,000 unit/일 충분 | 캐싱으로 절약 |
| ChatGPT Atlas 안정성 | 2025-10 출시, 베타 가능성 | Playwright 백업 |

---

박제일: 2026-04-27
근거: X·GitHub 검증 (Tier 1·2 only) + freeze 5/16 + 종환 자율 위임
도입 시작: 2026-05-17
