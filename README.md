# LLM Evolution Wiki (mirror)

This repository mirrors the `evolution` lab from [`joonan30/llm-wiki-labs`](https://github.com/joonan30/llm-wiki-labs), a Korean-language case study titled **"Compounding Wiki — 31일의 누적"** documenting 31 days of building an AI-native research wiki.

- Upstream repository: https://github.com/joonan30/llm-wiki-labs
- Upstream live site: https://joonan30.github.io/llm-wiki-labs/evolution/
- Original author: Joon-Yong An (Korea University)
- License: MIT (see [`LICENSE`](./LICENSE)) — copyright © 2026 Joon-Yong An

The HTML files here (`index.html`, `evolution/index.html`) are byte-exact copies of the upstream as of the last sync. No content, design, or copy has been modified.

## Run locally

```bash
python3 -m http.server 8000
```

Then open:
- http://localhost:8000/ — landing page
- http://localhost:8000/evolution/ — the 31-day case study

No build step. The only external dependency is Google Fonts (Newsreader, IBM Plex Sans, JetBrains Mono).
