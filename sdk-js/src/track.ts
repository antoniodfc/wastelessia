import { calculateCost } from "./pricing.js";
import { sendEventAsync } from "./sender.js";
import type { Tags } from "./types.js";

interface Usage {
  model: string;
  tokensIn: number;
  tokensOut: number;
}

/**
 * Wrap an LLM call to capture its usage metadata (tokens, cost, latency, tags)
 * and send it to Wastelessia asynchronously — without touching prompt content.
 *
 * @example
 * const res = await track(
 *   { team: "backend", feature: "search", env: "prod" },
 *   () => anthropic.messages.create({ model: "claude-sonnet-4-6", ... }),
 * );
 */
export async function track<T>(tags: Tags, fn: () => Promise<T>): Promise<T> {
  const start = Date.now();
  let success = true;
  let result: T | undefined;
  try {
    result = await fn();
    return result;
  } catch (err) {
    success = false;
    throw err;
  } finally {
    maybeSend(result, Date.now() - start, success, cleanTags(tags));
  }
}

function cleanTags(tags: Tags): Tags {
  const out: Tags = {};
  for (const key of ["team", "feature", "env", "client"] as const) {
    const value = tags[key];
    if (value !== undefined && value !== null) {
      out[key] = value;
    }
  }
  return out;
}

function maybeSend(response: unknown, elapsedMs: number, success: boolean, tags: Tags): void {
  const usage = extractUsage(response);
  if (usage === null) {
    return;
  }
  void sendEventAsync({
    timestamp: new Date().toISOString(),
    model: usage.model,
    tokens_in: usage.tokensIn,
    tokens_out: usage.tokensOut,
    cost_usd: calculateCost(usage.model, usage.tokensIn, usage.tokensOut),
    duration_ms: elapsedMs,
    success,
    tags,
  });
}

function extractUsage(response: unknown): Usage | null {
  if (response === null || typeof response !== "object") {
    return null;
  }
  const r = response as Record<string, unknown>;
  const model = r.model;
  const usage = r.usage;
  if (typeof model !== "string" || usage === null || typeof usage !== "object") {
    return null;
  }
  const u = usage as Record<string, unknown>;

  // Anthropic SDK: input_tokens / output_tokens
  if (typeof u.input_tokens === "number" && typeof u.output_tokens === "number") {
    return { model, tokensIn: u.input_tokens, tokensOut: u.output_tokens };
  }

  // OpenAI SDK: prompt_tokens / completion_tokens
  if (typeof u.prompt_tokens === "number" && typeof u.completion_tokens === "number") {
    return { model, tokensIn: u.prompt_tokens, tokensOut: u.completion_tokens };
  }

  return null;
}

// Exported for tests.
export { extractUsage };
