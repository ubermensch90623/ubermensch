#!/usr/bin/env python3
"""
NCS 공부 도우미 - Claude Code에서 직접 실행하는 학습 도구

사용법 (Claude Code에서):
  python study/ncs-study-tool.py quiz             # 랜덤 5문제 퀴즈
  python study/ncs-study-tool.py quiz 10           # 10문제 퀴즈
  python study/ncs-study-tool.py quiz --subject 수리  # 수리능력만
  python study/ncs-study-tool.py quiz --difficulty 하  # 쉬운 문제만
  python study/ncs-study-tool.py stats             # 내 공부 현황
  python study/ncs-study-tool.py weak              # 취약 과목 분석
  python study/ncs-study-tool.py review            # 틀린 문제 복습
"""

import json
import random
import sys
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
QUESTIONS_DIR = BASE_DIR / "questions"
TRACKER_PATH = BASE_DIR / "progress" / "tracker.json"


def load_questions(subject_filter=None, difficulty_filter=None):
    """문제 파일 로드"""
    all_questions = []
    for qfile in sorted(QUESTIONS_DIR.glob("*.json")):
        with open(qfile, encoding="utf-8") as f:
            data = json.load(f)
        subject = data["subject"]
        if subject_filter and subject_filter not in subject:
            continue
        for q in data["questions"]:
            q["subject"] = subject
            if difficulty_filter and q["difficulty"] != difficulty_filter:
                continue
            all_questions.append(q)
    return all_questions


def load_tracker():
    """진행 상황 로드"""
    with open(TRACKER_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_tracker(tracker):
    """진행 상황 저장"""
    with open(TRACKER_PATH, "w", encoding="utf-8") as f:
        json.dump(tracker, f, ensure_ascii=False, indent=2)


def run_quiz(count=5, subject=None, difficulty=None):
    """퀴즈 실행 - 결과를 JSON으로 출력 (Claude가 읽어서 사용자에게 보여줌)"""
    questions = load_questions(subject, difficulty)
    if not questions:
        print(json.dumps({"error": "조건에 맞는 문제가 없습니다."}, ensure_ascii=False))
        return

    selected = random.sample(questions, min(count, len(questions)))
    quiz_data = {
        "type": "quiz",
        "count": len(selected),
        "subject_filter": subject,
        "difficulty_filter": difficulty,
        "questions": []
    }

    for i, q in enumerate(selected, 1):
        quiz_data["questions"].append({
            "number": i,
            "id": q["id"],
            "subject": q["subject"],
            "difficulty": q["difficulty"],
            "type": q["type"],
            "question": q["question"],
            "choices": q["choices"],
            "answer": q["answer"],
            "explanation": q["explanation"]
        })

    print(json.dumps(quiz_data, ensure_ascii=False, indent=2))


def record_result(results_json):
    """퀴즈 결과 기록
    results_json: [{"id": "comm-001", "correct": true}, ...]
    """
    tracker = load_tracker()
    results = json.loads(results_json)
    questions = load_questions()
    q_map = {q["id"]: q for q in questions}

    session = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(results),
        "correct": sum(1 for r in results if r["correct"]),
        "details": []
    }

    for r in results:
        qid = r["id"]
        q = q_map.get(qid, {})
        subject = q.get("subject", "")
        difficulty = q.get("difficulty", "")
        qtype = q.get("type", "")

        session["details"].append({
            "id": qid,
            "subject": subject,
            "difficulty": difficulty,
            "type": qtype,
            "correct": r["correct"]
        })

        # 과목별 통계 업데이트
        if subject in tracker["subject_stats"]:
            stats = tracker["subject_stats"][subject]
            stats["total_attempted"] += 1
            if r["correct"]:
                stats["total_correct"] += 1
            if difficulty in stats["by_difficulty"]:
                stats["by_difficulty"][difficulty]["attempted"] += 1
                if r["correct"]:
                    stats["by_difficulty"][difficulty]["correct"] += 1
            # 틀린 유형 기록
            if not r["correct"] and qtype not in stats["weak_types"]:
                stats["weak_types"].append(qtype)

    tracker["sessions"].append(session)

    # 전체 정답률 계산
    total_a = sum(s["total_attempted"] for s in tracker["subject_stats"].values())
    total_c = sum(s["total_correct"] for s in tracker["subject_stats"].values())
    tracker["overall_accuracy"] = round(total_c / total_a * 100, 1) if total_a > 0 else 0

    # 예상 점수 (50문항 기준)
    tracker["estimated_score"] = round(tracker["overall_accuracy"] / 100 * 50 * 2, 1)

    save_tracker(tracker)
    print(json.dumps({
        "type": "result_saved",
        "session_score": f"{session['correct']}/{session['total']}",
        "overall_accuracy": tracker["overall_accuracy"],
        "estimated_score": tracker["estimated_score"]
    }, ensure_ascii=False, indent=2))


