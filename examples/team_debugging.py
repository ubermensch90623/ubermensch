"""Übermensch 사용 예제: Agent Teams - 경쟁 가설 디버깅

여러 DebuggerAgent가 서로 다른 가설을 세우고 검증하며,
DevilsAdvocateAgent가 가설을 교차 비판합니다.

사용법:
    export ANTHROPIC_API_KEY="your-api-key"
    python examples/team_debugging.py
"""

import asyncio
import logging

from ubermensch.agents.debugger import DebuggerAgent
from ubermensch.agents.devils_advocate import DevilsAdvocateAgent
from ubermensch.core.team import AgentTeam

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

BUG_REPORT = """
## Bug Report

**증상**: 사용자가 메시지를 보내면 앱이 1개 메시지 후 연결이 끊김.
웹소켓 연결이 첫 메시지 전송 직후 종료됨.

**에러 로그**:
```
2026-02-24 15:30:01 INFO  WebSocket connected: user_123
2026-02-24 15:30:05 INFO  Message received from user_123: "Hello"
2026-02-24 15:30:05 INFO  Broadcasting message to 5 clients
2026-02-24 15:30:05 ERROR Connection closed unexpectedly: user_123
2026-02-24 15:30:05 WARN  Failed to send ACK to user_123: connection already closed
```

**관련 코드**:
```python
async def handle_message(ws, message):
    data = json.loads(message)
    await broadcast(data)
    await ws.send(json.dumps({"type": "ack", "id": data["id"]}))

async def broadcast(data):
    for client in connected_clients:
        await client.send(json.dumps(data))
```

**환경**: Python 3.11, websockets 12.0, Ubuntu 22.04
**재현율**: 100% (모든 사용자)
"""


async def main():
    team = AgentTeam(name="debug-team")

    # 여러 DebuggerAgent를 다른 관점으로 스폰
    team.spawn_teammate(DebuggerAgent(name="debugger_network"))
    team.spawn_teammate(DebuggerAgent(name="debugger_logic"))
    team.spawn_teammate(DebuggerAgent(name="debugger_concurrency"))
    team.spawn_teammate(DevilsAdvocateAgent())

    # Lead가 자동으로 태스크 분해
    result = await team.run_team(
        user_request=(
            f"다음 버그를 경쟁 가설 방법론으로 조사해주세요. "
            f"각 디버거는 서로 다른 가설을 세우고, "
            f"Devil's Advocate는 가설들을 교차 검증해주세요.\n\n{BUG_REPORT}"
        ),
    )

    print("\n" + "=" * 60)
    print("디버깅 결과 종합:")
    print("=" * 60)
    print(result["synthesis"])

    await team.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
