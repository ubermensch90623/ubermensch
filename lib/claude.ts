import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { anthropic, ATLAS_MODEL, ATLAS_MAX_TOKENS } from "./anthropic";
import {
  SYSTEM_PROMPT,
  ClaudeNodeOutputSchema,
  buildRootUserMessage,
  buildExpandUserMessage,
} from "./prompts";
import type { ClaudeNodeOutput, AtlasNode, ClaudeElement } from "@/types/atlas";

export class AtlasGenerationError extends Error {
  constructor(
    message: string,
    public readonly cause?: unknown,
  ) {
    super(message);
    this.name = "AtlasGenerationError";
  }
}

export async function generateRootAtlas(
  topic: string,
): Promise<ClaudeNodeOutput> {
  return generateAtlasNode(buildRootUserMessage(topic));
}

export async function generateChildNode(
  parent: AtlasNode,
  element: ClaudeElement,
): Promise<ClaudeNodeOutput> {
  return generateAtlasNode(buildExpandUserMessage(parent, element));
}

async function generateAtlasNode(
  userMessage: string,
): Promise<ClaudeNodeOutput> {
  try {
    const response = await anthropic.messages.parse({
      model: ATLAS_MODEL,
      max_tokens: ATLAS_MAX_TOKENS,
      thinking: { type: "adaptive" },
      system: [
        {
          type: "text",
          text: SYSTEM_PROMPT,
          cache_control: { type: "ephemeral" },
        },
      ],
      output_config: {
        effort: "high",
        format: zodOutputFormat(ClaudeNodeOutputSchema),
      },
      messages: [{ role: "user", content: userMessage }],
    });

    if (response.stop_reason === "refusal") {
      throw new AtlasGenerationError(
        "Claude declined to generate this diagram. Try rephrasing the topic.",
      );
    }
    if (response.stop_reason === "max_tokens") {
      throw new AtlasGenerationError(
        "Diagram generation hit the token limit. Try a narrower topic.",
      );
    }
    if (!response.parsed_output) {
      throw new AtlasGenerationError(
        "Claude returned an unparseable diagram structure.",
      );
    }

    return response.parsed_output;
  } catch (err) {
    if (err instanceof AtlasGenerationError) throw err;
    if (err instanceof Anthropic.APIError) {
      throw new AtlasGenerationError(
        `Anthropic API error (${err.status}): ${err.message}`,
        err,
      );
    }
    throw err;
  }
}
