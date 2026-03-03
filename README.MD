# 🏢 Learning Agent Corp.

우버멘쉬의 NCS + 경제학 공기업 시험 합격을 위한 자율적 학습 시스템

## 목표 기관
- 서민금융진흥원
- 신용회복위원회
- 기업은행

## 조직 구조

### C-Suite (5명)
| 직위 | 에이전트 | 역할 |
|------|----------|------|
| CEO | 🧠 아키텍트 | 전체 전략 수립 |
| CTO | ⚙️ 시스템 엔지니어 | 데이터 파이프라인 |
| COO | 📋 운영총괄 | 일일 학습 실행 |
| CFO | 📈 성과분석관 | 점수 추적 |
| CMO | 💪 동기부여관 | 번아웃 방지 |

### 팀 (7개 + TF + 채용)
1. 데이터팀 (CTO) — Keep→Notion 파이프라인
2. 학습팀 (COO) — 실제 학습 실행
3. 분석팀 (CFO) — 성과 측정
4. 피드백팀 (CMO) — 지속가능성
5. 연구팀 (CEO) — 외부 정보
6. 업데이트팀 (CTO) — 시스템 반영
7. 외교팀 (CTO) — AI간 협업
8. 채용팀 (CEO) — 조직 진화
9. TF팀 (CEO) — 긴급 대응

### 전사 현황: 32명 + 8 레드팀 = 40명

## 배치 우선순위
1. 🔧 배관공 + 🔴 데이터 검증관 (Wave 1)
2. 📊 추적관 (Wave 2)
3. 📅 복습관 + 🔴 현실성 검증관 (Wave 3)
4. 🕵️ 전략 스카우터 + 🔴 정보 신뢰도 검증관 (Wave 4)
5. 이후 순차 배치

## 프로젝트 구조
```
├── CLAUDE.md                  # 전체 시스템 명세
├── agents/                    # 에이전트 프롬프트 파일
│   ├── c-suite/              # C-Suite 경영진
│   ├── data-team/            # 데이터팀
│   ├── learning-team/        # 학습팀
│   ├── analysis-team/        # 분석팀
│   ├── feedback-team/        # 피드백팀
│   ├── research-team/        # 연구팀
│   ├── update-team/          # 업데이트팀
│   ├── diplomacy-team/       # 외교팀
│   ├── hiring-team/          # 채용팀
│   └── tf-team/              # TF팀 프로토콜
├── config/                    # 설정 파일
│   └── agent-registry.json   # 전체 에이전트 등록부
├── data/                      # 데이터 저장소
│   ├── keep-memos/           # Keep 메모 임포트
│   ├── study-logs/           # 학습 활동 로그
│   └── reports/              # 생성된 보고서
├── workflows/                 # 프로세스 정의
│   ├── main-loop.md          # 메인 학습 사이클
│   ├── research-loop.md      # 연구 루프
│   ├── diplomacy-loop.md     # 외교 루프
│   └── automation-schedule.md # 24/7 자동화
└── status/                    # 현황 추적
    ├── deployment-status.json # 배치 현황
    └── weekly-report-template.json
```

## 핵심 원칙
- 새로 만들지 말고 기존 것을 합쳐서 실제로 쓸 수 있게
- "이거 복붙하세요" 수준의 단순함
- 한 번에 하나씩만 진행
- 완벽한 시스템보다 "당장 쓸 수 있는 최소 버전" 우선
- 린스타트업: 1명씩 채용하며 검증
