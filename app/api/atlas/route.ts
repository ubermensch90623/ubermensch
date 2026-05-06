import { z } from "zod";
import { generateRootAtlas, AtlasGenerationError } from "@/lib/claude";
import { createAtlas } from "@/lib/atlas-repo";

export const runtime = "nodejs";

const CreateBody = z.object({
  topic: z.string().trim().min(3).max(200),
});

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const parsed = CreateBody.safeParse(body);
  if (!parsed.success) {
    return Response.json(
      { error: "topic must be a string of 3–200 chars" },
      { status: 400 },
    );
  }
  const { topic } = parsed.data;

  try {
    const root = await generateRootAtlas(topic);
    const { atlasId, rootNodeId } = createAtlas({ topic, root });
    return Response.json({ id: atlasId, rootNodeId }, { status: 201 });
  } catch (err) {
    if (err instanceof AtlasGenerationError) {
      return Response.json({ error: err.message }, { status: 502 });
    }
    console.error("[/api/atlas POST]", err);
    return Response.json({ error: "Internal error" }, { status: 500 });
  }
}
