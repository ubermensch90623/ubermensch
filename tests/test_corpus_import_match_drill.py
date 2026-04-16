"""corpus import / match / drill 모듈 정식 unittest."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exam_analyzer.corpus.drill import (  # noqa: E402
    end_session,
    next_question,
    start_session,
    submit_answer,
)
from exam_analyzer.corpus.import_ import (  # noqa: E402
    ImportError as CorpusImportError,
    deduplicate,
    import_from_json_file,
    import_from_simple_text,
    parse_simple_text_block,
    question_from_user_dict,
)
from exam_analyzer.corpus.match import (  # noqa: E402
    SecondaryClaim,
    build_match_report,
    keyword_in_question,
    match_claim_to_corpus,
    report_to_dict,
)
from exam_analyzer.corpus.models import (  # noqa: E402
    Choice,
    CorpusSnapshot,
    Provenance,
    Question,
    generate_question_id,
)


def _basic_provenance() -> Provenance:
    return Provenance(
        source_type="ebook",
        source_name="테스트 이북",
        source_citation="p.1",
        source_date="2025-01-01",
    )


def _sample_user_dict() -> dict:
    return {
        "agency": "서민금융진흥원",
        "area": "NCS/의사소통",
        "question_text": "다음 글의 주제는?",
        "choices": [{"text": "주제 A"}, {"text": "주제 B"}],
        "correct_index": 2,
        "provenance": {
            "source_type": "ebook",
            "source_name": "테스트 이북",
            "source_date": "2025-01-01",
        },
    }


class TestImport(unittest.TestCase):
    def test_user_dict_success(self) -> None:
        q = question_from_user_dict(_sample_user_dict())
        self.assertEqual(q.agency, "서민금융진흥원")
        self.assertEqual(q.provenance.source_name, "테스트 이북")
        self.assertEqual(len(q.choices), 2)

    def test_missing_provenance_raises(self) -> None:
        d = _sample_user_dict()
        del d["provenance"]
        with self.assertRaises(CorpusImportError):
            question_from_user_dict(d)

    def test_provenance_missing_required_field_raises(self) -> None:
        d = _sample_user_dict()
        d["provenance"] = {"source_type": "", "source_name": "", "source_date": ""}
        with self.assertRaises(CorpusImportError):
            question_from_user_dict(d)

    def test_simple_text_parse(self) -> None:
        block = (
            "Q: 다음 중 틀린 것은?\n"
            "1) 선지1\n"
            "2) 선지2\n"
            "3) 선지3\n"
            "4) 선지4\n"
            "정답: 3\n"
            "해설: 3번 설명"
        )
        q = parse_simple_text_block(
            block, "서민금융진흥원", "NCS/문제해결", _basic_provenance()
        )
        self.assertEqual(q.correct_index, 3)
        self.assertEqual(len(q.choices), 4)
        self.assertTrue(q.choices[2].is_correct)
        self.assertFalse(q.choices[0].is_correct)
        self.assertEqual(q.explanation, "3번 설명")

    def test_import_multi_block_text(self) -> None:
        block = (
            "Q: 첫 문제\n1) 선지1\n2) 선지2\n정답: 1\n"
            "---\n"
            "Q: 둘째 문제\n1) 선지1\n2) 선지2\n정답: 2\n"
        )
        qs = import_from_simple_text(block, "x", "y", _basic_provenance())
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0].correct_index, 1)
        self.assertEqual(qs[1].correct_index, 2)

    def test_import_from_json_file(self) -> None:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump({"questions": [_sample_user_dict()]}, tmp, ensure_ascii=False)
        tmp.close()
        try:
            qs = import_from_json_file(Path(tmp.name))
            self.assertEqual(len(qs), 1)
        finally:
            os.unlink(tmp.name)

    def test_deduplicate(self) -> None:
        q = question_from_user_dict(_sample_user_dict())
        result = deduplicate([q], [q])
        self.assertEqual(result, [])


class TestMatch(unittest.TestCase):
    def _corpus(self) -> CorpusSnapshot:
        q1 = Question(
            id=generate_question_id(
                "primary", "서민금융진흥원", "직무/법률", "휴면예금"
            ),
            kind="primary",
            agency="서민금융진흥원",
            area="직무/법률",
            subtype="조문적용",
            question_text="휴면예금 관리 재단법상 소멸시효는?",
            choices=[Choice(1, "5년"), Choice(2, "10년", is_correct=True)],
            correct_index=2,
            related_law_articles=["휴면예금관리재단법 §5"],
            tags=["휴면예금", "소멸시효"],
            provenance=_basic_provenance(),
        )
        q2 = Question(
            id=generate_question_id(
                "primary", "서민금융진흥원", "NCS/수리", "도표"
            ),
            kind="primary",
            agency="서민금융진흥원",
            area="NCS/수리",
            subtype="도표해석",
            question_text="평균 대출 금리는?",
            choices=[Choice(1, "3.5%")],
            correct_index=1,
            provenance=_basic_provenance(),
        )
        return CorpusSnapshot(questions=[q1, q2])

    def test_keyword_matches_question_text_and_tags(self) -> None:
        corpus = self._corpus()
        q = corpus.questions[0]
        matched_fields: list = []
        score = keyword_in_question("휴면예금 소멸시효", q, matched_fields)
        self.assertGreater(score, 0.5)
        self.assertIn("question_text", matched_fields)

    def test_no_match_for_irrelevant_keyword(self) -> None:
        corpus = self._corpus()
        q = corpus.questions[0]
        matched_fields: list = []
        score = keyword_in_question("양자역학", q, matched_fields)
        self.assertEqual(score, 0.0)
        self.assertEqual(matched_fields, [])

    def test_match_claim_to_corpus_top_n(self) -> None:
        corpus = self._corpus()
        claim = SecondaryClaim(
            keyword="휴면예금",
            source_url="https://ex.com",
            quoted_text="휴면예금 문제",
            source_date="2026-03-20",
        )
        hits = match_claim_to_corpus(claim, corpus, top_n=5)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].matched_question_id, corpus.questions[0].id)

    def test_build_match_report(self) -> None:
        corpus = self._corpus()
        claims = [
            SecondaryClaim(
                keyword="휴면예금",
                source_url="u1",
                quoted_text="q",
                source_date="2026-03-20",
            ),
            SecondaryClaim(
                keyword="평균 대출 금리",
                source_url="u2",
                quoted_text="q",
                source_date="2026-03-20",
            ),
            SecondaryClaim(
                keyword="양자역학",
                source_url="u3",
                quoted_text="q",
                source_date="2026-03-20",
            ),
        ]
        report = build_match_report(claims, corpus)
        self.assertEqual(report.total_claims, 3)
        self.assertEqual(report.matched_claims, 2)
        self.assertIn("양자역학", report.unmatched_claims)
        payload = report_to_dict(report)
        self.assertIn("caveat", payload)
        self.assertIn("수석위원", payload["caveat"])


class TestDrill(unittest.TestCase):
    def _make_snapshot(self, n: int = 3) -> CorpusSnapshot:
        qs = []
        for i in range(n):
            qs.append(
                Question(
                    id=f"q_{i}",
                    kind="primary",
                    agency="서민금융진흥원",
                    area="NCS/의사소통",
                    subtype="주제",
                    question_text=f"Q{i}",
                    choices=[
                        Choice(1, "a"),
                        Choice(2, "b", is_correct=True),
                    ],
                    correct_index=2,
                    provenance=_basic_provenance(),
                )
            )
        return CorpusSnapshot(questions=qs)

    def test_sequential_mode(self) -> None:
        snap = self._make_snapshot()
        sess = start_session(snap, round_num=1, mode="sequential")
        self.assertEqual(len(sess.scope), 3)
        q = next_question(sess)
        self.assertEqual(q.id, "q_0")

    def test_submit_correct_wrong_skip(self) -> None:
        snap = self._make_snapshot()
        sess = start_session(snap, round_num=1, limit=3)
        submit_answer(sess, snap, selected_index=2)
        submit_answer(sess, snap, selected_index=1)
        submit_answer(sess, snap, selected_index=None)
        self.assertEqual(len(snap.attempts), 3)
        self.assertIs(snap.attempts[0].is_correct, True)
        self.assertIs(snap.attempts[1].is_correct, False)
        self.assertIsNone(snap.attempts[2].is_correct)

    def test_end_session_summary(self) -> None:
        snap = self._make_snapshot()
        sess = start_session(snap, round_num=1, limit=3)
        submit_answer(sess, snap, selected_index=2)
        submit_answer(sess, snap, selected_index=1)
        submit_answer(sess, snap, selected_index=None)
        summary = end_session(sess, snap, notes="테스트")
        self.assertEqual(summary["correct"], 1)
        self.assertEqual(summary["wrong"], 1)
        self.assertEqual(summary["skipped"], 1)
        self.assertEqual(summary["total_attempted"], 3)
        self.assertAlmostEqual(summary["accuracy"], 1 / 3, places=3)
        self.assertIsNotNone(snap.rounds[0].completed_at)

    def test_random_mode_seeded(self) -> None:
        snap = self._make_snapshot(n=5)
        sess1 = start_session(snap, round_num=1, mode="random", seed=42)
        # 다른 round 용 새로운 snapshot 으로 재현성 테스트
        snap2 = self._make_snapshot(n=5)
        sess2 = start_session(snap2, round_num=1, mode="random", seed=42)
        self.assertEqual(
            [q.id for q in sess1.scope], [q.id for q in sess2.scope]
        )

    def test_weakest_first_mode(self) -> None:
        snap = self._make_snapshot(n=4)
        sess = start_session(
            snap, round_num=1, mode="weakest_first", weakest_ids=["q_3", "q_1"]
        )
        # weakest 가 앞으로 옴
        self.assertEqual(sess.scope[0].id, "q_3")
        self.assertEqual(sess.scope[1].id, "q_1")

    def test_area_filter(self) -> None:
        snap = self._make_snapshot()
        # 다른 area 문항 추가
        snap.questions.append(
            Question(
                id="z1",
                kind="primary",
                agency="x",
                area="직무/경영",
                subtype="",
                question_text="NPV",
                choices=[Choice(1, "a", is_correct=True)],
                correct_index=1,
                provenance=_basic_provenance(),
            )
        )
        sess = start_session(snap, round_num=1, filter_area="NCS")
        ids = [q.id for q in sess.scope]
        self.assertNotIn("z1", ids)
        self.assertEqual(len(ids), 3)


if __name__ == "__main__":
    unittest.main()
