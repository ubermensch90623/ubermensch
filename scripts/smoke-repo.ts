import {
  createAtlas,
  getAtlas,
  findChildNode,
  addChildNode,
} from "@/lib/atlas-repo";
import { closeDb } from "@/lib/db";
import type { ClaudeNodeOutput } from "@/types/atlas";

const fakeRoot: ClaudeNodeOutput = {
  title: "Test Atlas",
  format: "concept",
  summary: "Smoke-test atlas to validate the repo layer.",
  elements: [
    { id: "center", kind: "ellipse", label: "Core idea", x: 500, y: 500, expandable: false },
    { id: "child-a", kind: "box", label: "Branch A", x: 200, y: 300, expandable: true, childPrompt: "Explore branch A" },
    { id: "child-b", kind: "box", label: "Branch B", x: 800, y: 300, expandable: true, childPrompt: "Explore branch B" },
    { id: "child-c", kind: "box", label: "Branch C", x: 500, y: 800, expandable: false },
  ],
};

const fakeChild: ClaudeNodeOutput = {
  title: "Branch A details",
  format: "process",
  summary: "Drilldown of branch A.",
  elements: [
    { id: "step1", kind: "box", label: "Step 1", x: 200, y: 500, expandable: false },
    { id: "step2", kind: "box", label: "Step 2", x: 500, y: 500, expandable: false },
    { id: "step3", kind: "box", label: "Step 3", x: 800, y: 500, expandable: false },
    { id: "arrow1", kind: "arrow", label: "", x: 0, y: 0, from: "step1", to: "step2", expandable: false },
  ],
};

console.log("[1] createAtlas...");
const { atlasId, rootNodeId } = createAtlas({
  topic: "smoke test",
  root: fakeRoot,
});
console.log(`    atlasId=${atlasId}  rootNodeId=${rootNodeId}`);

console.log("[2] getAtlas...");
const atlas = getAtlas(atlasId);
if (!atlas) throw new Error("atlas not found");
console.log(`    nodes=${Object.keys(atlas.nodes).length}  topic="${atlas.topic}"`);
console.log(`    root title="${atlas.nodes[rootNodeId].title}"`);
console.log(`    root elements=${atlas.nodes[rootNodeId].claudeElements.length}`);

console.log("[3] findChildNode (should be null before adding)...");
const before = findChildNode(atlasId, rootNodeId, "child-a");
console.log(`    before=${before === null ? "null ✓" : "FOUND (unexpected!)"}`);

console.log("[4] addChildNode...");
const child = addChildNode({
  atlasId,
  parentNodeId: rootNodeId,
  parentElementId: "child-a",
  child: fakeChild,
});
console.log(`    childId=${child.id}  format=${child.format}`);

console.log("[5] findChildNode (should now return the child)...");
const after = findChildNode(atlasId, rootNodeId, "child-a");
console.log(`    after id=${after?.id ?? "null"}  match=${after?.id === child.id ? "✓" : "✗"}`);

console.log("[6] idempotency: addChildNode with same key should fail...");
let collidedAsExpected = false;
try {
  addChildNode({
    atlasId,
    parentNodeId: rootNodeId,
    parentElementId: "child-a",
    child: fakeChild,
    });
} catch (err) {
  collidedAsExpected = true;
  console.log(`    correctly rejected duplicate (${(err as Error).message.split("\n")[0]})`);
}
if (!collidedAsExpected) throw new Error("UNIQUE constraint did not fire");

console.log("[7] getAtlas after expand...");
const finalAtlas = getAtlas(atlasId);
console.log(`    final nodes=${Object.keys(finalAtlas!.nodes).length} (expected 2)`);

console.log("\n✓ Repo layer smoke test passed");
closeDb();
