"""데이터 파이프라인 테스트 — Keep 파싱, 분류, 검수, 파이프라인."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ubermensch.data.note import Note, NoteCategory, NoteType, save_notes, load_notes
from ubermensch.data.keep_parser import KeepParser
from ubermensch.data.classifier import NoteClassifier
from ubermensch.data.pipeline import DataPipeline

FIXTURES = Path(__file__).parent / "fixtures" / "keep_sample"


# ─── Note 모델 테스트 ─────────────────────────────────────────

class TestNote:
    def test_default_values(self):
        n = Note()
        assert n.category == NoteCategory.OTHER
        assert n.note_type == NoteType.UNKNOWN
        assert n.verified is False

    def test_to_dict(self):
        n = Note(id="abc", title="테스트", category=NoteCategory.NCS)
        d = n.to_dict()
        assert d["category"] == "NCS"
        assert d["id"] == "abc"

    def test_from_dict(self):
        d = {"id": "abc", "title": "테스트", "category": "경제학", "note_type": "문제"}
        n = Note.from_dict(d)
        assert n.category == NoteCategory.ECONOMICS
        assert n.note_type == NoteType.PROBLEM

    def test_roundtrip_json(self):
        n = Note(id="test", title="경제학 정리", content="수요공급", category=NoteCategory.ECONOMICS)
        json_str = n.to_json()
        restored = Note.from_json(json_str)
        assert restored.id == n.id
        assert restored.category == NoteCategory.ECONOMICS

    def test_save_and_load(self, tmp_path):
        notes = [
            Note(id="1", title="NCS 수리", category=NoteCategory.NCS),
            Note(id="2", title="경제학 미시", category=NoteCategory.ECONOMICS),
        ]
        path = tmp_path / "notes.json"
        save_notes(notes, path)
        loaded = load_notes(path)
        assert len(loaded) == 2
        assert loaded[0].category == NoteCategory.NCS
        assert loaded[1].category == NoteCategory.ECONOMICS


# ─── KeepParser 테스트 ─────────────────────────────────────────

class TestKeepParser:
    def test_parse_directory(self):
        parser = KeepParser()
        notes = parser.parse_directory(FIXTURES)
        # 6개 파일 중 trashed(1) + empty(1) = 스킵 → 6개 파싱
        assert len(notes) >= 4
        assert parser.stats["total"] >= 6
        assert parser.stats["errors"] == 0

    def test_trashed_skipped(self):
        parser = KeepParser(skip_trashed=True)
        data = {"isTrashed": True, "textContent": "삭제됨", "title": "삭제"}
        result = parser.parse_json(data)
        assert result is None

    def test_trashed_not_skipped(self):
        parser = KeepParser(skip_trashed=False)
        data = {"isTrashed": True, "textContent": "삭제됨", "title": "삭제"}
        result = parser.parse_json(data)
        assert result is not None

    def test_empty_skipped(self):
        parser = KeepParser(skip_empty=True)
        data = {"textContent": "", "title": ""}
        result = parser.parse_json(data)
        assert result is None

    def test_list_content_parsed(self):
        parser = KeepParser()
        note = parser.parse_file(FIXTURES / "list_note.json")
        assert note is not None
        assert "NCS 수리" in note.content
        assert "오답노트" in note.content

    def test_labels_extracted(self):
        parser = KeepParser()
        note = parser.parse_file(FIXTURES / "ncs_math_01.json")
        assert "NCS" in note.labels
        assert "수리" in note.labels

    def test_timestamps_converted(self):
        parser = KeepParser()
        note = parser.parse_file(FIXTURES / "ncs_math_01.json")
        assert note.created_at != ""
        assert "20" in note.created_at  # 2023/2024년도

    def test_id_generated(self):
        parser = KeepParser()
        note = parser.parse_file(FIXTURES / "ncs_math_01.json")
        assert len(note.id) == 12

    def test_parse_text_dump_single(self):
        parser = KeepParser()
        notes = parser.parse_text_dump("수리 문제 풀이\n정답은 3번")
        assert len(notes) == 1

    def test_parse_text_dump_multiple(self):
        parser = KeepParser()
        text = "첫 번째 노트\n내용1\n\n\n\n두 번째 노트\n내용2\n\n\n\n세 번째 노트\n내용3"
        notes = parser.parse_text_dump(text)
        assert len(notes) == 3

    def test_parse_file_returns_note(self):
        parser = KeepParser()
        note = parser.parse_file(FIXTURES / "econ_micro_01.json")
        assert note is not None
        assert "탄력성" in note.content
        assert "경제학" in note.labels

    def test_nonexistent_directory_raises(self):
        parser = KeepParser()
        with pytest.raises(NotADirectoryError):
            parser.parse_directory("/nonexistent/path")


# ─── NoteClassifier 테스트 ─────────────────────────────────────

class TestNoteClassifier:
    @pytest.fixture
    def classifier(self):
        return NoteClassifier()

    @pytest.fixture
    def parsed_notes(self):
        parser = KeepParser()
        return parser.parse_directory(FIXTURES)

    def test_ncs_math_classified(self, classifier):
        note = Note(
            title="수리 오답정리",
            content="NCS 수리 증가율 문제 계산 비율",
            labels=["NCS"],
        )
        result = classifier.classify(note)
        assert result.category == NoteCategory.NCS
        assert result.subject == "수리"

    def test_ncs_language_classified(self, classifier):
        note = Note(
            title="언어 독해",
            content="독해 문제 지문을 읽고 주제를 고르시오 문맥 파악",
            labels=["NCS"],
        )
        result = classifier.classify(note)
        assert result.category == NoteCategory.NCS
        assert result.subject == "언어"

    def test_economics_micro_classified(self, classifier):
        note = Note(
            title="미시경제학",
            content="수요 공급 탄력성 균형 가격 미시 효용",
            labels=["경제학"],
        )
        result = classifier.classify(note)
        assert result.category == NoteCategory.ECONOMICS
        assert result.subject == "미시"

    def test_economics_macro_classified(self, classifier):
        note = Note(
            title="거시경제학",
            content="GDP 국민소득 IS-LM 거시 통화정책 재정정책 총수요",
            labels=["경제학", "거시"],
        )
        result = classifier.classify(note)
        assert result.category == NoteCategory.ECONOMICS
        assert result.subject == "거시"

    def test_problem_type_detected(self, classifier):
        note = Note(content="다음 중 올바른 것을 고르시오. 1. ... 2. ...")
        classifier.classify(note)
        assert note.note_type == NoteType.PROBLEM

    def test_solution_type_detected(self, classifier):
        note = Note(content="풀이: x = 100 따라서 정답은 3번")
        classifier.classify(note)
        assert note.note_type == NoteType.SOLUTION

    def test_wrong_answer_type_detected(self, classifier):
        note = Note(content="오답 분석: 틀린 이유는 주의할 점을 놓쳤음")
        classifier.classify(note)
        assert note.note_type == NoteType.WRONG_ANSWER

    def test_concept_type_detected(self, classifier):
        note = Note(content="개념 정리: 수요의 정의는 암기 요약")
        classifier.classify(note)
        assert note.note_type == NoteType.CONCEPT

    def test_tags_generated(self, classifier):
        note = Note(content="NCS 수리 문제 계산", labels=["NCS"])
        classifier.classify(note)
        assert len(note.tags) > 0

    def test_difficulty_hard(self, classifier):
        note = Note(content="고난도 심화 응용 문제")
        classifier.classify(note)
        assert note.difficulty == "상"

    def test_difficulty_easy(self, classifier):
        note = Note(content="기본 기초 암기 문제")
        classifier.classify(note)
        assert note.difficulty == "하"

    def test_classify_all(self, classifier, parsed_notes):
        results = classifier.classify_all(parsed_notes)
        assert len(results) == len(parsed_notes)
        # At least some should be classified as NCS or Economics
        categories = {n.category for n in results}
        assert NoteCategory.NCS in categories or NoteCategory.ECONOMICS in categories

    def test_memo_classified_as_other_or_schedule(self, classifier):
        note = Note(
            title="일정 메모",
            content="내일 도서관 9시 가기",
        )
        classifier.classify(note)
        # Should not be NCS or Economics
        assert note.category in (NoteCategory.OTHER, NoteCategory.MIXED)

    def test_mixed_classification(self, classifier):
        note = Note(content="NCS 수리 수요 공급 경제학 미시 계산 비율")
        classifier.classify(note)
        assert note.category == NoteCategory.MIXED


# ─── DataPipeline 테스트 ───────────────────────────────────────

class TestDataPipeline:
    def test_run_from_directory(self):
        pipeline = DataPipeline()
        results = pipeline.run_from_directory(FIXTURES)
        assert len(results) >= 3
        assert pipeline.stats.total_input >= 6
        assert pipeline.stats.verified > 0

    def test_run_from_text(self):
        text = (
            "NCS 수리 오답정리\n"
            "문제: 증가율 계산에서 기준 혼동\n"
            "풀이: 전년 대비이므로 전년이 기준\n"
            "\n\n\n"
            "경제학 미시 수요탄력성\n"
            "개념: 가격 변화에 대한 수요량 변화 비율\n"
            "탄력적: 대체재 多, 사치품"
        )
        pipeline = DataPipeline()
        results = pipeline.run_from_text(text)
        assert len(results) == 2

    def test_run_from_notes(self):
        notes = [
            Note(id="1", title="NCS 수리", content="수리 계산 비율 증가율 문제"),
            Note(id="2", title="경제학", content="수요 공급 미시 균형 탄력성"),
        ]
        pipeline = DataPipeline()
        results = pipeline.run(notes)
        assert len(results) == 2
        assert all(n.verified for n in results)

    def test_short_content_rejected(self):
        notes = [
            Note(id="1", title="", content="짧음"),  # < 10자
            Note(id="2", title="NCS", content="NCS 수리 문제 풀이 정답 계산 증가율"),
        ]
        pipeline = DataPipeline(min_content_length=10)
        results = pipeline.run(notes)
        assert len(results) == 1
        assert pipeline.stats.rejected == 1

    def test_duplicates_removed(self):
        notes = [
            Note(id="1", content="동일한 내용의 NCS 수리 문제 풀이 정리"),
            Note(id="2", content="동일한 내용의 NCS 수리 문제 풀이 정리"),
            Note(id="3", content="다른 내용의 경제학 미시 수요 공급 정리"),
        ]
        pipeline = DataPipeline()
        results = pipeline.run(notes)
        assert len(results) == 2
        assert pipeline.stats.duplicates_removed == 1

    def test_stats_summary(self):
        pipeline = DataPipeline()
        pipeline.run_from_directory(FIXTURES)
        summary = pipeline.stats.summary()
        assert "입력:" in summary
        assert "파싱:" in summary
        assert "검수 통과:" in summary

    def test_save_results(self, tmp_path):
        pipeline = DataPipeline()
        pipeline.run_from_directory(FIXTURES)
        path = pipeline.save_results(tmp_path / "output.json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert len(data) > 0

    def test_save_stats(self, tmp_path):
        pipeline = DataPipeline()
        pipeline.run_from_directory(FIXTURES)
        path = pipeline.save_stats(tmp_path / "stats.json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert "verified" in data

    def test_pipeline_categories_tracked(self):
        pipeline = DataPipeline()
        pipeline.run_from_directory(FIXTURES)
        stats = pipeline.stats
        assert len(stats.by_category) > 0

    def test_results_property(self):
        pipeline = DataPipeline()
        results = pipeline.run_from_directory(FIXTURES)
        assert pipeline.results == results

    def test_no_duplicates_mode_off(self):
        notes = [
            Note(id="1", content="동일한 내용의 NCS 수리 문제 풀이 정리"),
            Note(id="2", content="동일한 내용의 NCS 수리 문제 풀이 정리"),
        ]
        pipeline = DataPipeline(remove_duplicates=False)
        results = pipeline.run(notes)
        assert len(results) == 2
        assert pipeline.stats.duplicates_removed == 0
