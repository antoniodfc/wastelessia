# wastelessia (JS/TS SDK)

Tracker la dépense LLM par équipe, feature et client — sans proxy, sans toucher au contenu des prompts. Node.js 18+ (CommonJS et ESM).

## Installation

```bash
npm install wastelessia
```

## Usage

```ts
import { configure, track } from "wastelessia";

configure({ apiKey: "proj_xxx" }); // ou via WASTELESSIA_API_KEY

const result = await track(
  { team: "backend", feature: "search", env: "prod" },
  () =>
    anthropic.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 200,
      messages: [{ role: "user", content: prompt }],
    }),
);
```

`track` exécute la fonction, mesure tokens/coût/latence depuis la réponse, puis
envoie l'event en asynchrone (fire-and-forget — aucune latence ajoutée au call LLM).

Réponses supportées automatiquement : SDK **Anthropic** (`input_tokens`/`output_tokens`)
et **OpenAI** (`prompt_tokens`/`completion_tokens`).

## Configuration

| Variable d'env          | Défaut                          | Rôle                          |
|-------------------------|---------------------------------|-------------------------------|
| `WASTELESSIA_API_KEY`   | —                               | Clé projet (`proj_xxx`)       |
| `WASTELESSIA_ENDPOINT`  | `https://api.wastelessia.com`   | URL du backend                |
| `WASTELESSIA_DEBUG`     | —                               | `1` imprime les events captés |

`configure({ apiKey, endpoint })` prend le pas sur les variables d'env.

## Ce que le SDK ne fait pas

- Stocker les prompts ou les réponses
- Intercepter le trafic réseau
- Modifier les requêtes envoyées aux LLMs

## Développement

```bash
npm install
npm test          # vitest
npm run build     # tsup -> dist/ (ESM + CJS + types)
npm run typecheck
```
