"""Übermensch 사용 예제: Agent Teams - 병렬 코드 리뷰

3명의 리뷰어가 각각 다른 관점에서 코드를 동시에 리뷰하고,
Devil's Advocate가 결과를 교차 검증합니다.

사용법:
    export ANTHROPIC_API_KEY="your-api-key"
    python examples/team_code_review.py
"""

import asyncio
import logging

from ubermensch.agents.devils_advocate import DevilsAdvocateAgent
from ubermensch.agents.reviewers import (
    CodeReviewerAgent,
    PerformanceReviewerAgent,
    SecurityReviewerAgent,
)
from ubermensch.core.team import AgentTeam

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# 리뷰 대상 코드 예시
SAMPLE_CODE = """
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect("users.db")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    db = get_db()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = db.execute(query).fetchone()

    if user:
        return jsonify({"token": username + "_token_123", "status": "ok"})
    return jsonify({"status": "fail"}), 401

@app.route("/users")
def list_users():
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    return jsonify([dict(row) for row in users])

@app.route("/search")
def search():
    q = request.args.get("q", "")
    db = get_db()
    results = db.execute(f"SELECT * FROM users WHERE name LIKE '%{q}%'").fetchall()
    return jsonify(results)
"""


async def main():
    # 1. 팀 생성
    team = AgentTeam(name="code-review-team")

    # 2. 팀원 등록 (3 리뷰어 + 1 Devil's Advocate = 4명)
    team.spawn_teammate(SecurityReviewerAgent())
    team.spawn_teammate(PerformanceReviewerAgent())
    team.spawn_teammate(CodeReviewerAgent())
    team.spawn_teammate(DevilsAdvocateAgent())

    print(f"Team created: {team.teammate_names}")

    # 3. 태스크 직접 생성 (auto_plan 대신 수동 태스크 생성)
    tasks = await team.create_tasks([
        {
            "title": "Security review",
            "description": (
                f"Review this code for security vulnerabilities:\n```\n{SAMPLE_CODE}\n```"
            ),
            "priority": 10,
        },
        {
            "title": "Performance review",
            "description": (
                f"Review this code for performance issues:\n```\n{SAMPLE_CODE}\n```"
            ),
            "priority": 8,
        },
        {
            "title": "Code quality review",
            "description": (
                f"Review this code for quality and best practices:\n```\n{SAMPLE_CODE}\n```"
            ),
            "priority": 8,
        },
        {
            "title": "Cross-validate findings",
            "description": (
                "After other reviews complete, challenge and validate the findings. "
                "Look for overlooked issues and false positives."
            ),
            "priority": 5,
            "depends_on": [t.id for t in tasks] if 'tasks' in dir() else [],
        },
    ])

    # Devil's Advocate 태스크에 다른 태스크 의존성 추가
    tasks[-1].depends_on = [t.id for t in tasks[:-1]]

    # 4. 팀 실행 (auto_plan=False: 수동 생성한 태스크 사용)
    result = await team.run_team(
        user_request="이 Flask 코드를 보안/성능/품질 관점에서 종합 리뷰해주세요.",
        auto_plan=False,
    )

    # 5. 결과 출력
    print("\n" + "=" * 60)
    print("팀 리뷰 결과 종합:")
    print("=" * 60)
    print(result["synthesis"])

    print(f"\n완료된 태스크: {len([r for r in result['results'] if r.success])}")
    print(f"팀 메시지 수: {len(result['messages'])}")

    # 6. 정리
    await team.cleanup()


async def auto_plan_example():
    """Lead가 LLM으로 자동 태스크 분해하는 예제."""

    team = AgentTeam(name="auto-review-team")
    team.spawn_teammate(SecurityReviewerAgent())
    team.spawn_teammate(PerformanceReviewerAgent())
    team.spawn_teammate(CodeReviewerAgent())

    # auto_plan=True (기본값): Lead가 자동으로 태스크 분해
    result = await team.run_team(
        "Analyze the authentication system for security, performance, "
        "and code quality issues."
    )

    print(result["synthesis"])
    await team.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
