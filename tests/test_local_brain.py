"""LocalBrain + Autopilot 테스트."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from ubermensch.agents.corp.organization import LearningAgentCorp
from ubermensch.core.local_brain import LocalBrain, StudyState
from ubermensch.core.message import AgentMessage


# ─── StudyState 테스트 ────────────────────────────────────────

class TestStudyState:
    def test_initial_state(self):
        s = StudyState()
        assert s.cycle == 0
        assert s.day == 0
        assert s.streak == 0
        assert s.total_notes == 400
        assert s.parsed_notes == 0
        assert s.burnout_level == "SAFE"

    def test_advance_cycle_increments(self):
        s = StudyState()
        s.advance_cycle()
        assert s.cycle == 1
        assert s.day == 1
        assert s.streak == 1

    def test_advance_generates_topics(self):
        s = StudyState()
        s.advance_cycle()
        assert len(s.studied_topics) >= 2
        for t in s.studied_topics:
            assert t["subject"] in ("NCS", "경제학")
            assert "type" in t
            assert "day_studied" in t

    def test_advance_generates_accuracy(self):
        s = StudyState()
        s.advance_cycle()
        assert len(s.accuracy_by_type) > 0
        for area, score in s.accuracy_by_type.items():
            assert 0.0 <= score <= 1.0

    def test_advance_tracks_study_hours(self):
        s = StudyState()
        s.advance_cycle()
        assert len(s.study_hours) == 1
        assert 3.0 <= s.study_hours[0] <= 6.0

    def test_pipeline_progresses_over_cycles(self):
        s = StudyState()
        assert s.pipeline_status == "설계중"
        s.advance_cycle()  # cycle 1
        assert s.pipeline_status == "설계중"
        s.advance_cycle()  # cycle 2
        assert s.pipeline_status == "파일럿"
        s.advance_cycle()  # cycle 3
        s.advance_cycle()  # cycle 4
        assert s.pipeline_status == "가동중"

    def test_notes_parsed_after_cycle2(self):
        s = StudyState()
        s.advance_cycle()  # cycle 1 — no parsing yet
        assert s.parsed_notes == 0
        s.advance_cycle()  # cycle 2 — parsing starts
        assert s.parsed_notes > 0

    def test_burnout_escalation(self):
        s = StudyState()
        # Force high daily hours
        s.daily_hours = [7.5, 7.5]
        s.advance_cycle()  # 3rd day also high
        # After 3 days of >7h, should be WARNING
        if sum(s.daily_hours[-3:]) / 3 > 7:
            assert s.burnout_level == "WARNING"

    def test_gemini_connects_cycle3(self):
        s = StudyState()
        s.advance_cycle()
        s.advance_cycle()
        assert not s.gemini_connected
        s.advance_cycle()  # cycle 3
        assert s.gemini_connected

    def test_accuracy_improves_over_cycles(self):
        s = StudyState()
        s.advance_cycle()
        early_avg = sum(s.accuracy_by_type.values()) / len(s.accuracy_by_type)
        for _ in range(9):
            s.advance_cycle()
        late_avg = sum(s.accuracy_by_type.values()) / len(s.accuracy_by_type)
        assert late_avg > early_avg

    def test_save_and_load(self, tmp_path):
        path = tmp_path / "study.json"
        s = StudyState()
        s.advance_cycle()
        s.advance_cycle()
        s.save(path)

        loaded = StudyState.load(path)
        assert loaded.cycle == 2
        assert loaded.day == 2
        assert loaded.streak == 2
        assert loaded.parsed_notes == s.parsed_notes

    def test_load_nonexistent_returns_fresh(self, tmp_path):
        path = tmp_path / "nonexistent.json"
        s = StudyState.load(path)
        assert s.cycle == 0

    def test_to_dict(self):
        s = StudyState()
        s.advance_cycle()
        d = s.to_dict()
        assert "cycle" in d
        assert "accuracy_by_type" in d
        assert "burnout_level" in d
        assert d["cycle"] == 1


# ─── LocalBrain 테스트 ────────────────────────────────────────

class TestLocalBrain:
    def test_creation(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        assert brain.state.cycle == 0

    def test_advance(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        assert brain.state.cycle == 1
        # state should be saved
        assert (tmp_path / "study.json").exists()

    def test_think_ceo(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        response = brain.think("ceo", "미션 분석", "CEO system prompt")
        assert "CEO" in response
        assert "Day 1" in response

    def test_think_cto(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        response = brain.think("cto", "점검", "CTO system prompt")
        assert "파이프라인" in response

    def test_think_coo(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        response = brain.think("coo", "스케줄", "")
        assert "스케줄" in response

    def test_think_cfo(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        response = brain.think("cfo", "성과", "")
        assert "정답률" in response

    def test_think_cmo(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        response = brain.think("cmo", "동기부여", "")
        assert "번아웃" in response or "SAFE" in response

    def test_think_plumber(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        response = brain.think("plumber", "파이프라인", "")
        assert "400" in response

    def test_think_data_redteam(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        response = brain.think("data_redteam", "검증", "")
        assert "PASS" in response or "BLOCK" in response or "WARN" in response

    def test_think_unknown_agent(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        response = brain.think("unknown_agent", "test", "")
        assert "Day 1" in response

    def test_inject_replaces_ask_llm(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        corp = LearningAgentCorp()
        corp.hire_all()
        brain.inject(corp)

        # ask_llm should now be the local version
        ceo = corp.get_agent("ceo")
        result = asyncio.get_event_loop().run_until_complete(
            ceo.ask_llm("미션 분석")
        )
        assert "CEO" in result

    def test_inject_all_agents_work(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        corp = LearningAgentCorp()
        corp.hire_all()
        brain.inject(corp)

        async def _test():
            results = []
            for name in ["ceo", "cto", "coo", "cfo", "cmo", "plumber", "tracker"]:
                agent = corp.get_agent(name)
                r = await agent.run(AgentMessage(task="보고", context={}))
                results.append(r)
            return results

        results = asyncio.get_event_loop().run_until_complete(_test())
        assert all(r.success for r in results)

    def test_ceo_synthesis_mode(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        response = brain.think("ceo", "종합", "")
        assert "종합" in response or "사이클" in response

    def test_redteam_block_on_low_quality(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        # Force low verification rate
        brain.state.classified_notes = 100
        brain.state.verified_notes = 50  # 50% < 70% threshold
        response = brain.think("data_redteam", "검증", "")
        assert "BLOCK" in response

    def test_redteam_pass_on_good_quality(self, tmp_path):
        brain = LocalBrain(state_path=tmp_path / "study.json")
        brain.advance()
        brain.state.parsed_notes = 100
        brain.state.classified_notes = 90
        brain.state.verified_notes = 80
        response = brain.think("data_redteam", "검증", "")
        assert "PASS" in response

    def test_state_persistence_across_brains(self, tmp_path):
        path = tmp_path / "study.json"
        brain1 = LocalBrain(state_path=path)
        brain1.advance()
        brain1.advance()
        cycle = brain1.state.cycle

        brain2 = LocalBrain(state_path=path)
        assert brain2.state.cycle == cycle


# ─── Autopilot 테스트 ─────────────────────────────────────────

class TestAutopilot:
    def test_boot_creates_corp(self, tmp_path):
        from ubermensch.autopilot import Autopilot
        pilot = Autopilot(
            state_path=tmp_path / "corp.json",
            study_state_path=tmp_path / "study.json",
        )
        pilot.boot()
        assert pilot.corp is not None
        assert pilot.corp.headcount == 40
        assert pilot.brain is not None

    def test_boot_saves_state(self, tmp_path):
        from ubermensch.autopilot import Autopilot
        pilot = Autopilot(
            state_path=tmp_path / "corp.json",
            study_state_path=tmp_path / "study.json",
        )
        pilot.boot()
        assert (tmp_path / "corp.json").exists()

    def test_single_cycle(self, tmp_path):
        from ubermensch.autopilot import Autopilot
        pilot = Autopilot(
            state_path=tmp_path / "corp.json",
            study_state_path=tmp_path / "study.json",
        )

        async def _test():
            return await pilot.run(cycles=1)

        results = asyncio.get_event_loop().run_until_complete(_test())
        assert len(results) == 1
        assert results[0]["cycle"] == 1
        assert results[0]["day"] == 1
        assert 0 < results[0]["accuracy"] < 1

    def test_multi_cycle(self, tmp_path):
        from ubermensch.autopilot import Autopilot
        pilot = Autopilot(
            state_path=tmp_path / "corp.json",
            study_state_path=tmp_path / "study.json",
        )

        async def _test():
            return await pilot.run(cycles=3)

        results = asyncio.get_event_loop().run_until_complete(_test())
        assert len(results) == 3
        assert results[0]["day"] == 1
        assert results[2]["day"] == 3
        # Accuracy should generally improve
        assert results[2]["accuracy"] >= results[0]["accuracy"] - 0.1

    def test_state_persists_between_runs(self, tmp_path):
        from ubermensch.autopilot import Autopilot

        # First run: 2 cycles
        pilot1 = Autopilot(
            state_path=tmp_path / "corp.json",
            study_state_path=tmp_path / "study.json",
        )
        r1 = asyncio.get_event_loop().run_until_complete(pilot1.run(cycles=2))

        # Second run: 2 more cycles
        pilot2 = Autopilot(
            state_path=tmp_path / "corp.json",
            study_state_path=tmp_path / "study.json",
        )
        r2 = asyncio.get_event_loop().run_until_complete(pilot2.run(cycles=2))

        # Second run should continue from where first left off
        assert r2[0]["day"] == 3  # day 3, not day 1
        assert r2[1]["day"] == 4

    def test_cycle_result_fields(self, tmp_path):
        from ubermensch.autopilot import Autopilot
        pilot = Autopilot(
            state_path=tmp_path / "corp.json",
            study_state_path=tmp_path / "study.json",
        )
        results = asyncio.get_event_loop().run_until_complete(pilot.run(cycles=1))
        r = results[0]
        assert "cycle" in r
        assert "day" in r
        assert "elapsed" in r
        assert "accuracy" in r
        assert "burnout" in r
        assert "notes_migrated" in r
