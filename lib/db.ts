import Database from "better-sqlite3";
import path from "node:path";
import fs from "node:fs";

const DATABASE_PATH = process.env.DATABASE_PATH ?? "./data/atlas.db";

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (_db) return _db;

  const absolutePath = path.resolve(
    /* turbopackIgnore: true */ process.cwd(),
    DATABASE_PATH,
  );
  fs.mkdirSync(path.dirname(absolutePath), { recursive: true });

  const db = new Database(absolutePath);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");

  _db = db;
  return db;
}

export function closeDb(): void {
  if (_db) {
    _db.close();
    _db = null;
  }
}

export const SCHEMA_SQL = `
CREATE TABLE IF NOT EXISTS atlas (
  id            TEXT PRIMARY KEY,
  root_node_id  TEXT NOT NULL,
  topic         TEXT NOT NULL,
  created_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS node (
  id                       TEXT PRIMARY KEY,
  atlas_id                 TEXT NOT NULL REFERENCES atlas(id) ON DELETE CASCADE,
  parent_id                TEXT,
  parent_element_id        TEXT,
  title                    TEXT NOT NULL,
  format                   TEXT NOT NULL,
  summary                  TEXT NOT NULL,
  claude_elements_json     TEXT NOT NULL,
  created_at               INTEGER NOT NULL,
  UNIQUE(atlas_id, parent_id, parent_element_id)
);

CREATE INDEX IF NOT EXISTS idx_node_atlas ON node(atlas_id);
`;

export function applySchema(db: Database.Database): void {
  db.exec(SCHEMA_SQL);
}
