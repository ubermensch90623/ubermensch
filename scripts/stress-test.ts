import { applyLayoutTemplate } from "@/lib/format";
import { claudeToSkeletons } from "@/lib/excalidraw";
import {
  createAtlas,
  getAtlas,
  findChildNode,
  addChildNode,
  getNode,
} from "@/lib/atlas-repo";
import { closeDb } from "@/lib/db";
import type {
  ClaudeNodeOutput,
  ClaudeElement,
  ElementCustomData,
} from "@/types/atlas";

interface Failure {
  scenario: string;
  invariant: string;
  detail: string;
}

const failures: Failure[] = [];
function fail(scenario: string, invariant: string, detail: string) {
  failures.push({ scenario, invariant, detail });
  console.log(`    ✗ ${invariant}: ${detail}`);
}
function pass(invariant: string) {
  console.log(`    ✓ ${invariant}`);
}

function assertSkeletonInvariants(scenario: string, node: ClaudeNodeOutput) {
  const skeletons = claudeToSkeletons(node);

  // Invariant 1: every non-arrow input element should produce at least one skeleton
  const inputShapes = node.elements.filter((e) => e.kind !== "arrow");
  const inputShapeIds = new Set(inputShapes.map((e) => e.id));
  const outputSemanticIds = new Set<string>();
  for (const s of skeletons) {
    const cd = (s as { customData?: ElementCustomData }).customData;
    if (cd?.semanticId) outputSemanticIds.add(cd.semanticId);
  }
  const missing = [...inputShapeIds].filter((id) => !outputSemanticIds.has(id));
  if (missing.length > 0) {
    fail(scenario, "all shape ids preserved", `missing: ${missing.join(", ")}`);
  } else {
    pass("all shape ids preserved");
  }

  // Invariant 2: no NaN / Infinity in coords
  let badCoord = false;
  for (const s of skeletons) {
    const x = (s as { x?: number }).x;
    const y = (s as { y?: number }).y;
    if (x !== undefined && (!Number.isFinite(x) || Number.isNaN(x))) badCoord = true;
    if (y !== undefined && (!Number.isFinite(y) || Number.isNaN(y))) badCoord = true;
  }
  if (badCoord) {
    fail(scenario, "no NaN/Infinity in coords", "found");
  } else {
    pass("no NaN/Infinity in coords");
  }

  // Invariant 3: arrows have valid bindings (or are filtered out)
  const skeletonShapeIds = new Set<string>();
  for (const s of skeletons) {
    if (s.type !== "arrow") {
      const id = (s as { id?: string }).id;
      if (id) skeletonShapeIds.add(id);
    }
  }
  let badArrow = false;
  for (const s of skeletons) {
    if (s.type !== "arrow") continue;
    const arrow = s as { start?: { id?: string }; end?: { id?: string } };
    if (!arrow.start?.id || !arrow.end?.id) badArrow = true;
    if (arrow.start?.id && !skeletonShapeIds.has(arrow.start.id)) badArrow = true;
    if (arrow.end?.id && !skeletonShapeIds.has(arrow.end.id)) badArrow = true;
  }
  if (badArrow) {
    fail(scenario, "arrows reference existing shape ids", "broken binding");
  } else {
    pass("arrows reference existing shape ids");
  }

  // Invariant 4: customData.expandable + childPrompt round-trip
  for (const inputEl of inputShapes) {
    if (!inputEl.expandable) continue;
    const stamped = skeletons.find((s) => {
      const cd = (s as { customData?: ElementCustomData }).customData;
      return cd?.semanticId === inputEl.id;
    });
    if (!stamped) {
      fail(scenario, "expandable shapes stamped", `${inputEl.id} not in output`);
      continue;
    }
    const cd = (stamped as { customData?: ElementCustomData }).customData;
    if (!cd?.expandable) {
      fail(scenario, "expandable preserved", `${inputEl.id} lost expandable flag`);
    }
  }
  pass("expandable preserved");

  // Invariant 5: skeleton ids are unique (Excalidraw requires unique element ids)
  const seenIds = new Set<string>();
  let dupIds: string[] = [];
  for (const s of skeletons) {
    const id = (s as { id?: string }).id;
    if (!id) continue;
    if (seenIds.has(id)) dupIds.push(id);
    seenIds.add(id);
  }
  if (dupIds.length > 0) {
    fail(scenario, "skeleton ids unique", `duplicates: ${dupIds.join(", ")}`);
  } else {
    pass("skeleton ids unique");
  }
}

