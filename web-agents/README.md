<div align="center">

<!-- title -->

# Awesome Web Agents


<p align="center">
  <a href="https://awesome.re" target="_blank">
    <img src="https://awesome.re/badge.svg">
  </a>
  <a href="https://twitter.com/steeldotdev" target="_blank">
    <img src="https://img.shields.io/twitter/follow/steeldotdev.svg?logo=twitter">
  </a>
  <a href="https://discord.gg/steel-dev" target="_blank">
			<img src="https://img.shields.io/static/v1?label=&message=Join%20the%20discord&color=mediumslateblue">
		</a>
<!--   <a href="https://github.com/steel-dev/awesome-web-agents/actions/workflows/lint.yaml" target="_blank">
    <img src="https://github.com/steel-dev/awesome-web-agents/actions/workflows/lint.yaml/badge.svg">
  </a>-->
</p>

<!-- subtitle -->

A curated list of tools, frameworks, and resources for building AI agents that can browse and interact with the web.

</div>

<h2>About Steel</h2>
<!-- image -->

<a href="https://steel.dev" target="_blank" rel="noopener noreferrer">
  <img src="steel_hero.png" />
</a>

Steel is an [open-source](https://github.com/steel-dev/steel-browser) browser API built specifically for AI agents. We make it easy to build AI applications that can effectively interact with the web.

✨ Get started for free [here](https://app.steel.dev).
<!-- description -->
<!-- TOC -->

<h2>Contents</h2>

- [Awesome Web Agents](#awesome-web-agents)
  - [Autonomous Web Agents](#autonomous-web-agents)
    - [AI Browsers](#ai-browsers)
    - [Computer-use Agents](#computer-use-agents)
  - [AI Web Automation Tools](#ai-web-automation-tools)
    - [Dev Tools](#dev-tools)
  - [AI Web Scrapers/Crawlers](#ai-web-scraperscrawlers)
  - [Web Search \& Query Tools](#web-search--query-tools)
  - [Benchmarks \& Research](#benchmarks--research)
  - [Tutorials \& Guides](#tutorials--guides)
  - [금융공기업 NCS 기출문제 모음](#금융공기업-ncs-기출문제-모음)
  - [Interested in implementing Steel?](#interested-in-implementing-steel)
  - [Join the Community](#join-the-community)
  - [Contributing](#contributing)
    - [Contributors](#contributors)

<!-- CONTENT -->

<!--
## Featured (new releases)

- [Apple](https://apple.com) - Apple as a placeholder.
- [Opera Agentic Feature](https://techcrunch.com/2025/03/03/opera-announces-a-new-agentic-feature-for-its-browser/) - Opera announces a new agentic feature for its browser, showcasing innovative web agent integration.

-->

## Autonomous Web Agents

AI agents that autonomously navigate and interact with the web through a user-friendly interface. (a.k.a Browser Agents)

- [Surf.new](https://surf.new) - An open-source playground for chatting with different web agents. ![GitHub Repo stars](https://img.shields.io/github/stars/steel-dev/surf.new?style=social)
- [OpenAI Operator](https://openai.com/index/introducing-operator/) - OpenAI's AI agent that browses the web for you. Now integrated into ChatGPT as agent mode for Pro/Plus/Team users.
- [Browser-Use](https://www.browser-use.com) - SOTA agent and framework that makes the web LLM-friendly. ![GitHub Repo stars](https://img.shields.io/github/stars/Browser-Use/browser-use?style=social)
- [Skyvern-AI](https://www.skyvern.com/) - Framework to automate browser-based workflows. ![GitHub Repo stars](https://img.shields.io/github/stars/Skyvern-AI/skyvern?style=social)
- [Proxy by Convergence](https://convergence.ai) - Proxy is your AI-powered digital assistant that explores the web and executes tasks through simple conversation.
- [Google Project Mariner](https://deepmind.google/technologies/project-mariner/) - A research prototype exploring the future of human-agent interaction, starting with your browser.
- [Runner H](https://www.hcompany.ai/) - Runner H is a state-of-the-art AI agent that will allow anyone to automate complex, cumbersome, multi-step tasks without repetitive and manual input.
- [WebVoyager (Agent)](https://github.com/MinorJerry/WebVoyager) - Vision-enabled web agent. ![GitHub Repo stars](https://img.shields.io/github/stars/MinorJerry/WebVoyager?style=social)
- [AgentGPT](https://github.com/reworkd/AgentGPT) - Deploy autonomous AI agents in your browser. ![GitHub Repo stars](https://img.shields.io/github/stars/reworkd/AgentGPT?style=social)
- [Agent-E](https://github.com/EmergenceAI/Agent-E) - Agent & framework with HTML DOM distillation. ![GitHub Repo stars](https://img.shields.io/github/stars/EmergenceAI/Agent-E?style=social)
- [Kura](https://www.trykura.com/) - Web Agents for the Enterprise.
- [Manus](https://manus.im/) - A general AI agent for long-running tasks across browsers, terminals, and text editors. Acquired by Meta in Dec 2025.
- [doBrowser](https://www.dobrowser.io) - An AI-powered Chrome extension that understands natural language and takes actions in your browser on your behalf.
- [WebSurfer (Autogen)](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.agents.web_surfer.html#autogen_ext.agents.web_surfer.MultimodalWebSurfer) - MultimodalWebSurfer is a multimodal agent that can search the web and visit web pages. ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/autogen?style=social)
- [Magentic-One](https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/) - A generalist multi-agent system for solving complex tasks including surfing the web via Autogen's MultimodalWebSurfer.
- [Harpa.ai](https://harpa.ai/) - An AI-powered Chrome extension & browser agent that understands natural language and takes actions on your behalf.
- [Yutori](https://yutori.com/) - A multi-agent system that executes browser-based tasks in parallel given a natural language prompt.
- [Automina](https://automina.app/) - AI browser automation tool with natural language control.
- [rtrvr.ai](https://www.rtrvr.ai/) - AI Web Agent Chrome Extension that autonomously does tasks, scrapes to Sheets, and calls API's – all with just prompts and your own browser!
- [Nanobrowser](https://nanobrowser.ai) - An open-source & local-first AI web agent Chrome extension with flexible LLM options and multi-agent system. ![GitHub Repo stars](https://img.shields.io/github/stars/nanobrowser/nanobrowser?style=social)
- [Browserable](https://browserable.ai) - An open-source & self-hostable browser automation library for AI agents. ![GitHub Repo stars](https://img.shields.io/github/stars/browserable/browserable?style=social)
- [Tongyi WebAgent](https://github.com/Alibaba-NLP/WebAgent) - WebAgent for Information Seeking bulit by Tongyi Lab, Alibaba Group. ![GitHub Repo stars](https://img.shields.io/github/stars/Alibaba-NLP/WebAgent?style=social)
- [Agent-S](https://github.com/simular-ai/Agent-S) - Open agentic framework that uses computers like a human. Agent S3 surpassed human-level performance on OSWorld (72.60%). ICLR 2025 Best Paper. ![GitHub Repo stars](https://img.shields.io/github/stars/simular-ai/Agent-S?style=social)
- [Amazon Nova Act](https://github.com/aws/nova-act) - Python SDK for building browser agents by AWS. 0.939 on ScreenSpot Web Text benchmark, integrates with Playwright. ![GitHub Repo stars](https://img.shields.io/github/stars/aws/nova-act?style=social)
- [BrowserOS](https://github.com/browseros-ai/BrowserOS) - Open-source Chromium fork that runs AI agents natively. Acts as MCP server with 31 tools. Supports Claude, OpenAI, Gemini, Ollama. ![GitHub Repo stars](https://img.shields.io/github/stars/browseros-ai/BrowserOS?style=social)
- [AutoAgent](https://github.com/HKUDS/AutoAgent) - Fully-automated zero-code LLM agent framework with multi-agent system for research and information retrieval. ![GitHub Repo stars](https://img.shields.io/github/stars/HKUDS/AutoAgent?style=social)
- [Notte](https://github.com/nottelabs/notte) - Framework to build web agents and deploy serverless web automation functions on reliable browser infrastructure. ![GitHub Repo stars](https://img.shields.io/github/stars/nottelabs/notte?style=social)
- [TheAgenticBrowser](https://github.com/TheAgenticAI/TheAgenticBrowser) - Agent-based browser automation using natural language, built on PydanticAI with multi-agent architecture. ![GitHub Repo stars](https://img.shields.io/github/stars/TheAgenticAI/TheAgenticBrowser?style=social)
- [Genspark](https://www.genspark.ai/) - Top-rated AI agent for research that cross-checks multiple sources and produces cited reports.
- [Kortix](https://www.kortix.ai/) - General AI agent platform for autonomous web tasks.

### AI Browsers

AI-native browsers with built-in agent capabilities.

- [ChatGPT Atlas](https://openai.com/index/introducing-operator/) - OpenAI's agentic browser with Agent Mode for autonomous multi-step tasks in every tab.
- [Perplexity Comet](https://www.perplexity.ai/comet) - Chromium-based browser with Perplexity AI built in. Autonomous navigation, form-filling, email/calendar management.
- [Opera Neon](https://www.opera.com) - Agentic browser with four specialized agents: Neon Do (web automation), Neon Make (code/creative), ODRA (deep research), and chat.
- [Google Chrome Auto Browse](https://google.com) - Autonomous task completion via Gemini AI side panel for Premium subscribers. Launched Jan 2026.
- [Fellou](https://fellou.ai/) - First spatial agentic AI browser that automates deep research across logged-in accounts with visual task planning.
- [Dia Browser](https://www.diabrowser.com/) - AI-native browser from The Browser Company (Arc). Acquired by Atlassian in Sept 2025.

### Computer-use Agents

- [Anthropic Computer Use](https://www.anthropic.com/news/3-5-models-and-computer-use) - Computer use agent that can control your browser.
- [Self-Operating Computer Framework](https://github.com/OthersideAI/self-operating-computer) - A framework to enable multimodal models to operate a computer. ![GitHub Repo stars](https://img.shields.io/github/stars/OthersideAI/self-operating-computer?style=social)
- [Highlight](https://highlightai.com/) - Highlight AI lets models understand your desktop activity. Get stuff done faster.
- [OpenInterpreter](https://github.com/openinterpreter/open-interpreter) - An open-source CLI based agent that can write & execute code as well as control your browser. ![GitHub Repo stars](https://img.shields.io/github/stars/openinterpreter/open-interpreter?style=social)
- [UI-TARS](https://github.com/bytedance/UI-TARS?tab=readme-ov-file) - A GUI agent model designed to interact seamlessly with GUIs using human-like perception, reasoning, and action capabilities. ![GitHub Repo stars](https://img.shields.io/github/stars/bytedance/UI-TARS?style=social)
- [OpenAI Computer-Using Agent (CUA)](https://openai.com/index/computer-using-agent/) - Combines GPT-4o vision with RL. 87% on WebVoyager, 38.1% on OSWorld. Now integrated into ChatGPT as agent mode.
- [Microsoft Computer Use for Copilot Studio](https://www.microsoft.com/en-us/copilot/copilot-studio) - Allows Copilot Studio agents to interact with any application through its GUI on Microsoft-hosted infrastructure.

## AI Web Automation Tools

Tools, frameworks and libraries that translate natural language instructions into web interactions.

- [Asteroid.ai](https://asteroid.ai/) - Hosted Browser Agents for SMEs to automate complex workflows. ![GitHub Repo stars](https://img.shields.io/github/stars/ishan0102/vimGPT?style=social)
- [PulsarRPA](https://github.com/platonai/pulsarRPA) - AI-powered browser automation for data extraction. ![GitHub Repo stars](https://img.shields.io/github/stars/platonai/pulsarRPA?style=social)
- [VimGPT](https://github.com/ishan0102/vimGPT) - Experimental project using GPT-4 Vision to browse the web via the Vimium extension. ![GitHub Repo stars](https://img.shields.io/github/stars/ishan0102/vimGPT?style=social)
- [Cekura.io](https://www.cekura.io/) - An AI browser agent that helps companies maintain up-to-date documentation.
- [Dex by Dexterity](https://getdexterity.com/) - An AI coworker embedding into and controlling your browser.
- [Autobrowser](https://autobrowser.ai/) - A free, experimental Chrome extension that leverages Claude Computer Use to automate tasks in your browser.
- [Bytebot](https://bytebot.ai) - Bytebot provides AI-powered scraping automations that evolve with your target sites.
- [Runcopycat](https://www.runcopycat.com/) - A no-code browser automation platform that turns screen recordings into reusable automated workflows.
- [Bardeen.ai](https://bardeen.ai) - A Chrome extension that enables AI-powered browser automations, allowing users to automate tasks and workflows directly within the browser.
- [Starizon.ai](https://starizon.ai/) - Browser assistant for web task automation.
- [BrowserGPT](https://browsegpt.ai/) - Browser extension for page summaries and Q&A.
- [Browse.ai](https://www.browse.ai/) - Chrome extension webscraping that can leverage AI for structured data extraction.
- [Strawberry Browser](https://www.strawberrybrowser.com/) - A personal assistant that sits in your browser, automates repetitive web actions, learns your workflows.
- [Deta.surf](https://deta.surf/) - An integrated platform that combines a browser, file manager, and AI assistant with browser-level context.
- [Reworkd](https://reworkd.ai) - No-code web data extraction solution using agentic AI.
- [Ottogrid](https://ottogrid.ai/) - Spreadsheet based web agents to automate manual research.

### Dev Tools

- [Steel.dev](https://steel.dev) - Open-source headless browser API built specifically for AI agents and apps. ![GitHub Repo stars](https://img.shields.io/github/stars/steel-dev/steel-browser?style=social)
- [Omniparser](https://microsoft.github.io/OmniParser/) - Tool for parsing GUIs for vision based agents. ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/OmniParser?style=social)
- [LaVague](https://www.lavague.ai/) - Framework for natural language web automation. ![GitHub Repo stars](https://img.shields.io/github/stars/lavague-ai/LaVague?style=social)
- [Langchain Playwright toolkit](https://python.langchain.com/docs/integrations/tools/playwright/#use-within-an-agent) - Toolkit integration with AI agents.
- [Browserbase](https://browserbase.com) - Serverless browser infrastructure for AI agents. $40M Series B (June 2025), 50M+ sessions, 1000+ customers.
- [Stagehand](https://www.stagehand.dev/) - AI web browsing framework. v3 removed Playwright dependency, added native CDP, 44% faster. Multi-language SDKs (Python, Go, Kotlin, C#, Ruby). ![GitHub Repo stars](https://img.shields.io/github/stars/browserbase/stagehand?style=social)
- [Tarsier](https://github.com/reworkd/tarsier) - Vision utilities library for web interaction agents. ![GitHub Repo stars](https://img.shields.io/github/stars/reworkd/tarsier?style=social)
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) - Experimental agent for task completion and web browsing. ![GitHub Repo stars](https://img.shields.io/github/stars/Significant-Gravitas/AutoGPT?style=social)
- [Bytebot](https://github.com/bytebot-ai/bytebot) - Containerized computer use agent framework with a virtual desktop environment. ![GitHub Repo stars](https://img.shields.io/github/stars/bytebot-ai/bytebot?style=social)
- [Playwright MCP Server](https://github.com/microsoft/playwright-mcp) - Microsoft's MCP server for browser automation via Playwright. Uses accessibility snapshots. Built into GitHub Copilot Coding Agent. ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/playwright-mcp?style=social)
- [Vercel Agent Browser](https://github.com/vercel-labs/agent-browser) - Headless browser automation CLI specifically for AI agents from Vercel Labs. ![GitHub Repo stars](https://img.shields.io/github/stars/vercel-labs/agent-browser?style=social)
- [Browser-Use Web UI](https://github.com/browser-use/web-ui) - Run AI agents in your browser with DeepSeek-r1 support for deep thinking. ![GitHub Repo stars](https://img.shields.io/github/stars/browser-use/web-ui?style=social)

## AI Web Scrapers/Crawlers

Web crawlers & scrapers that leverage AI to navigate websites and extract content.

- [FireCrawl](https://www.firecrawl.dev/) - APIs for turning websites into LLM-friendly markdown. ![GitHub Repo stars](https://img.shields.io/github/stars/mendableai/firecrawl?style=social)
- [Crawl4AI](https://crawl4ai.com) - Open-source LLM Friendly Web Crawler & Scraper. ![GitHub Repo stars](https://img.shields.io/github/stars/unclecode/crawl4ai?style=social)
- [ScrapeGraphAI](https://scrapegraphai.com/) - Python scraper based on AI. ![GitHub Repo stars](https://img.shields.io/github/stars/ScrapeGraphAI/Scrapegraph-ai?style=social)
- [WebAgent (OpenAgents)](https://github.com/xlang-ai/OpenAgents) - The web-browsing agent module of the OpenAgents platform (HKU). Enables autonomous navigation of websites via natural language, as part of a larger multi-modal agent framework. ![GitHub Repo stars](https://img.shields.io/github/stars/xlang-ai/OpenAgents?style=social)
- [Expand.ai](https://www.expand.ai/) - Turns any website into a type-safe API you can rely on.
- [LLM Scraper](https://github.com/mishushakov/llm-scraper) - Uses LLMs for intelligent scraping and content understanding. ![GitHub Repo stars](https://img.shields.io/github/stars/mishushakov/llm-scraper?style=social)
- [SpiderCreator](https://github.com/carlosplanchon/spidercreator) - Create complex Playwright spiders with natural language prompts. ![GitHub Repo stars](https://img.shields.io/github/stars/carlosplanchon/spidercreator?style=social)
- [Scrapling](https://github.com/D4Vinci/Scrapling) - Adaptive web scraping framework with interactive shell. 92% test coverage, BeautifulSoup-like API. ![GitHub Repo stars](https://img.shields.io/github/stars/D4Vinci/Scrapling?style=social)
- [Crawl4AI MCP Server](https://github.com/sadiuysal/crawl4ai-mcp-server) - MCP server exposing Crawl4AI as tools for AI agents. Self-hosted Firecrawl alternative. Compatible with OpenAI Agents SDK, Cursor, Claude Code. ![GitHub Repo stars](https://img.shields.io/github/stars/sadiuysal/crawl4ai-mcp-server?style=social)

## Web Search & Query Tools

Utilities that help agents search the web or query web data via natural language.

- [AgentQL](https://www.agentql.com/) - A query language and toolkit that makes the web AI-ready. ![GitHub Repo stars](https://img.shields.io/github/stars/tinyfish-io/agentql?style=social)
- [SerpAPI](https://serpapi.com/) - Search API that provides Google Search results for your agents.
- [Serper.dev](https://serper.dev/) - Performant and cost effective search API that provides Google Search results for your agents.
- [Jina.ai](https://jina.ai/) - Neural search platform for web data.
- [Exa.ai](https://exa.ai) - Semantic Search Engine for AI.

## Benchmarks & Research

Datasets, benchmarks, and notable research efforts for evaluating and advancing web-capable AI agents.

- [Web Agent Leaderboard](https://leaderboard.steel.dev) - Web agent leaderboard compiling different AI agent products and how they perform on the widely used WebVoyager benchmarks. ![GitHub Repo stars](https://img.shields.io/github/stars/steel-dev/leaderboard?style=social)
- [Web Games by Convergence](https://webgames.convergence.ai/) - a collection of challenges designed for testing general-purpose web-browsing AI agents. ![GitHub Repo stars](https://img.shields.io/github/stars/convergence-ai/webgames?style=social)
- [Bananalyzer](https://github.com/reworkd/bananalyzer) - An open-source evaluation framework for web-based AI agents. ![GitHub Repo stars](https://img.shields.io/github/stars/reworkd/bananalyzer?style=social)
- [Mind2Web](https://osu-nlp-group.github.io/Mind2Web) - A large-scale dataset for generalist web agents. ![GitHub Repo stars](https://img.shields.io/github/stars/OSU-NLP-Group/Mind2Web?style=social)
- [World of Bits: An Open-Domain Platform for Web-Based Agents](https://proceedings.mlr.press/v70/shi17a/shi17a.pdf) - OpenAI's research paper that introduces World or Bits: a platform where agents complete tasks on the internet by performing low-level keyboard and mouse actions.
- [MiniWoB++](https://miniwob.farama.org) - A classic suite of 104 mini web browser tasks in a synthetic environment. It's is an extension of the OpenAI MiniWoB benchmark. ![GitHub Repo stars](https://img.shields.io/github/stars/Farama-Foundation/miniwob-plusplus?style=social)
- [WebArena](https://webarena.dev) - A realistic, self-hostable web environment for autonomous agents. Includes official leaderboard tracking agent performance. ![GitHub Repo stars](https://img.shields.io/github/stars/web-arena-x/webarena?style=social)
- [WebCanvas](https://github.com/iMeanAI/WebCanvas) - An online evaluation framework for dynamic web environments. Tests agents on live websites. ![GitHub Repo stars](https://img.shields.io/github/stars/iMeanAI/WebCanvas?style=social)
- [WebGPT](https://openai.com/research/webgpt) - OpenAI's browser-assisted question-answering research project.
- [WebShop](https://webshop-pnlp.github.io) - A simulated e-commerce shopping environment with 1.18M real Amazon products. ![GitHub Repo stars](https://img.shields.io/github/stars/princeton-nlp/WebShop?style=social)
- [WebVoyager (Benchmark)](https://github.com/MinorJerry/WebVoyager) - Vision-enabled web agent using GPT-4V for real-world website interaction. ![GitHub Repo stars](https://img.shields.io/github/stars/MinorJerry/WebVoyager?style=social)
- [WorkArena](https://github.com/ServiceNow/WorkArena) - A suite of 33 browser-based tasks for enterprise "knowledge worker" scenarios. ![GitHub Repo stars](https://img.shields.io/github/stars/ServiceNow/WorkArena?style=social)
- [BrowserGym by ServiceNow](https://github.com/ServiceNow/BrowserGym) - A gym environment for web task automation. ![GitHub Repo stars](https://img.shields.io/github/stars/ServiceNow/BrowserGym?style=social)
- [WebArena Verified](https://openreview.net/forum?id=CSIo4D7xBG) - Reproducible re-evaluation of WebArena with strengthened measurement. Reduces false-negative rate by 11.3%. ICLR 2026.
- [MM-BrowseComp](https://openreview.net/forum?id=zIT4MLbjlO) - 224 hand-crafted questions testing multimodal retrieval and reasoning with images/videos on webpages. ICLR 2026.
- [WebChoreArena](https://openreview.net/forum?id=d0xqdsR41U) - 532 curated tasks testing labor-intensive web tasks across Massive Memory, Calculation, and Long-Term Memory challenges. ICLR 2026.
- [ST-WebAgentBench](https://openreview.net/forum?id=IIzehISTBe) - Benchmark for safety and trustworthiness of web agents across 6 dimensions. ICLR 2025.
- [Deep Research Bench](https://futuresearch.ai/deep-research-bench/) - Benchmarks how well LLM agents perform web research with both retro and live evaluations.

## Tutorials & Guides

Resources for learning how to build, deploy, or utilize AI web agents.

- [LangGraph WebVoyager Tutorial](https://langchain-ai.github.io/langgraph/tutorials/web-navigation/web_voyager/) - Tutorial demonstrating how to build a web navigation agent using LangGraph Agents, Vision Models, and Web Voyager.
- [Build an AI Browser Agent](https://dzone.com/articles/build-ai-browser-agent-llms-playwright-browser-use) - Step-by-step guide to create an AI that browses the web using Playwright and the Browser-Use library.
- [Install & Run Browser-Use Locally](https://aleksandarhaber.com/install-and-run-browser-use-ai-agents-locally-using-ollama/) - Instructions on installing the open-source Browser-Use agent with a local LLM.
- [Build a Browser Agent with DeepSeek](https://nodeshift.com/blog/build-a-browser-use-agent-with-deepseek-a-step-by-step-guide) - Walks through deploying a Browser-Use web UI agent powered by the DeepSeek model on a cloud VM.
- [DeepLearning.AI - Building AI Browser Agents](https://www.deeplearning.ai/short-courses/building-ai-browser-agents/) - Short course on building agents that navigate and interact with websites reliably.
- [Playwright MCP Comprehensive Guide](https://medium.com/@bluudit/playwright-mcp-comprehensive-guide-to-ai-powered-browser-automation-in-2025-712c9fd6cffa) - Guide to AI-powered browser automation with Playwright MCP.
- [AI Web Agents Complete Guide (Skyvern)](https://www.skyvern.com/blog/ai-web-agents-complete-guide-to-intelligent-browser-automation-november-2025/) - Comprehensive guide to intelligent browser automation.
- [Agentic Browser Landscape 2026](https://www.nohackspod.com/blog/agentic-browser-landscape-2026) - Complete landscape guide covering major players, architectures, and trends.

## 금융공기업 NCS 기출문제 모음

금융공기업 NCS 기출문제 및 학습 자료를 과목별, 기관별, 년도별로 분류한 큐레이션 목록입니다.

**[금융공기업 NCS 기출문제 모음 바로가기 →](../ncs/financial-exams.md)**

<!-- END CONTENT -->

## Interested in implementing Steel?
Feel free to reach out at [team@steel.dev](mailto:team@steel.dev?subject=Hello%20from%20github!) or on [Discord](https://discord.gg/steel-dev).

Steel is an [open-source](https://github.com/steel-dev/steel-browser) browser API built specifically for AI agents. Get started for free [here](https://app.steel.dev).


## Join the Community

<!-- list people worth following on social sites (Twitter, LinkedIn, GitHub, YouTube etc.) -->

- Follow [@steeldotdev](https://x.com/steeldotdev) on X.
- Join the [Discord community](https://discord.gg/steel-dev).
- Feel free to reach out to us at [team@steel.dev](mailto:team@steel.dev?subject=Hello%20from%20github!)

## Contributing

[Contributions of any kind welcome, just follow the guidelines](contributing.md)!

### Contributors

[Thanks goes to these contributors](https://github.com/steel-dev/awesome-web-agents/graphs/contributors)!
