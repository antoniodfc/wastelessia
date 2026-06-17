# Cost in USD per 1M tokens — updated June 2026
# Sources: Anthropic pricing page, OpenAI pricing page
_PRICING: dict[str, tuple[float, float]] = {
    # Anthropic
    "claude-opus-4-8":                  (15.00, 75.00),
    "claude-opus-4-7":                  (15.00, 75.00),
    "claude-sonnet-4-6":                ( 3.00, 15.00),
    "claude-sonnet-4-5":                ( 3.00, 15.00),
    "claude-haiku-4-5-20251001":        ( 0.80,  4.00),
    "claude-haiku-4-5":                 ( 0.80,  4.00),
    # OpenAI
    "gpt-4o":                           ( 2.50, 10.00),
    "gpt-4o-mini":                      ( 0.15,  0.60),
    "gpt-4.1":                          ( 2.00,  8.00),
    "gpt-4.1-mini":                     ( 0.40,  1.60),
    "o3":                               (10.00, 40.00),
    "o4-mini":                          ( 1.10,  4.40),
    # Google
    "gemini-2.5-pro":                   ( 1.25, 10.00),
    "gemini-2.5-flash":                 ( 0.15,  0.60),
}

_PER_TOKEN = 1_000_000


def calculate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    normalized = model.lower()
    for key, (price_in, price_out) in _PRICING.items():
        if normalized.startswith(key) or key in normalized:
            return (tokens_in * price_in + tokens_out * price_out) / _PER_TOKEN
    # Unknown model: return 0 rather than crash
    return 0.0