async function runScenario(name: string, node: ClaudeNodeOutput) {
  console.log(`\n[${name}]`);
  const tuned = applyLayoutTemplate(node);
  assertSkeletonInvariants(name, tuned);

  // Repo round-trip
  const { atlasId, rootNodeId } = await createAtlas({
    topic: name,
    root: tuned,
  });
  const fetched = await getAtlas(atlasId);
  if (!fetched || !fetched.nodes[rootNodeId]) {
    fail(name, "DB round-trip", "atlas/root missing after fetch");
    return;
  }
  const stored = fetched.nodes[rootNodeId];
  if (stored.claudeElements.length !== tuned.elements.length) {
    fail(
      name,
      "DB round-trip element count",
      `wrote ${tuned.elements.length} got ${stored.claudeElements.length}`,
    );
  } else {
    pass("DB round-trip preserves element count");
  }
}

// =============================================================================

const SCENARIOS: { name: string; node: ClaudeNodeOutput }[] = [];

// 1. Process: classic CPU pipeline
SCENARIOS.push({
  name: "1. process: CPU pipeline (5 stages)",
  node: {
    title: "CPU pipeline", format: "process", summary: "Classic 5-stage RISC.",
    elements: [
      { id: "fetch", kind: "box", label: "Fetch", x: 100, y: 500, expandable: true, childPrompt: "fetch internals" },
      { id: "decode", kind: "box", label: "Decode", x: 300, y: 500, expandable: true, childPrompt: "decoding" },
      { id: "execute", kind: "box", label: "Execute", x: 500, y: 500, expandable: true, childPrompt: "ALU" },
      { id: "memory", kind: "box", label: "Memory", x: 700, y: 500, expandable: true, childPrompt: "memory access" },
      { id: "writeback", kind: "box", label: "Writeback", x: 900, y: 500, expandable: false },
      { id: "a1", kind: "arrow", label: "", x: 0, y: 0, from: "fetch", to: "decode", expandable: false },
      { id: "a2", kind: "arrow", label: "", x: 0, y: 0, from: "decode", to: "execute", expandable: false },
      { id: "a3", kind: "arrow", label: "", x: 0, y: 0, from: "execute", to: "memory", expandable: false },
      { id: "a4", kind: "arrow", label: "", x: 0, y: 0, from: "memory", to: "writeback", expandable: false },
    ],
  },
});

// 2. History: French Revolution timeline
SCENARIOS.push({
  name: "2. history: French Revolution",
  node: {
    title: "프랑스 혁명", format: "history", summary: "Key events 1789-1799.",
    elements: [
      { id: "estates", kind: "box", label: "Estates-General", x: 150, y: 400, expandable: true, childPrompt: "Estates-General convocation" },
      { id: "bastille", kind: "box", label: "Bastille", x: 300, y: 200, expandable: true, childPrompt: "Storming of Bastille" },
      { id: "terror", kind: "box", label: "Reign of Terror", x: 600, y: 350, expandable: true, childPrompt: "1793 Terror" },
      { id: "napoleon", kind: "box", label: "Napoleon coup", x: 850, y: 600, expandable: false },
      { id: "h1", kind: "arrow", label: "", x: 0, y: 0, from: "estates", to: "bastille", expandable: false },
      { id: "h2", kind: "arrow", label: "", x: 0, y: 0, from: "bastille", to: "terror", expandable: false },
      { id: "h3", kind: "arrow", label: "", x: 0, y: 0, from: "terror", to: "napoleon", expandable: false },
    ],
  },
});

