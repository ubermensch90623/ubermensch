"""
크롤링 대상 사이트 정의
- 목표 기관: 서민금융진흥원, 근로복지공단, 건강보험공단, 경기도 공공기관
- NCS 공통 자료 + 기관별 자료 + 커뮤니티 후기
"""

# 목표 기관 정보
TARGET_INSTITUTIONS = {
    "서민금융진흥원": {
        "name": "서민금융진흥원",
        "short": "서금원",
        "website": "https://www.kinfa.or.kr",
        "recruit_url": "https://www.kinfa.or.kr/info/recruit.do",
        "exam_type": "NCS 직업기초능력평가",
        "subjects": ["의사소통능력", "수리능력", "문제해결능력", "자원관리능력", "정보능력"],
        "keywords": ["서민금융진흥원 NCS", "서민금융진흥원 필기", "서민금융진흥원 채용", "서금원 시험"],
    },
    "근로복지공단": {
        "name": "근로복지공단",
        "short": "근복",
        "website": "https://www.comwel.or.kr",
        "recruit_url": "https://www.comwel.or.kr/comwel/paym/open/open1.jsp",
        "exam_type": "NCS 직업기초능력평가 + 직무수행능력평가",
        "subjects": ["의사소통능력", "수리능력", "문제해결능력", "자원관리능력", "조직이해능력"],
        "keywords": ["근로복지공단 NCS", "근로복지공단 필기", "근로복지공단 채용", "근복 시험"],
    },
    "건강보험공단": {
        "name": "국민건강보험공단",
        "short": "건보",
        "website": "https://www.nhis.or.kr",
        "recruit_url": "https://recruit.nhis.or.kr",
        "exam_type": "NCS 직업기초능력평가",
        "subjects": ["의사소통능력", "수리능력", "문제해결능력", "자원관리능력", "정보능력"],
        "keywords": ["건강보험공단 NCS", "건보 필기", "국민건강보험공단 채용", "건보 시험", "NHIS 채용"],
    },
    "경기도공공기관": {
        "name": "경기도 공공기관",
        "short": "경기도",
        "website": "https://www.gg.go.kr",
        "recruit_url": "https://job.gg.go.kr",
        "exam_type": "NCS 직업기초능력평가",
        "subjects": ["의사소통능력", "수리능력", "문제해결능력"],
        "keywords": ["경기도 공공기관 NCS", "경기도 공공기관 채용", "경기도 NCS 필기"],
    },
}

# NCS 공통 크롤링 소스
NCS_COMMON_SOURCES = [
    {
        "name": "NCS 공식 필기문항",
        "url": "https://ncs.go.kr/blind/rh13/bbs_lib_list.do?libDstinCd=48",
        "type": "official_questions",
        "description": "NCS 기반 채용 모델 공식 필기시험 샘플 문항",
    },
    {
        "name": "NCS 예시문항",
        "url": "https://ncs.go.kr/blind/blp/bbs_lib_list.do?libDstinCd=55",
        "type": "official_questions",
        "description": "시험 대비용 추가 예시 문항",
    },
    {
        "name": "잡알리오 채용공고",
        "url": "https://job.alio.go.kr/recruit.do",
        "type": "recruitment",
        "description": "공공기관 채용 공고 통합 시스템",
    },
    {
        "name": "링커리어 NCS CBT",
        "url": "https://cbt.linkareer.com/exam/public-company",
        "type": "mock_exam",
        "description": "실제 기출 기반 무료 온라인 CBT 모의고사",
    },
    {
        "name": "링커리어 NCS 기출 정리",
        "url": "https://community.linkareer.com/employment_data/4251423",
        "type": "exam_review",
        "description": "2025 최신 NCS 기출문제 정리",
    },
    {
        "name": "링커리어 NCS 풀이전략",
        "url": "https://community.linkareer.com/employment_data/4182192",
        "type": "study_strategy",
        "description": "NCS 기출문제 유형별 풀이 전략",
    },
    {
        "name": "사이버국가고시센터 PSAT",
        "url": "https://www.gosi.kr/",
        "type": "psat_questions",
        "description": "PSAT 기출문제 및 정답 (NCS PSAT형 대비)",
    },
    {
        "name": "공취사 PSAT 아카이브",
        "url": "https://gongchisa.oopy.io/",
        "type": "psat_questions",
        "description": "민경채·7급·5급 PSAT 문항 및 해설",
    },
]

# 커뮤니티 크롤링 소스 (시험 후기, 기출 복원)
COMMUNITY_SOURCES = [
    {
        "name": "링커리어 커뮤니티",
        "base_url": "https://community.linkareer.com",
        "search_url": "https://community.linkareer.com/search?keyword={keyword}",
        "type": "community",
    },
    {
        "name": "잡코리아 공기업",
        "base_url": "https://www.jobkorea.co.kr",
        "search_url": "https://www.jobkorea.co.kr/Search/?stext={keyword}",
        "type": "community",
    },
]

# 웹 검색 쿼리 (기관별 기출/후기 수집용)
def get_search_queries(institution_key: str) -> list[str]:
    """기관별 검색 쿼리 생성"""
    inst = TARGET_INSTITUTIONS.get(institution_key, {})
    name = inst.get("name", institution_key)
    short = inst.get("short", "")

    queries = [
        f"{name} NCS 기출문제",
        f"{name} 필기시험 후기",
        f"{name} 채용 시험 과목",
        f"{name} NCS 유형",
        f"{name} 합격 수기",
        f"{name} 시험 난이도",
        f"{name} 필기 준비",
    ]

    if short:
        queries.extend([
            f"{short} NCS 기출",
            f"{short} 시험 후기",
            f"{short} 합격 후기",
        ])

    return queries
