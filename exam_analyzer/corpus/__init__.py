"""exam_analyzer.corpus — 기출 문항·예상 문항 데이터베이스 + 회독 관리.

Architecture (reconstruction-plan.md v3 §4):
  - models.py: Question, Choice, Attempt, ReviewRound dataclass
  - storage.py: ~/.exam_corpus.json atomic I/O (저작권 민감 → repo 커밋 금지)
  - import_.py: 사용자 이북 발췌본 반입 (JSON/대화형/텍스트)
  - drill.py: 회독 세션 (플래시카드, 랜덤, 취약 유형 집중)
  - scoring.py: 숙련도 산출, diagnose 와의 연계
  - match.py: 2차 소스 키워드 ↔ 1차 corpus 문항 매핑

ZERO-TOLERANCE (CLAUDE.md §1): 사용자 원본 발췌 외의 문항은 반입 금지.
에이전트가 생성한 예상 문항은 별도 유형(Question.kind="reverse_engineered")
으로 표시하고 근거 체인 필수.
"""

__all__ = []  # 각 모듈 구현 후 확장