// 3. Biology: Animal cell with cross-section labels
SCENARIOS.push({
  name: "3. biology: Animal cell",
  node: {
    title: "Animal cell", format: "biology", summary: "Eukaryotic cell with organelles.",
    elements: [
      { id: "membrane", kind: "ellipse", label: "Cell membrane", x: 500, y: 500, w: 500, h: 500, expandable: true, childPrompt: "phospholipid bilayer" },
      { id: "nucleus", kind: "ellipse", label: "Nucleus", x: 480, y: 480, w: 130, h: 130, expandable: true, childPrompt: "nucleus details" },
      { id: "mito", kind: "ellipse", label: "Mitochondrion", x: 350, y: 380, w: 80, h: 50, expandable: true, childPrompt: "mitochondrion cross-section" },
      { id: "er", kind: "icon", label: "ER", x: 600, y: 350, expandable: false },
      { id: "ribo", kind: "icon", label: "Ribosome", x: 620, y: 600, expandable: false },
    ],
  },
});

// 4. Geography: Plate tectonics
SCENARIOS.push({
  name: "4. geography: Plate tectonics",
  node: {
    title: "Pacific plate boundaries", format: "geography", summary: "Major plate boundaries around the Pacific Ring of Fire.",
    elements: [
      { id: "pacific-plate", kind: "region", label: "Pacific Plate", x: 500, y: 500, w: 600, h: 400, expandable: true, childPrompt: "Pacific plate features" },
      { id: "north-am", kind: "region", label: "North American Plate", x: 200, y: 300, w: 250, h: 200, expandable: true, childPrompt: "NA plate" },
      { id: "san-andreas", kind: "text", label: "San Andreas Fault", x: 250, y: 400, expandable: false },
      { id: "ring", kind: "text", label: "Ring of Fire", x: 700, y: 700, expandable: false },
    ],
  },
});

// 5. Concept: Solar system
SCENARIOS.push({
  name: "5. concept: Solar system",
  node: {
    title: "Solar system", format: "concept", summary: "The Sun and the eight planets.",
    elements: [
      { id: "sun", kind: "ellipse", label: "Sun", x: 500, y: 500, w: 200, h: 200, expandable: true, childPrompt: "Sun details" },
      { id: "mercury", kind: "ellipse", label: "Mercury", x: 100, y: 100, w: 30, h: 30, expandable: true, childPrompt: "Mercury" },
      { id: "venus", kind: "ellipse", label: "Venus", x: 200, y: 100, w: 50, h: 50, expandable: true, childPrompt: "Venus" },
      { id: "earth", kind: "ellipse", label: "Earth", x: 300, y: 100, w: 60, h: 60, expandable: true, childPrompt: "Earth" },
      { id: "mars", kind: "ellipse", label: "Mars", x: 400, y: 100, w: 40, h: 40, expandable: true, childPrompt: "Mars" },
      { id: "jupiter", kind: "ellipse", label: "Jupiter", x: 500, y: 100, w: 100, h: 100, expandable: true, childPrompt: "Jupiter" },
      { id: "saturn", kind: "ellipse", label: "Saturn", x: 600, y: 100, w: 90, h: 90, expandable: false },
      { id: "uranus", kind: "ellipse", label: "Uranus", x: 700, y: 100, w: 70, h: 70, expandable: false },
      { id: "neptune", kind: "ellipse", label: "Neptune", x: 800, y: 100, w: 70, h: 70, expandable: false },
    ],
  },
});

// 6. Single element atlas
SCENARIOS.push({
  name: "6. edge: single-element atlas",
  node: {
    title: "Lonely concept", format: "concept", summary: "Just one thing.",
    elements: [
      { id: "alone", kind: "ellipse", label: "Alone", x: 500, y: 500, expandable: false },
    ],
  },
});

