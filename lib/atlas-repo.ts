import { getDb } from "./db";
import { newAtlasId, newNodeId } from "./id";
import type {
  Atlas,
  AtlasNode,
  ClaudeElement,
  ClaudeNodeOutput,
  Format,
} from "@/types/atlas";

interface AtlasRow {
  id: string;
  root_node_id: string;
  topic: string;
  created_at: number;
}

interface NodeRow {
  id: string;
  atlas_id: string;
  parent_id: string | null;
  parent_element_id: string | null;
  title: string;
  format: string;
  summary: string;
  claude_elements_json: string;
  created_at: number;
}

function rowToNode(row: NodeRow): AtlasNode {
  return {
    id: row.id,
    atlasId: row.atlas_id,
    parentId: row.parent_id,
    parentElementId: row.parent_element_id,
    title: row.title,
    format: row.format as Format,
    summary: row.summary,
    claudeElements: JSON.parse(row.claude_elements_json) as ClaudeElement[],
    createdAt: row.created_at,
  };
}

export interface CreateAtlasArgs {
  topic: string;
  root: ClaudeNodeOutput;
}

export function createAtlas(args: CreateAtlasArgs): {
  atlasId: string;
  rootNodeId: string;
} {
  const db = getDb();
  const atlasId = newAtlasId();
  const rootNodeId = newNodeId();
  const now = Date.now();

  const tx = db.transaction(() => {
    db.prepare(
      `INSERT INTO atlas (id, root_node_id, topic, created_at)
       VALUES (?, ?, ?, ?)`,
    ).run(atlasId, rootNodeId, args.topic, now);

    db.prepare(
      `INSERT INTO node (
         id, atlas_id, parent_id, parent_element_id,
         title, format, summary, claude_elements_json, created_at
       ) VALUES (?, ?, NULL, NULL, ?, ?, ?, ?, ?)`,
    ).run(
      rootNodeId,
      atlasId,
      args.root.title,
      args.root.format,
      args.root.summary,
      JSON.stringify(args.root.elements),
      now,
    );
  });
  tx();

  return { atlasId, rootNodeId };
}

export function getAtlas(atlasId: string): Atlas | null {
  const db = getDb();
  const atlasRow = db
    .prepare(`SELECT * FROM atlas WHERE id = ?`)
    .get(atlasId) as AtlasRow | undefined;
  if (!atlasRow) return null;

  const nodeRows = db
    .prepare(`SELECT * FROM node WHERE atlas_id = ?`)
    .all(atlasId) as NodeRow[];

  const nodes: Record<string, AtlasNode> = {};
  for (const row of nodeRows) {
    nodes[row.id] = rowToNode(row);
  }

  return {
    id: atlasRow.id,
    rootNodeId: atlasRow.root_node_id,
    topic: atlasRow.topic,
    createdAt: atlasRow.created_at,
    nodes,
  };
}

export function getNode(nodeId: string): AtlasNode | null {
  const db = getDb();
  const row = db.prepare(`SELECT * FROM node WHERE id = ?`).get(nodeId) as
    | NodeRow
    | undefined;
  return row ? rowToNode(row) : null;
}

export function findChildNode(
  atlasId: string,
  parentNodeId: string,
  parentElementId: string,
): AtlasNode | null {
  const db = getDb();
  const row = db
    .prepare(
      `SELECT * FROM node
       WHERE atlas_id = ? AND parent_id = ? AND parent_element_id = ?`,
    )
    .get(atlasId, parentNodeId, parentElementId) as NodeRow | undefined;
  return row ? rowToNode(row) : null;
}

export interface AddChildNodeArgs {
  atlasId: string;
  parentNodeId: string;
  parentElementId: string;
  child: ClaudeNodeOutput;
}

export function addChildNode(args: AddChildNodeArgs): AtlasNode {
  const db = getDb();
  const nodeId = newNodeId();
  const now = Date.now();

  db.prepare(
    `INSERT INTO node (
       id, atlas_id, parent_id, parent_element_id,
       title, format, summary, claude_elements_json, created_at
     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  ).run(
    nodeId,
    args.atlasId,
    args.parentNodeId,
    args.parentElementId,
    args.child.title,
    args.child.format,
    args.child.summary,
    JSON.stringify(args.child.elements),
    now,
  );

  const node = getNode(nodeId);
  if (!node) {
    throw new Error(`Failed to load just-inserted node ${nodeId}`);
  }
  return node;
}
