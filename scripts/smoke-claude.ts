import { generateRootAtlas, generateChildNode } from "@/lib/claude";
import type { AtlasNode } from "@/types/atlas";

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error(
      "✗ ANTHROPIC_API_KEY not set. Add it to .env.local (or your shell) and re-run.",
    );
    process.exit(1);
  }

  const topic = process.argv[2] ?? "How a CPU executes an instruction";
  console.log(`\n[1] Generating root atlas for: "${topic}"\n`);

  const t0 = Date.now();
  const root = await generateRootAtlas(topic);
  const t1 = Date.now();

  console.log(`✓ Root generated in ${((t1 - t0) / 1000).toFixed(1)}s`);
  console.log(`  Title:   ${root.title}`);
  console.log(`  Format:  ${root.format}`);
  console.log(`  Summary: ${root.summary}`);
  console.log(`  Elements: ${root.elements.length}`);
  for (const el of root.elements) {
    console.log(
      `    - [${el.kind}] ${el.id} "${el.label}" @ (${el.x}, ${el.y}) expandable=${el.expandable}`,
    );
  }

  const expandable = root.elements.find((e) => e.expandable && e.kind !== "arrow");
  if (!expandable) {
    console.log("\n[!] No expandable element found — skipping child test");
    return;
  }

  console.log(`\n[2] Expanding "${expandable.label}"...\n`);
  const fakeParent: AtlasNode = {
    id: "smoke-root",
    atlasId: "smoke",
    parentId: null,
    parentElementId: null,
    title: root.title,
    format: root.format,
    summary: root.summary,
    claudeElements: root.elements,
    createdAt: Date.now(),
  };

  const t2 = Date.now();
  const child = await generateChildNode(fakeParent, expandable);
  const t3 = Date.now();

  console.log(`✓ Child generated in ${((t3 - t2) / 1000).toFixed(1)}s`);
  console.log(`  Title:   ${child.title}`);
  console.log(`  Format:  ${child.format}`);
  console.log(`  Summary: ${child.summary}`);
  console.log(`  Elements: ${child.elements.length}`);
}

main().catch((err) => {
  console.error("\n✗ Smoke test failed:", err);
  process.exit(1);
});