// 7. Duplicate element ids (malformed input)
SCENARIOS.push({
  name: "7. malformed: duplicate ids",
  node: {
    title: "Bad atlas", format: "concept", summary: "Duplicates.",
    elements: [
      { id: "a", kind: "box", label: "First", x: 200, y: 200, expandable: false },
      { id: "a", kind: "box", label: "Second (dup)", x: 800, y: 800, expandable: false },
      { id: "b", kind: "box", label: "Third", x: 500, y: 500, expandable: false },
    ],
  },
});

// 8. Coords out of normalized range
SCENARIOS.push({
  name: "8. edge: coords out of 0..1000 range",
  node: {
    title: "Out of bounds", format: "concept", summary: "Wonky coords.",
    elements: [
      { id: "neg", kind: "box", label: "Negative", x: -200, y: -100, expandable: false },
      { id: "huge", kind: "box", label: "Way out", x: 5000, y: 5000, expandable: false },
      { id: "ok", kind: "box", label: "Normal", x: 500, y: 500, expandable: false },
    ],
  },
});

// 9. Very long labels + non-ASCII
SCENARIOS.push({
  name: "9. edge: long + non-ASCII labels",
  node: {
    title: "Big labels 큰 레이블 🌍", format: "concept", summary: "Labels with unicode and emoji.",
    elements: [
      { id: "long", kind: "box", label: "A".repeat(60), x: 200, y: 200, expandable: false },
      { id: "korean", kind: "box", label: "한국어 텍스트 테스트", x: 500, y: 500, expandable: false },
      { id: "emoji", kind: "box", label: "🌍🚀💡", x: 800, y: 800, expandable: false },
    ],
  },
});

// 10. Many arrows to one hub (concept fan-in)
SCENARIOS.push({
  name: "10. structure: fan-in to hub",
  node: {
    title: "Hub", format: "concept", summary: "Many things converge.",
    elements: [
      { id: "hub", kind: "ellipse", label: "Hub", x: 500, y: 500, w: 150, h: 150, expandable: true, childPrompt: "Hub" },
      { id: "p1", kind: "box", label: "P1", x: 100, y: 100, expandable: false },
      { id: "p2", kind: "box", label: "P2", x: 900, y: 100, expandable: false },
      { id: "p3", kind: "box", label: "P3", x: 100, y: 900, expandable: false },
      { id: "p4", kind: "box", label: "P4", x: 900, y: 900, expandable: false },
      { id: "ar1", kind: "arrow", label: "", x: 0, y: 0, from: "p1", to: "hub", expandable: false },
      { id: "ar2", kind: "arrow", label: "", x: 0, y: 0, from: "p2", to: "hub", expandable: false },
      { id: "ar3", kind: "arrow", label: "", x: 0, y: 0, from: "p3", to: "hub", expandable: false },
      { id: "ar4", kind: "arrow", label: "", x: 0, y: 0, from: "p4", to: "hub", expandable: false },
    ],
  },
});

// 11. Disconnected components
SCENARIOS.push({
  name: "11. structure: disconnected components",
  node: {
    title: "Two clusters", format: "concept", summary: "Two unconnected groups.",
    elements: [
      { id: "g1a", kind: "box", label: "G1A", x: 200, y: 300, expandable: false },
      { id: "g1b", kind: "box", label: "G1B", x: 200, y: 600, expandable: false },
      { id: "g1ab", kind: "arrow", label: "", x: 0, y: 0, from: "g1a", to: "g1b", expandable: false },
      { id: "g2a", kind: "box", label: "G2A", x: 800, y: 300, expandable: false },
      { id: "g2b", kind: "box", label: "G2B", x: 800, y: 600, expandable: false },
      { id: "g2ab", kind: "arrow", label: "", x: 0, y: 0, from: "g2a", to: "g2b", expandable: false },
    ],
  },
});

