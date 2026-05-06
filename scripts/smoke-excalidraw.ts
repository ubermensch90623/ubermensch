import { claudeToSkeletons } from "@/lib/excalidraw";
import type { ClaudeNodeOutput, ElementCustomData } from "@/types/atlas";

const fakeRoot: ClaudeNodeOutput = {
  title: "How a CPU executes an instruction",
  format: "process",
  summary: "The classic five-stage RISC pipeline.",
  elements: [
    { id: "fetch",   kind: "box", label: "Fetch",     x: 150, y: 500, expandable: true,  childPrompt: "How fetch works" },
    { id: "decode",  kind: "box", label: "Decode",    x: 350, y: 500, expandable: true,  childPrompt: "Instruction decoding" },
    { id: "execute", kind: "box", label: "Execute",   x: 550, y: 500, expandable: true,  childPrompt: "ALU operations" },
    { id: "memory",  kind: "box", label: "Memory",    x: 750, y: 500, expandable: true,  childPrompt: "Memory access" },
    { id: "write",   kind: "box", label: "Writeback", x: 900, y: 500, expandable: false },
    { id: "a1", kind: "arrow", label: "", x: 0, y: 0, from: "fetch",   to: "decode",  expandable: false },
    { id: "a2", kind: "arrow", label: "", x: 0, y: 0, from: "decode",  to: "execute", expandable: false },
    { id: "a3", kind: "arrow", label: "", x: 0, y: 0, from: "execute", to: "memory",  expandable: false },
    { id: "a4", kind: "arrow", label: "", x: 0, y: 0, from: "memory",  to: "write",   expandable: false },
    { id: "a-bad", kind: "arrow", label: "", x: 0, y: 0, from: "write", to: "nonexistent", expandable: false },
  ],
};

const skeletons = claudeToSkeletons(fakeRoot);
console.log(`✓ ${fakeRoot.elements.length} ClaudeElements → ${skeletons.length} skeletons`);

const byType = new Map<string, number>();
for (const s of skeletons) byType.set(s.type, (byType.get(s.type) ?? 0) + 1);
console.log("  By type:");
for (const [t, n] of byType) console.log(`    ${t}: ${n}`);

const arrowCount = skeletons.filter((s) => s.type === "arrow").length;
if (arrowCount !== 4) {
  throw new Error(`Expected 4 valid arrows (1 dropped due to bad ref), got ${arrowCount}`);
}
console.log(`  ✓ Bad-reference arrow correctly filtered (a-bad → nonexistent dropped)`);

const semIds = new Set<string>();
for (const s of skeletons) {
  const cd = (s as { customData?: ElementCustomData }).customData;
  if (cd?.semanticId) semIds.add(cd.semanticId);
}
const expected = ["fetch", "decode", "execute", "memory", "write", "a1", "a2", "a3", "a4"];
const missing = expected.filter((id) => !semIds.has(id));
if (missing.length > 0) {
  throw new Error(`Missing semanticIds: ${missing.join(", ")}`);
}
console.log(`  ✓ All ${expected.length} semantic ids stamped`);

const decode = skeletons.find(
  (s) => (s as { id?: string }).id === "decode",
) as { customData?: ElementCustomData; label?: { text: string } } | undefined;
if (!decode?.customData?.expandable) {
  throw new Error("decode element should be expandable");
}
if (!decode.customData.childPrompt) {
  throw new Error("decode element should carry childPrompt");
}
if (decode.label?.text !== "Decode") {
  throw new Error(`decode label should be "Decode", got "${decode.label?.text}"`);
}
console.log("  ✓ Expandable + childPrompt + label preserved on decode");

const a1 = skeletons.find(
  (s) => s.type === "arrow" && (s as { customData?: ElementCustomData }).customData?.semanticId === "a1",
) as { start?: { id: string }; end?: { id: string } } | undefined;
if (a1?.start?.id !== "fetch" || a1?.end?.id !== "decode") {
  throw new Error("a1 arrow should bind fetch → decode");
}
console.log("  ✓ Arrow start/end bindings reference correct ids");

console.log("\n✓ Skeleton mapper smoke test passed");
