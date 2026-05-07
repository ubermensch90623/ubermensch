import { getAtlas } from "@/lib/atlas-repo";

export const runtime = "nodejs";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const atlas = await getAtlas(id);
  if (!atlas) {
    return Response.json({ error: "Atlas not found" }, { status: 404 });
  }
  return Response.json({ atlas });
}
