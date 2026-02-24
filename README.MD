# Übermensch

멀티 에이전트 오케스트레이션 프레임워크. Claude API 기반으로 자료 조사, 웹 크롤링, 자동화를 수행합니다.

## 아키텍처

**Subagents 패턴**: Main Agent가 서브에이전트를 생성하고 병렬로 작업을 위임합니다.

```
Main Agent (Orchestrator)
├── Researcher Agent  ← 웹 검색/크롤링으로 정보 수집
├── Summarizer Agent  ← 수집된 정보 요약
└── (확장 가능)       ← 커스텀 에이전트 추가
```

## 설치

```bash
pip install -e .
```

## 사용법

```python
import asyncio
from ubermensch import SubagentOrchestrator
from ubermensch.agents import ResearcherAgent, SummarizerAgent

async def main():
    orchestrator = SubagentOrchestrator()
    orchestrator.register_agent(ResearcherAgent())
    orchestrator.register_agent(SummarizerAgent())

    result = await orchestrator.run("AI 에이전트 최신 트렌드를 조사해줘")
    print(result)

asyncio.run(main())
```

## 요구사항

- Python >= 3.11
- `ANTHROPIC_API_KEY` 환경변수 설정 필요
