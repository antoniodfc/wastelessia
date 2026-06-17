import { afterEach, describe, expect, it, vi } from "vitest";

import { calculateCost } from "../src/pricing.js";
import { extractUsage, track } from "../src/track.js";
import * as sender from "../src/sender.js";
import type { TrackEvent } from "../src/types.js";

function anthropicResponse(model = "claude-sonnet-4-6", tokensIn = 100, tokensOut = 50) {
  return { model, usage: { input_tokens: tokensIn, output_tokens: tokensOut } };
}

function openaiResponse(model = "gpt-4o", promptTokens = 100, completionTokens = 50) {
  return { model, usage: { prompt_tokens: promptTokens, completion_tokens: completionTokens } };
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("extractUsage", () => {
  it("parses Anthropic responses", () => {
    expect(extractUsage(anthropicResponse())).toEqual({
      model: "claude-sonnet-4-6",
      tokensIn: 100,
      tokensOut: 50,
    });
  });

  it("parses OpenAI responses", () => {
    expect(extractUsage(openaiResponse())).toEqual({
      model: "gpt-4o",
      tokensIn: 100,
      tokensOut: 50,
    });
  });

  it("returns null for non-LLM values", () => {
    expect(extractUsage(null)).toBeNull();
    expect(extractUsage({ foo: "bar" })).toBeNull();
    expect(extractUsage("string")).toBeNull();
  });
});

describe("calculateCost", () => {
  it("prices sonnet correctly", () => {
    expect(calculateCost("claude-sonnet-4-6", 1_000_000, 0)).toBeCloseTo(3.0, 5);
  });

  it("returns 0 for unknown models", () => {
    expect(calculateCost("unknown-model-x", 1000, 500)).toBe(0);
  });
});

describe("track", () => {
  it("returns the wrapped result and sends an event", async () => {
    const spy = vi.spyOn(sender, "sendEventAsync").mockResolvedValue();

    const result = await track({ team: "backend", feature: "search", env: "prod" }, async () =>
      anthropicResponse(),
    );

    expect(result).toEqual(anthropicResponse());
    expect(spy).toHaveBeenCalledOnce();
    const event = spy.mock.calls[0]![0] as TrackEvent;
    expect(event.tags).toEqual({ team: "backend", feature: "search", env: "prod" });
    expect(event.tokens_in).toBe(100);
    expect(event.tokens_out).toBe(50);
    expect(event.success).toBe(true);
  });

  it("rethrows and does not send when the call throws before returning", async () => {
    const spy = vi.spyOn(sender, "sendEventAsync").mockResolvedValue();

    await expect(
      track({ feature: "broken" }, async () => {
        throw new Error("boom");
      }),
    ).rejects.toThrow("boom");

    // No usage to extract when the call fails before producing a response.
    expect(spy).not.toHaveBeenCalled();
  });

  it("omits undefined tags", async () => {
    const spy = vi.spyOn(sender, "sendEventAsync").mockResolvedValue();

    await track({ team: "ml" }, async () => anthropicResponse());

    const event = spy.mock.calls[0]![0] as TrackEvent;
    expect(event.tags).toEqual({ team: "ml" });
  });
});
