import { createAtlas, getAtlas, addChildNode } from "@/lib/atlas-repo";
import { closeDb } from "@/lib/db";
import type { ClaudeNodeOutput } from "@/types/atlas";

const RUNS = 100;
const ids = new Set<string>();
let collisions = 0;
let errors = 0;

const baseRoot: ClaudeNodeOutput = {
  title: "Volume test",
  format: "concept",
  summary: "",
  elements: [
    { id: "a", kind: "ellipse", label: "A", x: 500, y: 500, expandable: true, childPrompt: "child" },
    { id: "b", kind: "box", label: "B", x: 200, y: 200, expandable: false },
  ],
};

const baseChild: ClaudeNodeOutput = {
  title: "Child",
  format: "concept",
  summary: "",
  elements: [{ id: "c1", kind: "box", label: "C1", x: 500, y: 500, expandable: false }],
};

async function main() {
  console.log(`Creating ${RUNS} atlases (each with 1 child) on the same DB...`);
  const startedAt = Date.now();

  for (let i = 0; i < RUNS; i++) {
    try {
      const { atlasId, rootNodeId } = await createAtlas({
        topic: `vol-${i}`,
        root: baseRoot,
      });
      if (ids.has(atlasId)) collisions++;
      ids.add(atlasId);

      const child = await addChildNode({
        atlasId,
        parentNodeId: rootNodeId,
        parentElementId: "a",
        child: baseChild,
      });
      if (ids.has(child.id)) collisions++;
      ids.add(child.id);

      const fetched = await getAtlas(atlasId);
      if (!fetched || Object.keys(fetched.nodes).length !== 2) {
        errors++;
      }
    } catch (err) {
      errors++;
      console.error(`  iter ${i} error: ${(err as Error).message}`);
    }
  }

  const elapsed = Date.now() - startedAt;
  console.log(`\nResults:`);
  console.log(`  ${RUNS} iterations in ${elapsed}ms (avg ${(elapsed / RUNS).toFixed(1)}ms each)`);
  console.log(`  unique ids generated: ${ids.size}`);
  console.log(`  id collisions: ${collisions}`);
  console.log(`  iter errors: ${errors}`);
  closeDb();
  process.exit(collisions === 0 && errors === 0 ? 0 : 1);
}

main().catch((err) => {
  console.error(err);
  closeDb();
  process.exit(2);
});
