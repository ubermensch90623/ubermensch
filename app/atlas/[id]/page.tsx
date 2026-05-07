import { notFound } from "next/navigation";
import { getAtlas } from "@/lib/atlas-repo";
import { AtlasViewer } from "./AtlasViewer";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export default async function AtlasPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const atlas = await getAtlas(id);
  if (!atlas) notFound();

  return <AtlasViewer atlas={atlas} />;
}