// 12. Process with cycle (should no-op layout)
SCENARIOS.push({
  name: "12. structure: process with cycle",
  node: {
    title: "Loop", format: "process", summary: "A→B→C→A loop.",
    elements: [
      { id: "x", kind: "box", label: "X", x: 100, y: 100, expandable: false },
      { id: "y", kind: "box", label: "Y", x: 500, y: 100, expandable: false },
      { id: "z", kind: "box", label: "Z", x: 900, y: 100, expandable: false },
      { id: "xy", kind: "arrow", label: "", x: 0, y: 0, from: "x", to: "y", expandable: false },
      { id: "yz", kind: "arrow", label: "", x: 0, y: 0, from: "y", to: "z", expandable: false },
      { id: "zx", kind: "arrow", label: "", x: 0, y: 0, from: "z", to: "x", expandable: false },
    ],
  },
});

// 13. Arrow pointing at non-existent element
SCENARIOS.push({
  name: "13. malformed: arrow → unknown id",
  node: {
    title: "Broken arrows", format: "process", summary: "",
    elements: [
      { id: "real", kind: "box", label: "Real", x: 500, y: 500, expandable: false },
      { id: "ghost-arrow", kind: "arrow", label: "", x: 0, y: 0, from: "real", to: "ghost", expandable: false },
    ],
  },
});

// 14. Empty labels everywhere
SCENARIOS.push({
  name: "14. edge: empty labels",
  node: {
    title: "Untitled", format: "concept", summary: "",
    elements: [
      { id: "a", kind: "box", label: "", x: 300, y: 300, expandable: false },
      { id: "b", kind: "box", label: "", x: 700, y: 300, expandable: false },
      { id: "c", kind: "box", label: "", x: 500, y: 700, expandable: false },
    ],
  },
});

// 15. Special chars in element ids (URL/DOM safety)
SCENARIOS.push({
  name: "15. edge: special chars in ids",
  node: {
    title: "Special ids", format: "concept", summary: "",
    elements: [
      { id: "a.b/c d", kind: "box", label: "Dotted", x: 300, y: 300, expandable: true, childPrompt: "explore" },
      { id: "한글-id", kind: "box", label: "Korean id", x: 700, y: 300, expandable: false },
      { id: "<script>", kind: "box", label: "XSS attempt", x: 500, y: 700, expandable: false },
    ],
  },
});

// 16. Process with single arrow (only 2 nodes)
SCENARIOS.push({
  name: "16. structure: minimal 2-node process",
  node: {
    title: "Minimal", format: "process", summary: "Just two steps.",
    elements: [
      { id: "in", kind: "box", label: "In", x: 100, y: 500, expandable: false },
      { id: "out", kind: "box", label: "Out", x: 900, y: 500, expandable: false },
      { id: "io", kind: "arrow", label: "", x: 0, y: 0, from: "in", to: "out", expandable: false },
    ],
  },
});