def show_stats():
    """학습 현황 출력"""
    tracker = load_tracker()
    stats = {
        "type": "stats",
        "start_date": tracker["start_date"],
        "total_sessions": len(tracker["sessions"]),
        "overall_accuracy": tracker["overall_accuracy"],
        "estimated_score": tracker["estimated_score"],
        "target_score": tracker["target_score"],
        "subjects": {}
    }

    for subject, data in tracker["subject_stats"].items():
        if data["total_attempted"] > 0:
            accuracy = round(data["total_correct"] / data["total_attempted"] * 100, 1)
        else:
            accuracy = 0
        stats["subjects"][subject] = {
            "attempted": data["total_attempted"],
            "correct": data["total_correct"],
            "accuracy": accuracy,
            "by_difficulty": data["by_difficulty"],
            "weak_types": data["weak_types"]
        }

    print(json.dumps(stats, ensure_ascii=False, indent=2))


def show_weak():
    """취약 과목 분석"""
    tracker = load_tracker()
    analysis = {"type": "weak_analysis", "recommendations": []}

    for subject, data in tracker["subject_stats"].items():
        if data["total_attempted"] == 0:
            analysis["recommendations"].append({
                "subject": subject,
                "message": "아직 풀어본 문제가 없습니다. 먼저 쉬운(하) 문제부터 시작하세요.",
                "priority": "시작 필요"
            })
            continue

        accuracy = data["total_correct"] / data["total_attempted"] * 100

        # 난이도별 분석
        for diff in ["하", "중", "상"]:
            d = data["by_difficulty"][diff]
            if d["attempted"] > 0:
                diff_acc = d["correct"] / d["attempted"] * 100
                if diff in ["하", "중"] and diff_acc < 85:
                    analysis["recommendations"].append({
                        "subject": subject,
                        "difficulty": diff,
                        "accuracy": round(diff_acc, 1),
                        "message": f"{subject}의 {diff} 난이도 정답률이 {diff_acc:.0f}%입니다. 85% 이상이 되도록 반복 연습이 필요합니다.",
                        "priority": "높음" if diff == "하" else "중간"
                    })

        if data["weak_types"]:
            analysis["recommendations"].append({
                "subject": subject,
                "message": f"자주 틀리는 유형: {', '.join(data['weak_types'])}",
                "priority": "집중 학습"
            })

    if not analysis["recommendations"]:
        analysis["recommendations"].append({
            "message": "전 과목 양호합니다! 고난이도(상) 문제에 도전해보세요.",
            "priority": "좋음"
        })

    print(json.dumps(analysis, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "type": "help",
            "commands": {
                "quiz": "랜덤 문제 풀기 (기본 5문제)",
                "quiz N": "N문제 풀기",
                "quiz --subject 수리": "특정 과목만",
                "quiz --difficulty 하": "특정 난이도만",
                "stats": "학습 현황 보기",
                "weak": "취약 과목 분석",
                "record '{결과JSON}'": "결과 기록"
            }
        }, ensure_ascii=False, indent=2))
        return

    cmd = sys.argv[1]

    if cmd == "quiz":
        count = 5
        subject = None
        difficulty = None
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--subject" and i + 1 < len(sys.argv):
                subject = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--difficulty" and i + 1 < len(sys.argv):
                difficulty = sys.argv[i + 1]
                i += 2
            elif sys.argv[i].isdigit():
                count = int(sys.argv[i])
                i += 1
            else:
                i += 1
        run_quiz(count, subject, difficulty)

    elif cmd == "stats":
        show_stats()

    elif cmd == "weak":
        show_weak()

    elif cmd == "record" and len(sys.argv) > 2:
        record_result(sys.argv[2])

    else:
        print(json.dumps({"error": f"알 수 없는 명령: {cmd}"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
