# 색상·스타일 정책 (경제학 시각화)

## 핵심 원칙

- 한 차트 = 한 톤. 의미 있는 대비만 색 분리.
- 색상은 의미를 운반해야 한다 (수요=파랑, 공급=빨강 일관).
- 흑백 인쇄에서도 구분되도록 `linestyle` 병용.
- 색맹 친화 팔레트 우선.

## 표준 의미-색 매핑

| 의미 | 색상 | 헥스 |
|---|---|---|
| 수요 / 가계 / 소비 | 파랑 | `#1f77b4` |
| 공급 / 기업 / 생산 | 빨강 | `#d62728` |
| 정부 / 재정 | 초록 | `#2ca02c` |
| 화폐 / 통화 / 중앙은행 | 주황 | `#ff7f0e` |
| 해외 / 무역 | 보라 | `#9467bd` |
| 균형점 / 강조 | 검정 | `#000000` |
| 사중손실 / 비효율 | 빨강 채우기 (alpha=0.25) | `#d62728` |
| 잉여 (소비자/생산자) | 파랑·빨강 채우기 (alpha=0.25) | 위 동일 |

## matplotlib rcParams (한 번에 적용)

```python
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "legend.frameon": False,
    "lines.linewidth": 2.0,
    "figure.dpi": 110,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "axes.unicode_minus": False,
})
```

## 출력 형식

| 용도 | 형식 | 비고 |
|---|---|---|
| 문서 임베드 | SVG | 벡터, 한글 폰트 깨짐 없음 |
| 발표 슬라이드 | PNG (200dpi) | 호환성 |
| 인쇄 보고서 | PDF | LaTeX 통합 시 |
| 채팅 응답 | PNG | 기본 |

## 한글 폰트 환경 진단 스크립트

코드 생성 전에 사용자 환경 확인이 필요하면:

```python
import matplotlib.font_manager as fm

candidates = ["Noto Sans CJK KR", "NanumGothic", "Malgun Gothic", "AppleGothic"]
installed = {p.name for p in fm.fontManager.ttflist}
print("설치된 한글 폰트:", [c for c in candidates if c in installed])
print("기본 폰트:", plt.rcParams["font.family"])
```

설치 안내:
- **Ubuntu/Debian**: `sudo apt install fonts-noto-cjk`
- **macOS**: 시스템 기본 AppleGothic 있음
- **Windows**: 시스템 기본 Malgun Gothic 있음
- **pip**: `pip install matplotlib koreanize-matplotlib` 후 `import koreanize_matplotlib` 한 줄

## 차트 크기 가이드

| 용도 | figsize |
|---|---|
| 단일 모델 (수요공급, IS-LM) | (6, 4.5) |
| 비교정학 1×2 패널 | (10, 4.5) |
| 2×2 다중 패널 | (10, 8) |
| 슬라이드 임베드 | (8, 5) |
| 인포그래픽 세로 | (5, 7) |

## 라벨 컨벤션

- 축 라벨: `"수량 Q"`, `"가격 P"` — 변수 한글명 + 기호.
- 범례: `"수요 D"`, `"수요' D′ (증가)"` — prime 표기로 이동 표시.
- 균형점: `"E"`, `"E′"` 으로 표기 (annotate).
- 데이터 출처는 차트 제목 우측에 `"— 출처: 한국은행 ECOS"` 형식.
- 시뮬레이션이면 제목에 `"(시뮬레이션 예시)"`.

## 흔한 실수와 수정

| 증상 | 원인 | 수정 |
|---|---|---|
| 한글이 □□□ | 폰트 미설정 | SKILL.md 보일러플레이트 적용 |
| 음수 부호가 □ | unicode_minus | `plt.rcParams["axes.unicode_minus"] = False` |
| 곡선이 너무 가늘다 | 기본 1.5 | `lines.linewidth=2.0` |
| 격자가 너무 진하다 | 기본 alpha=1 | `grid.alpha=0.3` |
| 범례 박스 거슬림 | 기본 frameon=True | `legend.frameon=False` |
