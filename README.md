# Atlas

Type any educational topic — history, biology, physics, geography, processes —
and get an interactive, hand-drawn diagram you can explore. Click any element
to drill into a deeper, AI-generated sub-diagram for that piece. URLs are
shareable; child nodes are cached so re-clicks are instant.

Inspired by Gauth's "Atlas" feature; built on Next.js 16, Excalidraw, and
Claude (Anthropic API).

## Stack

- **Next.js 16** (App Router) + TypeScript + Tailwind v4
- **Excalidraw** — hand-drawn aesthetic canvas
- **Claude (`@anthropic-ai/sdk`)** — generates structured diagram JSON via
  `messages.parse()` + `output_config.format` (Zod schema), with adaptive
  thinking and prompt-caching on the system prompt
- **better-sqlite3** — local file-based persistence, idempotent child-node
  caching keyed by `(atlas_id, parent_id, parent_element_id)`

## Setup

```bash
# 1. Install
npm install

# 2. Configure
cp .env.local.example .env.local
# then edit .env.local and set ANTHROPIC_API_KEY

# 3. Initialize the database
npm run db:init

# 4. Dev server
npm run dev   # → http://localhost:3000
```

## How it works

1. User submits a topic on `/`.
2. `POST /api/atlas` → Claude generates a `ClaudeNodeOutput` (title, format,
   summary, 6–12 elements with semantic ids, normalized 0..1000 coordinates,
   `expandable` flag per element). The atlas + root node are persisted.
3. User is redirected to `/atlas/[id]`. The server component fetches the atlas
   and hands it to `AtlasViewer` (client). The viewer converts
   `claudeElements` → Excalidraw scene via `lib/excalidraw-client.ts` and
   stamps each shape's `customData` with `semanticId`/`expandable`.
4. On `pointerDown`, the viewer reads `customData.expandable` from the hit
   element. If true, it `POST`s `/api/atlas/[id]/expand` with
   `{ parentNodeId, parentElementId }`.
5. The expand route looks up a cached child via the UNIQUE key; on miss, it
   calls Claude with the parent's context + the clicked element's
   `childPrompt`, persists the result, and returns it.
6. The viewer pushes the new node onto a stack (rendered as a breadcrumb)
   and updates the Excalidraw scene.

## Project layout

```
app/
  page.tsx                            # /
  atlas/[id]/page.tsx                 # /atlas/[id] — server, fetches atlas
  atlas/[id]/AtlasViewer.tsx          # client — Excalidraw + click handler
  atlas/[id]/not-found.tsx            # 404
  atlas/[id]/error.tsx                # runtime error boundary
  api/atlas/route.ts                  # POST create root atlas
  api/atlas/[id]/route.ts             # GET fetch atlas
  api/atlas/[id]/expand/route.ts      # POST expand a child node
components/
  TopicForm.tsx, BreadcrumbTrail.tsx, ShareBar.tsx, LoadingOverlay.tsx
lib/
  anthropic.ts                        # client + model constants
  prompts.ts                          # system prompt + Zod schema
  claude.ts                           # generateRootAtlas / generateChildNode
  excalidraw.ts                       # pure semantic→skeleton mapper (server-safe)
  excalidraw-client.ts                # convertToExcalidrawElements wrapper (client-only)
  db.ts                               # better-sqlite3 singleton + schema
  atlas-repo.ts                       # createAtlas / getAtlas / findChildNode / addChildNode
  id.ts                               # nanoid wrappers
types/atlas.ts
scripts/
  init-db.ts                          # npm run db:init
  smoke-claude.ts                     # end-to-end Claude smoke test
  smoke-repo.ts                       # round-trip atlas through the repo
  smoke-excalidraw.ts                 # skeleton-mapper unit check
```

## Notes

- **Server/client split for Excalidraw.** The Excalidraw runtime touches
  `window`/`navigator` at module load, so it cannot be imported on the
  server. `lib/excalidraw.ts` is the pure skeleton builder (server-safe);
  `lib/excalidraw-client.ts` is the only place that calls
  `convertToExcalidrawElements` and is loaded only on the client.
- **No `excalidrawElements` in the DB.** We store only `claudeElements`
  (semantic) and re-convert on every render. Saves ~half the JSON and
  avoids needing a DOM in any server-side codepath.
- **better-sqlite3 + serverless.** The local SQLite file works for self-hosted
  deploys but not Vercel's read-only FS. Swap `lib/db.ts` for Vercel KV or
  Postgres + Prisma to deploy serverlessly.
