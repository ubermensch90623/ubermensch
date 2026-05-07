import type * as RepoApi from "./atlas-repo-sqlite";

const backendName =
  process.env.STORAGE_BACKEND === "vercel-kv" ? "vercel-kv" : "sqlite";

const impl: typeof RepoApi =
  backendName === "vercel-kv"
    ? (require("./atlas-repo-kv") as typeof RepoApi)
    : (require("./atlas-repo-sqlite") as typeof RepoApi);

export const createAtlas = impl.createAtlas;
export const getAtlas = impl.getAtlas;
export const getNode = impl.getNode;
export const findChildNode = impl.findChildNode;
export const addChildNode = impl.addChildNode;

export type { CreateAtlasArgs, AddChildNodeArgs } from "./atlas-repo-sqlite";

export const STORAGE_BACKEND = backendName;
