import { applyLayoutTemplate } from "@/lib/format";
import type { ClaudeNodeOutput } from "@/types/atlas";

function approx(a: number, b: number, tol = 1): boolean {
  return Math.abs(a - b) <= tol;
}

console.log("[1] Process layout — topo sort + even spacing");
const processInput: ClaudeNodeOutput = {
  title: "P", format: "process", summary: "",
  elements: [
    // Intentionally out-of-order coords + scrambled Claude order
    { id: "execute", kind: "box", label: "Execute", x: 999, y: 999, expandable: false },
    { id: "fetch",   kind: "box", label: "Fetch",   x: 0,   y: 0,   expandable: false },
    { id: "decode",  kind: "box", label: "Decode",  x: 500, y: 250, expandable: false },
    { id: "memory",  kind: "box", label: "Memory",  x: 100, y: 800, expandable: false },
    { id: "write",   kind: "box", label: "Write",   x: 800, y: 100, expandable: false },
    { id: "a1", kind: "arrow", label: "", x: 0, y: 0, from: "fetch",   to: "decode",  expandable: false },
    { id: "a2", kind: "arrow", label: "", x: 0, y: 0, from: "decode",  to: "execute", expandable: false },
    { id: "a3", kind: "arrow", label: "", x: 0, y: 0, from: "execute", to: "memory",  expandable: false },
    { id: "a4", kind: "arrow", label: "", x: 0, y: 0, from: "memory",  to: "write",   expandable: false },
  ],
};
const processOut = applyLayoutTemplate(processInput);
const order = ["fetch", "decode", "execute", "memory", "write"];
let lastX = -Infinity;
for (const id of order) {
  const el = processOut.elements.find((e) => e.id === id);
  if (!el) throw new Error(`missing ${id}`);
  if (el.y !== 500) throw new Error(`${id} y should be 500, got ${el.y}`);
  if (el.x <= lastX) throw new Error(`${id} x=${el.x} should be > prev ${lastX}`);
  lastX = el.x;
  console.log(`    ${id} → x=${el.x.toFixed(0)} y=${el.y}`);
}
const fetchX = processOut.elements.find((e) => e.id === "fetch")!.x;
const writeX = processOut.elements.find((e) => e.id === "write")!.x;
if (!approx(fetchX, 100) || !approx(writeX, 900)) {
  throw new Error(`fetch should be at x≈100 (got ${fetchX}), write at x≈900 (got ${writeX})`);
}
console.log("    ✓ Topo order respected, evenly spaced fetch=100…write=900 at y=500");

console.log("\n[2] Process layout — cycle detection (should no-op)");
const cycleInput: ClaudeNodeOutput = {
  title: "C", format: "process", summary: "",
  elements: [
    { id: "a", kind: "box", label: "A", x: 100, y: 100, expandable: false },
    { id: "b", kind: "box", label: "B", x: 200, y: 200, expandable: false },
    { id: "ab", kind: "arrow", label: "", x: 0, y: 0, from: "a", to: "b", expandable: false },
    { id: "ba", kind: "arrow", label: "", x: 0, y: 0, from: "b", to: "a", expandable: false },
  ],
};
const cycleOut = applyLayoutTemplate(cycleInput);
const aOrig = cycleInput.elements.find((e) => e.id === "a")!;
const aOut = cycleOut.elements.find((e) => e.id === "a")!;
if (aOut.x !== aOrig.x || aOut.y !== aOrig.y) {
  throw new Error("Cycle should leave coords unchanged");
}
console.log("    ✓ Cycle detected → coords unchanged");

console.log("\n[3] Concept layout — central + radial");
const conceptInput: ClaudeNodeOutput = {
  title: "K", format: "concept", summary: "",
  elements: [
    { id: "leaf-a", kind: "ellipse", label: "A", x: 0, y: 0, expandable: false },
    { id: "leaf-b", kind: "ellipse", label: "B", x: 0, y: 0, expandable: false },
    { id: "leaf-c", kind: "ellipse", label: "C", x: 0, y: 0, expandable: false },
    { id: "leaf-d", kind: "ellipse", label: "D", x: 0, y: 0, expandable: false },
    // Central: largest by area
    { id: "core",   kind: "region",  label: "Core", x: 0, y: 0, w: 300, h: 200, expandable: false },
  ],
};
const conceptOut = applyLayoutTemplate(conceptInput);
const core = conceptOut.elements.find((e) => e.id === "core")!;
if (core.x !== 500 || core.y !== 500) {
  throw new Error(`Core should be at center (500,500), got (${core.x},${core.y})`);
}
console.log(`    ✓ Largest element "core" placed at center (${core.x}, ${core.y})`);

const leaves = ["leaf-a", "leaf-b", "leaf-c", "leaf-d"]
  .map((id) => conceptOut.elements.find((e) => e.id === id)!);
for (const l of leaves) {
  const dx = l.x - 500;
  const dy = l.y - 500;
  const r = Math.sqrt(dx * dx + dy * dy);
  if (!approx(r, 320, 2)) {
    throw new Error(`${l.id} should be at radius 320 from center, got ${r.toFixed(1)}`);
  }
  console.log(`    ${l.id} → (${l.x},${l.y}) r=${r.toFixed(1)}`);
}
console.log("    ✓ All satellites on circle r=320");

console.log("\n[4] Default layouts (history, biology, geography) → no-op");
for (const fmt of ["history", "biology", "geography"] as const) {
  const inp: ClaudeNodeOutput = {
    title: "X", format: fmt, summary: "",
    elements: [
      { id: "a", kind: "box", label: "A", x: 123, y: 456, expandable: false },
      { id: "b", kind: "box", label: "B", x: 789, y: 234, expandable: false },
    ],
  };
  const out = applyLayoutTemplate(inp);
  const a = out.elements.find((e) => e.id === "a")!;
  if (a.x !== 123 || a.y !== 456) {
    throw new Error(`${fmt} should be no-op, but a moved`);
  }
  console.log(`    ✓ ${fmt}: coords preserved`);
}

console.log("\n✓ Format layout smoke test passed");
