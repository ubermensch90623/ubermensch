import { customAlphabet } from "nanoid";

const URL_SAFE_ALPHABET =
  "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

const atlasIdGen = customAlphabet(URL_SAFE_ALPHABET, 10);
const nodeIdGen = customAlphabet(URL_SAFE_ALPHABET, 12);

export function newAtlasId(): string {
  return atlasIdGen();
}

export function newNodeId(): string {
  return nodeIdGen();
}
