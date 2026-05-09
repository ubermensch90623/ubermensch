import { kv } from "@vercel/kv";
import { newAtlasId, newNodeId } from "./id";
import type {
  Atlas,
  AtlasNode,
  ClaudeNodeOutput,
} from "@/types/atlas";

interface AtlasMeta {
  id: string;
  rootNodeId: string;
  topic: string;
  createdAt: number;
}

const atlasKey = (atlasId: string) => `atlas:${atlasId}`;
const nodeKey = (nodeId: string) => `node:${nodeId}`;
const atlasNodesKey = (atlasId: string) => `atlas-nodes:${atlasId}`;
const childLinkKey = (
  atlasId: string,
  parentNodeId: string,
  parentElementId: string,
) => `child-link:${atlasId}::${parentNodeId}::${parentElementId}`;

export interface CreateAtlasArgs {
  topic: string;
  root: ClaudeNodeOutput;
}

export async function createAtlas(args: CreateAtlasArgs): Promise<{
  atlasId: string;
  rootNodeId: string;
}> {
  const atlasId = newAtlasId();
  const rootNodeId = newNodeId();
  const now = Date.now();

  const rootNode: AtlasNode = {
    id: rootNodeId,
    atlasId,
    parentId: null,
    parentElementId: null,
    title: args.root.title,
    format: args.root.format,
    summary: args.root.summary,
    claudeElements: args.root.elements,
    createdAt: now,
  };

  const meta: AtlasMeta = {
    id: atlasId,
    rootNodeId,
    topic: args.topic,
    createdAt: now,
  };

  // Order matters: write the node first, then the atlas record (the
  // visibility boundary). atlas-nodes set is best-effort — getAtlas always
  // includes rootNodeId regardless of the set, so a missing sadd is OK.
  await kv.set(nodeKey(rootNodeId), rootNode);
  await kv.set(atlasKey(atlasId), meta);
  await kv.sadd(atlasNodesKey(atlasId), rootNodeId);

  return { atlasId, rootNodeId };
}

export async function getAtlas(atlasId: string): Promise<Atlas | null> {
  const meta = await kv.get<AtlasMeta>(atlasKey(atlasId));
  if (!meta) return null;

  const setMembers =
    (await kv.smembers(atlasNodesKey(atlasId))) ?? [];
  const ids = new Set<string>(setMembers as string[]);
  ids.add(meta.rootNodeId);

  const idArray = [...ids];
  const keys = idArray.map(nodeKey);
  const values = keys.length
    ? await kv.mget<(AtlasNode | null)[]>(...keys)
    : [];

  const nodes: Record<string, AtlasNode> = {};
  values.forEach((node, i) => {
    if (node) nodes[idArray[i]] = node;
  });

  return {
    id: meta.id,
    rootNodeId: meta.rootNodeId,
    topic: meta.topic,
    createdAt: meta.createdAt,
    nodes,
  };
}

export async function getNode(nodeId: string): Promise<AtlasNode | null> {
  return (await kv.get<AtlasNode>(nodeKey(nodeId))) ?? null;
}

export async function findChildNode(
  atlasId: string,
  parentNodeId: string,
  parentElementId: string,
): Promise<AtlasNode | null> {
  const childId = await kv.get<string>(
    childLinkKey(atlasId, parentNodeId, parentElementId),
  );
  if (!childId) return null;
  return await getNode(childId);
}

export interface AddChildNodeArgs {
  atlasId: string;
  parentNodeId: string;
  parentElementId: string;
  child: ClaudeNodeOutput;
}

export async function addChildNode(args: AddChildNodeArgs): Promise<AtlasNode> {
  const meta = await kv.get<AtlasMeta>(atlasKey(args.atlasId));
  if (!meta) {
    throw new Error(`Atlas ${args.atlasId} not found`);
  }

  const nodeId = newNodeId();
  const now = Date.now();
  const node: AtlasNode = {
    id: nodeId,
    atlasId: args.atlasId,
    parentId: args.parentNodeId,
    parentElementId: args.parentElementId,
    title: args.child.title,
    format: args.child.format,
    summary: args.child.summary,
    claudeElements: args.child.elements,
    createdAt: now,
  };

  // Step 1: write the node payload first.
  await kv.set(nodeKey(nodeId), node);

  // Step 2: race-safe link reservation. NX semantics make this the
  // atomic equivalent of the SQLite UNIQUE(atlas_id, parent_id,
  // parent_element_id) constraint. If two concurrent calls race, only
  // one wins.
  const linkKey = childLinkKey(
    args.atlasId,
    args.parentNodeId,
    args.parentElementId,
  );
  const reserved = await kv.set(linkKey, nodeId, { nx: true });
  if (reserved !== "OK") {
    await kv.del(nodeKey(nodeId));
    throw new Error(
      `UNIQUE conflict: child already exists for (${args.parentNodeId}, ${args.parentElementId})`,
    );
  }

  // Step 3: track in the atlas's node set (best effort — getAtlas
  // tolerates a missing entry by always including rootNodeId).
  await kv.sadd(atlasNodesKey(args.atlasId), nodeId);

  return node;
}
