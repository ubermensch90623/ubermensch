import { z } from "zod";
import { generateChildNode, AtlasGenerationError } from "@/lib/claude";
import {
  getNode,
  findChildNode,
  addChildNode,
} from "@/lib/atlas-repo";

export const runtime = "nodejs";

const ExpandBody = z.object({
  parentNodeId: z.string().min(1),
  parentElementId: z.string().min(1),
});

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id: atlasId } = await params;

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const parsed = ExpandBody.safeParse(body);
  if (!parsed.success) {
    return Response.json(
      { error: "parentNodeId and parentElementId are required" },
      { status: 400 },
    );
  }
  const { parentNodeId, parentElementId } = parsed.data;

  const cached = await findChildNode(atlasId, parentNodeId, parentElementId);
  if (cached) {
    return Response.json({ node: cached, cached: true });
  }

  const parent = await getNode(parentNodeId);
  if (!parent || parent.atlasId !== atlasId) {
    return Response.json({ error: "Parent node not found" }, { status: 404 });
  }

  const element = parent.claudeElements.find((e) => e.id === parentElementId);
  if (!element) {
    return Response.json(
      { error: `Element "${parentElementId}" not found in parent node` },
      { status: 404 },
    );
  }
  if (!element.expandable) {
    return Response.json(
      { error: `Element "${parentElementId}" is not expandable` },
      { status: 400 },
    );
  }

  try {
    const child = await generateChildNode(parent, element);
    const node = await addChildNode({
      atlasId,
      parentNodeId,
      parentElementId,
      child,
    });
    return Response.json({ node, cached: false }, { status: 201 });
  } catch (err) {
    if (err instanceof AtlasGenerationError) {
      return Response.json({ error: err.message }, { status: 502 });
    }
    console.error("[/api/atlas/[id]/expand POST]", err);
    return Response.json({ error: "Internal error" }, { status: 500 });
  }
}
