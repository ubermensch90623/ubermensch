import { kv } from "@vercel/kv";
import { newAtlasId, newNodeId } from "./id";
import type {
  Atlas,
  AtlasNode,
  ClaudeNodeOutput,
} from "@/types/atlas";

interface AtlasRecord {
  id: string;
  rootNodeId: string;
  topic: string;
  createdAt: number;
  nodeIds: string[];
  childIndex: Record<string, string>;
}

const atlasKey = (atlasId: string) => `atlas:${atlasId}`;
const nodeKey = (nodeId: string) => `node:${nodeId}`;
const childIndexKey = (atlasId: string, parentNodeId: string, parentElementId: string) =>
  `${atlasId}::${parentNodeId}::${parentElementId}`;

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

  const atlasRecord: AtlasRecord = {
    id: atlasId,
    rootNodeId,
    topic: args.topic,
    createdAt: now,
    nodeIds: [rootNodeId],
    childIndex: {},
  };

  await Promise.all([
    kv.set(atlasKey(atlasId), atlasRecord),
    kv.set(nodeKey(rootNodeId), rootNode),
  ]);

  return { atlasId, rootNodeId };
}

export async function getAtlas(atlasId: string): Promise<Atlas | null> {
  const record = await kv.get<AtlasRecord>(atlasKey(atlasId));
  if (!record) return null;

  const nodeKeys = record.nodeIds.map(nodeKey);
  const nodeValues = nodeKeys.length
    ? await kv.mget<(AtlasNode | null)[]>(...nodeKeys)
    : [];

  const nodes: Record<string, AtlasNode> = {};
  for (const node of nodeValues) {
    if (node) nodes[node.id] = node;
  }

  return {
    id: record.id,
    rootNodeId: record.rootNodeId,
    topic: record.topic,
    createdAt: record.createdAt,
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
  const record = await kv.get<AtlasRecord>(atlasKey(atlasId));
  if (!record) return null;
  const childId = record.childIndex[childIndexKey(atlasId, parentNodeId, parentElementId)];
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
  const record = await kv.get<AtlasRecord>(atlasKey(args.atlasId));
  if (!record) {
    throw new Error(`Atlas ${args.atlasId} not found`);
  }
  const indexKey = childIndexKey(args.atlasId, args.parentNodeId, args.parentElementId);
  const existingChildId = record.childIndex[indexKey];
  if (existingChildId) {
    throw new Error(
      `Child already exists for (${args.parentNodeId}, ${args.parentElementId})`,
    );
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

  const updatedRecord: AtlasRecord = {
    ...record,
    nodeIds: [...record.nodeIds, nodeId],
    childIndex: { ...record.childIndex, [indexKey]: nodeId },
  };

  await Promise.all([
    kv.set(nodeKey(nodeId), node),
    kv.set(atlasKey(args.atlasId), updatedRecord),
  ]);

  return node;
}
