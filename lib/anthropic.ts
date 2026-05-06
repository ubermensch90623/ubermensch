import Anthropic from "@anthropic-ai/sdk";

export const anthropic = new Anthropic();

export const ATLAS_MODEL = process.env.ANTHROPIC_MODEL ?? "claude-opus-4-7";

export const ATLAS_MAX_TOKENS = 16000;
