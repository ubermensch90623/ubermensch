# NCS Mermaid 템플릿 모음

[ncs-hierarchy.md](ncs-hierarchy.md)의 색상 클래스를 재사용.

## 1. 직무 전체 능력단위 트리 (가장 자주 쓰임)

```mermaid
flowchart TB
    JOB[세분류: 경영기획<br/>분류번호 02011501]:::detail

    JOB --> U1[능력단위 01<br/>사업환경 분석]:::unit
    JOB --> U2[능력단위 02<br/>경영방침 수립]:::unit
    JOB --> U3[능력단위 03<br/>경영계획 수립]:::unit
    JOB --> U4[능력단위 04<br/>신규사업 기획]:::unit
    JOB --> U5[능력단위 05<br/>사업타당성 검토]:::unit

    classDef detail fill:#FFD966
    classDef unit   fill:#A6A6A6,color:#fff
```

## 2. 능력단위 → 요소 → 수행준거 (3단 펼침)

```mermaid
flowchart LR
    U[능력단위 01<br/>사업환경 분석]:::unit

    U --> E1[요소 1.1<br/>분석 절차 수립]:::element
    U --> E2[요소 1.2<br/>정보 수집]:::element
    U --> E3[요소 1.3<br/>분석 결과 도출]:::element

    E1 --> C11[수행준거<br/>1.1.1 절차 정의]:::criteria
    E1 --> C12[수행준거<br/>1.1.2 일정 수립]:::criteria
    E2 --> C21[수행준거<br/>1.2.1 1차 자료 수집]:::criteria
    E2 --> C22[수행준거<br/>1.2.2 2차 자료 수집]:::criteria
    E3 --> C31[수행준거<br/>1.3.1 SWOT 분석]:::criteria
    E3 --> C32[수행준거<br/>1.3.2 시사점 도출]:::criteria

    classDef unit     fill:#A6A6A6,color:#fff
    classDef element  fill:#A9D18E
    classDef criteria fill:#F4B183
```

## 3. 학습모듈 흐름 (선수관계 포함)

```mermaid
flowchart TB
    M01[모듈 01<br/>NCS 이해]
    M02[모듈 02<br/>사업환경 분석]
    M03[모듈 03<br/>경영방침 수립]
    M04[모듈 04<br/>경영계획 수립]
    M05[모듈 05<br/>실습: 가상기업 기획]

    M01 --> M02
    M02 --> M03
    M03 --> M04
    M02 --> M05
    M03 --> M05
    M04 --> M05
```

선수 관계가 복잡하면 `flowchart LR`로 가로 배치.

## 4. 두 직무 능력단위 중첩 (유사 직무 비교)

```mermaid
flowchart LR
    subgraph A[직무 A: 경영기획]
        A1[사업환경 분석]
        A2[경영방침 수립]
        A3[경영계획 수립]
        A4[신규사업 기획]
    end

    subgraph B[직무 B: 사업기획]
        B1[시장조사]
        B2[사업타당성 검토]
        B3[사업계획서 작성]
        B4[리스크 분석]
    end

    subgraph SHARED[공통 능력단위]
        S1[사업타당성 검토]
        S2[시장환경 분석]
    end

    A1 -.- S2
    B1 -.- S2
    A4 -.- S1
    B2 -.- S1
```

`-.-` (점선)으로 공유 관계 표현.

## 5. NCS 기반 과정 설계 (학습기간 + 평가)

```mermaid
flowchart TB
    Start([교육 시작]) --> A[모듈 1<br/>40시간<br/>지필 평가]
    A --> B[모듈 2<br/>32시간<br/>실기 평가]
    B --> C{내부 평가<br/>합격?}
    C -->|합격| D[모듈 3<br/>48시간<br/>프로젝트]
    C -->|불합격| A
    D --> E[모듈 4<br/>40시간<br/>OJT]
    E --> F{외부 평가}
    F -->|합격| G([수료 + 자격 응시])
    F -->|불합격| D
```

## 6. 능력단위 ↔ 직무능력 매핑

```mermaid
graph LR
    subgraph 능력단위
        U1[사업환경 분석]
        U2[경영방침 수립]
        U3[경영계획 수립]
    end

    subgraph 직무능력
        K1[문제해결능력]
        K2[정보능력]
        K3[자원관리능력]
        K4[의사소통능력]
    end

    U1 --> K1
    U1 --> K2
    U2 --> K3
    U2 --> K4
    U3 --> K1
    U3 --> K3
    U3 --> K4
```

## 7. 자격증 ↔ NCS 능력단위 매핑

```mermaid
flowchart LR
    CERT[국가기술자격<br/>경영기획전문가]:::cert

    CERT --> U1[능력단위 01<br/>사업환경 분석]:::unit
    CERT --> U2[능력단위 02<br/>경영방침 수립]:::unit
    CERT --> U3[능력단위 03<br/>경영계획 수립]:::unit
    CERT --> U5[능력단위 05<br/>사업타당성 검토]:::unit

    classDef cert fill:#FFC000,color:#000
    classDef unit fill:#A6A6A6,color:#fff
```

## 사용 가이드

- 노드는 **공식 명칭** 그대로. 약어 금지.
- 분류번호는 노드 안에 한 줄로 표시 (`<br/>분류번호 02011501`).
- `subgraph`로 그룹화 시 그룹 이름도 한글.
- 색상은 `ncs-hierarchy.md` 클래스 재사용.
- 25개 이상 노드면 `flowchart TB` 대신 `subgraph` 분할 권장.
