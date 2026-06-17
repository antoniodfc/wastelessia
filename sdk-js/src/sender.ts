import { getConfig } from "./config.js";
import type { TrackEvent } from "./types.js";

const DEBUG = ["1", "true", "yes"].includes((process.env.WASTELESSIA_DEBUG ?? "").toLowerCase());

/**
 * Fire-and-forget: never throws, never blocks the caller.
 * The returned promise is for tests; production code does not await it.
 */
export function sendEventAsync(event: TrackEvent): Promise<void> {
  if (DEBUG) {
    console.log(`[wastelessia] ${JSON.stringify(event)}`);
  }

  const config = getConfig();
  if (!config.apiKey) {
    return Promise.resolve();
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);

  return fetch(`${config.endpoint}/v1/events`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${config.apiKey}`,
    },
    body: JSON.stringify(event),
    signal: controller.signal,
  })
    .then(() => undefined)
    .catch(() => undefined) // swallow all errors
    .finally(() => clearTimeout(timeout));
}
