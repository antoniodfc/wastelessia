// Cost in USD per 1M tokens — updated June 2026
// Sources: Anthropic pricing page, OpenAI pricing page
const PRICING: Record<string, [number, number]> = {
  // Anthropic
  "claude-opus-4-8": [15.0, 75.0],
  "claude-opus-4-7": [15.0, 75.0],
  "claude-sonnet-4-6": [3.0, 15.0],
  "claude-sonnet-4-5": [3.0, 15.0],
  "claude-haiku-4-5-20251001": [0.8, 4.0],
  "claude-haiku-4-5": [0.8, 4.0],
  // OpenAI
  "gpt-4o": [2.5, 10.0],
  "gpt-4o-mini": [0.15, 0.6],
  "gpt-4.1": [2.0, 8.0],
  "gpt-4.1-mini": [0.4, 1.6],
  o3: [10.0, 40.0],
  "o4-mini": [1.1, 4.4],
  // Google
  "gemini-2.5-pro": [1.25, 10.0],
  "gemini-2.5-flash": [0.15, 0.6],
};

const PER_TOKEN = 1_000_000;

export function calculateCost(model: string, tokensIn: number, tokensOut: number): number {
  const normalized = model.toLowerCase();
  for (const [key, [priceIn, priceOut]] of Object.entries(PRICING)) {
    if (normalized.startsWith(key) || normalized.includes(key)) {
      return (tokensIn * priceIn + tokensOut * priceOut) / PER_TOKEN;
    }
  }
  // Unknown model: return 0 rather than throw.
  return 0;
}
