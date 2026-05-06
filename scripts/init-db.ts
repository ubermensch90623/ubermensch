import { getDb, applySchema, closeDb } from "@/lib/db";

const db = getDb();
applySchema(db);

const tables = db
  .prepare("SELECT name FROM sqlite_master WHERE type='table'")
  .all() as Array<{ name: string }>;

console.log("✓ Schema applied. Tables:");
for (const t of tables) {
  if (t.name.startsWith("sqlite_")) continue;
  console.log(`  - ${t.name}`);
}

closeDb();
