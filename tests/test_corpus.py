"""corpus 모듈 단위 테스트 (audit-v2 권고)."""
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

from exam_analyzer.corpus.models import (  # noqa: E402
    Attempt,
    Choice,
    CorpusSnapshot,
    Provenance,
    Question,
    ReviewRound,
    generate_question_id,
    question_from_dict,
    question_to_dict,
    snapshot_from_dict,
    snapshot_to_dict,
)
from exam_analyzer.corpus.storage import (  # noqa: E402
    add_question,
    default_corpus_path,
    find_question,
    load_corpus,
    remove_question,
    save_corpus,
)


def _sample_question() -> Question:
    return Question(
        id=generate_question_id("primary", "서민금융진흥원", "NCS/의사소통", "주제 찾기 지문"),
        kind="primary",
        agency="서민금융진흥원",
        area="NCS/의사소통",
        subtype="주제찾기",
        question_text="주제 찾기 지문",
        choices=[
            Choice(index=1, text="보기1"),
            Choice(index=2, text="보기2", is_correct=True),
            Choice(index=3, text="보기3"),
        ],
        correct_index=2,
        provenance=Provenance(
            source_type="ebook",
            source_name="예시 기출 이북",
            source_citation="p.42",
            source_date="2025-01-01",
        ),
    )


class TestModels(unittest.TestCase):
    def test_generate_id_deterministic(self) -> None:
        a = generate_question_id("primary", "X", "Y", "Z..........")
        b = generate_question_id("primary", "X", "Y", "Z..........")
        self.assertEqual(a, b)
        self.assertEqual(len(a), 10)

    def test_id_changes_on_content(self) -> None:
        a = generate_question_id("primary", "X", "Y", "첫번째 문항")
        b = generate_question_id("primary", "X", "Y", "두번째 문항")
        self.assertNotEqual(a, b)

    def test_question_round_trip(self) -> None:
        q = _sample_question()
        d = question_to_dict(q)
        q2 = question_from_dict(d)
        self.assertEqual(q2.id, q.id)
        self.assertEqual(q2.question_text, q.question_text)
        self.assertEqual(len(q2.choices), 3)
        self.assertTrue(q2.choices[1].is_correct)
        self.assertEqual(q2.provenance.source_name, "예시 기출 이북")

    def test_reverse_engineered_fields(self) -> None:
        q = Question(
            id="re_test_01",
            kind="reverse_engineered",
            agency="서민금융진흥원",
            area="직무/법률",
            subtype="조문적용",
            question_text="예상 문항",
            choices=[Choice(index=1, text="a")],
            rationale_chain=["기출책A Q#42", "후기B URL", "법령 §14"],
            confidence="mid",
            counter_arguments=["기출A와 다른 직렬의 문항일 가능성"],
        )
        d = question_to_dict(q)
        q2 = question_from_dict(d)
        self.assertEqual(q2.kind, "reverse_engineered")
        self.assertEqual(len(q2.rationale_chain), 3)
        self.assertEqual(q2.confidence, "mid")
        self.assertEqual(len(q2.counter_arguments), 1)


class TestStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        self.tmp.close()
        self.path = Path(self.tmp.name)
        if self.path.exists():
            self.path.unlink()

    def tearDown(self) -> None:
        if self.path.exists():
            self.path.unlink()

    def test_load_missing_returns_empty(self) -> None:
        snap = load_corpus(self.path)
        self.assertEqual(snap.questions, [])
        self.assertEqual(snap.attempts, [])

    def test_save_load_round_trip(self) -> None:
        snap = CorpusSnapshot()
        q = _sample_question()
        add_question(snap, q)
        save_corpus(snap, self.path)
        loaded = load_corpus(self.path)
        self.assertEqual(len(loaded.questions), 1)
        self.assertEqual(loaded.questions[0].id, q.id)

    def test_add_duplicate_returns_false(self) -> None:
        snap = CorpusSnapshot()
        q = _sample_question()
        self.assertTrue(add_question(snap, q))
        self.assertFalse(add_question(snap, q))
        self.assertEqual(len(snap.questions), 1)

    def test_find_and_remove(self) -> None:
        snap = CorpusSnapshot()
        q = _sample_question()
        add_question(snap, q)
        found = find_question(snap, q.id[:5])
        self.assertIsNotNone(found)
        self.assertEqual(found.id, q.id)
        self.assertTrue(remove_question(snap, q.id))
        self.assertEqual(snap.questions, [])

    def test_utf8_korean_preserved(self) -> None:
        snap = CorpusSnapshot()
        q = _sample_question()
        add_question(snap, q)
        save_corpus(snap, self.path)
        raw = self.path.read_text(encoding="utf-8")
        self.assertIn("서민금융진흥원", raw)
        self.assertIn("주제찾기", raw)

    def test_env_override(self) -> None:
        original = os.environ.get("EXAM_CORPUS_FILE")
        os.environ["EXAM_CORPUS_FILE"] = str(self.path)
        try:
            self.assertEqual(default_corpus_path(), self.path)
        finally:
            if original is None:
                del os.environ["EXAM_CORPUS_FILE"]
            else:
                os.environ["EXAM_CORPUS_FILE"] = original


class TestSnapshot(unittest.TestCase):
    def test_snapshot_full_roundtrip(self) -> None:
        q = _sample_question()
        attempt = Attempt(
            question_id=q.id,
            round_num=1,
            attempted_at="2026-04-16T10:00:00",
            selected_index=2,
            is_correct=True,
            time_spent_sec=45.2,
            confidence="sure",
        )
        round_ = ReviewRound(
            round_num=1,
            started_at="2026-04-16T09:00:00",
            scope_question_ids=[q.id],
        )
        snap = CorpusSnapshot(
            questions=[q], attempts=[attempt], rounds=[round_]
        )
        d = snapshot_to_dict(snap)
        self.assertEqual(d["version"], 1)
        snap2 = snapshot_from_dict(d)
        self.assertEqual(len(snap2.questions), 1)
        self.assertEqual(len(snap2.attempts), 1)
        self.assertEqual(len(snap2.rounds), 1)
        self.assertEqual(snap2.attempts[0].selected_index, 2)
        self.assertEqual(snap2.rounds[0].round_num, 1)


if __name__ == "__main__":
    unittest.main()
