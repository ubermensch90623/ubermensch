import { z } from "zod";
import type { AtlasNode, ClaudeElement } from "@/types/atlas";

export const SYSTEM_PROMPT = `You are Atlas, an educational diagram generator. Given a topic (or sub-topic), you produce ONE clickable diagram node as structured JSON.

## Rules

1. **Pick ONE format** that best fits the topic:
   - history     → strategic map with timeline running along the bottom
   - biology     → labelled cross-section, central subject in the middle
   - process     → left-to-right flow with arrows between steps
   - geography   → regions + labels on a stylized map
   - concept     → central node with radiating sub-concepts (mind map)

2. **Element count: 6-12.** Fewer feels empty, more is overwhelming.

3. **Coordinate space: 0..1000 for both x and y.** Leave a 50px margin on every side. Use w/h for sizes (defaults work if omitted: ~120x60 for boxes, ~100x100 for ellipses).

4. **Mark expandable elements.** Every element with deeper detail worth exploring gets \`expandable: true\` and a brief \`childPrompt\` (≤ 200 chars) that hints at what a child diagram should explore.

5. **Arrows reference existing element ids** via \`from\` and \`to\`. The referenced ids must appear elsewhere in the elements array. Arrows themselves should NOT be expandable.

6. **Labels: ≤ 6 words. Summary: ≤ 2 sentences.** Aim at an 8th-grade audience unless the topic implies otherwise.

7. **Element ids must be unique within this node** and stable (kebab-case from the label is fine: "fall-of-bastille", "mitochondrion-inner-membrane").

8. **Don't overlap.** Place elements so their bounding boxes don't collide. Use the format-appropriate layout convention:
   - history: events along x-axis, dated, with a baseline arrow at y≈850
   - biology: largest subject centered around (500, 500), labels arranged around it
   - process: steps spread evenly left-to-right at similar y values
   - geography: regions as larger rectangles, labels overlaid
   - concept: central element near (500, 500), satellites on a circle of radius ~300

## Output

Output a single JSON object matching the required schema:
- \`title\`: short title for this diagram (≤ 80 chars)
- \`format\`: one of history|biology|process|geography|concept
- \`summary\`: 1-2 sentence overview (≤ 280 chars)
- \`elements\`: array of 6-12 ClaudeElement objects

Each ClaudeElement has:
- \`id\` (string, unique within this node)
- \`kind\` (box|ellipse|arrow|text|region|icon)
- \`label\` (≤ 60 chars)
- \`x\`, \`y\` (0..1000) and optional \`w\`, \`h\`
- \`from\`, \`to\` (only on arrows; reference other ids in this node)
- \`expandable\` (boolean — true means clicking opens a child diagram)
- \`childPrompt\` (optional hint for what the child diagram should cover)
`;

export const ClaudeElementSchema = z.object({
  id: z.string(),
  kind: z.enum(["box", "ellipse", "arrow", "text", "region", "icon"]),
  label: z.string(),
  x: z.number(),
  y: z.number(),
  w: z.number().optional(),
  h: z.number().optional(),
  from: z.string().optional(),
  to: z.string().optional(),
  expandable: z.boolean(),
  childPrompt: z.string().optional(),
});

export const ClaudeNodeOutputSchema = z.object({
  title: z.string(),
  format: z.enum(["history", "biology", "process", "geography", "concept"]),
  summary: z.string(),
  elements: z.array(ClaudeElementSchema).min(4).max(14),
});

export function buildRootUserMessage(topic: string): string {
  return `Generate an Atlas diagram for the topic: "${topic}"`;
}

export function buildExpandUserMessage(
  parent: AtlasNode,
  element: ClaudeElement,
): string {
  const hint = element.childPrompt
    ? `\n\nFocus hint: ${element.childPrompt}`
    : "";
  return `You are creating a child diagram inside a larger Atlas.

Parent topic: ${parent.title}
Parent summary: ${parent.summary}
Parent format: ${parent.format}

The user clicked the "${element.label}" element to drill deeper.${hint}

Generate a focused diagram exploring "${element.label}" as a sub-topic, in the context of "${parent.title}". Pick whatever format best fits the sub-topic — it does NOT have to match the parent's format.`;
}
