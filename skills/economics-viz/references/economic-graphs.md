# 표준 경제 그래프 카탈로그

SKILL.md의 한글 폰트 보일러플레이트가 이미 적용된 상태라고 가정.

## 1. 수요공급 모형

| 변형 | 키워드 | 처리 |
|---|---|---|
| 균형 이동 | "수요 증가", "공급 충격" | 곡선 두 개(원본 + 점선) + 균형점 두 개 |
| 가격통제 | "가격상한", "최저임금" | 균형 + 수평선 + 잉여 영역 채우기 |
| 세금/보조금 | "조세귀착", "쐐기" | 공급곡선 평행이동 + 사중손실 삼각형 |
| 탄력성 | "탄력적", "비탄력적" | 기울기 다른 두 곡선 비교 패널 |

### 사중손실 영역 채우기 예시

```python
ax.fill_betweenx(np.linspace(eq_p_new, eq_p_old, 50),
                 q_supply_at_new_p, q_demand_at_new_p,
                 alpha=0.25, color="#d62728", label="사중손실")
```

## 2. IS-LM / AD-AS / Phillips

| 모델 | x축 | y축 | 곡선 |
|---|---|---|---|
| IS-LM | 국민소득 Y | 이자율 r | IS 우하향, LM 우상향 |
| AD-AS | 산출 Y | 물가 P | AD 우하향, SRAS 우상향, LRAS 수직 |
| Phillips | 실업률 u | 인플레이션 π | 단기 우하향, 장기 수직 |
| Laffer | 세율 t | 세수 T | 역 U자형 |

### Phillips 단기 vs 장기

```python
u = np.linspace(2, 10, 200)
short_run = 8 / u - 1            # 우하향
long_run = np.where(u >= 6, 0, np.nan)  # u = 6 (자연실업률)에서 수직

# 장기는 수직선으로 별도 처리
ax.plot(u, short_run, label="단기 Phillips")
ax.axvline(6, color="black", linestyle="--", label="장기 Phillips (자연실업률 6%)")
```

## 3. 미시 — 무차별곡선 / 예산제약

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0.1, 10, 200)
U = [4, 6, 8]                   # 효용 수준
for u in U:
    y = u**2 / x                # Cobb-Douglas: U = x^0.5 * y^0.5 → y = U^2/x
    ax.plot(x, y, label=f"U = {u}")

# 예산제약 P_x·x + P_y·y = M
M, Px, Py = 12, 1, 1
budget_x = np.linspace(0, M / Px, 50)
budget_y = (M - Px * budget_x) / Py
ax.plot(budget_x, budget_y, "k--", label="예산제약")
```

## 4. 게임이론 보수행렬 (히트맵)

```python
import numpy as np
import matplotlib.pyplot as plt

# 죄수의 딜레마 — 행: 행위자 A, 열: 행위자 B
# 셀: (A보수, B보수)
payoff_A = np.array([[-1, -3],
                     [ 0, -2]])
payoff_B = np.array([[-1,  0],
                     [-3, -2]])

fig, ax = plt.subplots(figsize=(4.5, 4))
ax.matshow(payoff_A, cmap="Blues", alpha=0.5)
for i in range(2):
    for j in range(2):
        ax.text(j, i, f"({payoff_A[i,j]}, {payoff_B[i,j]})",
                ha="center", va="center", fontsize=12)
ax.set_xticks([0, 1]); ax.set_xticklabels(["협력", "배신"])
ax.set_yticks([0, 1]); ax.set_yticklabels(["협력", "배신"])
ax.set_xlabel("행위자 B"); ax.set_ylabel("행위자 A")
ax.set_title("죄수의 딜레마 보수행렬")
```

내쉬균형은 별도 마커(★)로 강조.

## 5. 시계열 (실증 데이터)

데이터 출처 필수. 미명시 시계열 그리지 말 것.

```python
# 예: 한국은행 ECOS API 또는 KOSIS 다운로드 CSV
df = pd.read_csv("ecos_cpi.csv", parse_dates=["date"])
ax.plot(df["date"], df["cpi"], label="CPI (2020=100)")
ax.set_title("소비자물가지수 추이 — 출처: 한국은행 ECOS")
```

권장 데이터 출처:
- **한국은행 ECOS**: GDP, 환율, 금리, 통화량
- **KOSIS**: 고용, 인구, 산업
- **FRED**: 미국·국제 비교 자료
- **OECD.Stat**: 국가 간 비교

## 6. 비교정학 (다중 패널)

정책 충격 전후를 좌·우 패널로 비교:

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
# ax1: 충격 전, ax2: 충격 후
ax1.set_title("(a) 통화정책 충격 이전")
ax2.set_title("(b) 통화정책 충격 이후")
```

## 색상 정책

- 곡선 1: `#1f77b4` (파랑)
- 곡선 2: `#d62728` (빨강) — 대비용
- 이동/대안 곡선: 동일 색의 `linestyle="--"`
- 강조 영역: `alpha=0.25` 채우기
- 균형점/내쉬점: 검정 점 + 별 마커

전체 팔레트는 [palette-and-style.md](palette-and-style.md).