async function main() {
  console.log("=== Atlas system stress test (15+ scenarios) ===");
  for (const s of SCENARIOS) {
    await runScenario(s.name, s.node);
  }

  // Cross-cutting: deep expansion chain
  console.log("\n[17. depth: 5-level expansion chain]");
  const baseRoot: ClaudeNodeOutput = {
    title: "Root", format: "concept", summary: "",
    elements: [
      { id: "deeper", kind: "box", label: "Go deeper", x: 500, y: 500, expandable: true, childPrompt: "deeper" },
      { id: "stay", kind: "box", label: "Stay", x: 200, y: 200, expandable: false },
    ],
  };
  const { atlasId, rootNodeId } = await createAtlas({ topic: "deep test", root: baseRoot });
  let parentId = rootNodeId;
  for (let depth = 1; depth <= 5; depth++) {
    const child: ClaudeNodeOutput = {
      title: `Level ${depth}`, format: "concept", summary: "",
      elements: [
        { id: `deeper-${depth}`, kind: "box", label: `Deeper ${depth}`, x: 500, y: 500, expandable: depth < 5, childPrompt: depth < 5 ? "deeper" : undefined },
      ],
    };
    const inserted = await addChildNode({
      atlasId,
      parentNodeId: parentId,
      parentElementId: depth === 1 ? "deeper" : `deeper-${depth - 1}`,
      child,
    });
    parentId = inserted.id;
  }
  const finalAtlas = await getAtlas(atlasId);
  if (!finalAtlas || Object.keys(finalAtlas.nodes).length !== 6) {
    fail("17. deep chain", "5+1 nodes after deep insert", `got ${Object.keys(finalAtlas?.nodes ?? {}).length}`);
  } else {
    pass("5+1 nodes persisted across deep chain");
  }

  // 18. Idempotent re-expand
  console.log("\n[18. idempotency: re-clicking same expandable]");
  const { atlasId: a18, rootNodeId: r18 } = await createAtlas({
    topic: "idempotency",
    root: baseRoot,
  });
  const child1 = await addChildNode({
    atlasId: a18,
    parentNodeId: r18,
    parentElementId: "deeper",
    child: { title: "First", format: "concept", summary: "", elements: [{ id: "x", kind: "box", label: "X", x: 500, y: 500, expandable: false }] },
  });
  // Now find via lookup — should match
  const cached = await findChildNode(a18, r18, "deeper");
  if (cached?.id !== child1.id) {
    fail("18. idempotency", "findChildNode returns the same row", `got ${cached?.id}, expected ${child1.id}`);
  } else {
    pass("findChildNode returns the same row on repeat");
  }
  // Try to add again — should reject
  let rejected = false;
  try {
    await addChildNode({
      atlasId: a18,
      parentNodeId: r18,
      parentElementId: "deeper",
      child: { title: "Second", format: "concept", summary: "", elements: [{ id: "y", kind: "box", label: "Y", x: 500, y: 500, expandable: false }] },
    });
  } catch {
    rejected = true;
  }
  if (!rejected) {
    fail("18. idempotency", "second insert rejected", "duplicate accepted");
  } else {
    pass("second insert rejected (UNIQUE constraint)");
  }

  // 19. JSON serialization round-trip integrity
  console.log("\n[19. integrity: JSON round-trip preserves all fields]");
  const big: ClaudeElement = {
    id: "rich",
    kind: "ellipse",
    label: "Rich element 🎨",
    x: 123.456,
    y: 789.012,
    w: 100,
    h: 80,
    expandable: true,
    childPrompt: "explore me with full detail",
  };
  const nodeRich: ClaudeNodeOutput = { title: "Rich", format: "concept", summary: "", elements: [big] };
  const { atlasId: aRich, rootNodeId: rRich } = await createAtlas({ topic: "rich", root: nodeRich });
  const fetchedRich = await getAtlas(aRich);
  const stored = fetchedRich?.nodes[rRich].claudeElements[0];
  if (!stored) {
    fail("19. integrity", "JSON round-trip", "node missing");
  } else {
    const fields: (keyof ClaudeElement)[] = ["id", "kind", "label", "x", "y", "w", "h", "expandable", "childPrompt"];
    let bad = false;
    for (const f of fields) {
      if (stored[f] !== big[f]) {
        bad = true;
        fail("19. integrity", `${f} preserved`, `wrote ${big[f]}, got ${stored[f]}`);
      }
    }
    if (!bad) pass("all 9 fields round-trip cleanly");
  }

  // 20. Storage backend identity check
  console.log("\n[20. config: storage backend identity]");
  const repoMod = await import("@/lib/atlas-repo");
  if (typeof repoMod.STORAGE_BACKEND !== "string") {
    fail("20. backend", "STORAGE_BACKEND export", "missing");
  } else {
    console.log(`    backend in use: ${repoMod.STORAGE_BACKEND}`);
    pass("STORAGE_BACKEND exposed");
  }

  // -- Summary --
  console.log("\n========================================");
  if (failures.length === 0) {
    console.log("✓ All scenarios passed");
  } else {
    console.log(`✗ ${failures.length} failure(s):`);
    for (const f of failures) {
      console.log(`  [${f.scenario}] ${f.invariant}: ${f.detail}`);
    }
  }
  console.log("========================================");
  closeDb();
  process.exit(failures.length === 0 ? 0 : 1);
}

main().catch((err) => {
  console.error(err);
  closeDb();
  process.exit(2);
});
