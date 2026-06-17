#!/usr/bin/env bash
# Test end-to-end (PRD §7, J5) : SDK -> backend -> Postgres.
# Démarre la stack, envoie un event via le SDK Python, vérifie qu'il est en base.
#
#   ./e2e.sh            # lance la stack, teste, laisse tourner
#   ./e2e.sh --down     # teste puis arrête tout
set -euo pipefail

cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"

echo "→ Démarrage Postgres + API (docker compose)…"
docker compose up -d --build --wait

echo "→ Seed du projet de test (proj_demo123)…"
docker compose exec -T db psql -U postgres -d wastelessia < seed.sql

echo "→ Envoi d'un event via le SDK Python…"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="python3"
WASTELESSIA_ENDPOINT="http://localhost:8000" \
WASTELESSIA_API_KEY="proj_demo123" \
PYTHONPATH="$ROOT/src" \
"$PY" - <<'PYEOF'
import time
from unittest.mock import MagicMock
from wastelessia import track

def fake_response():
    r = MagicMock()
    r.model = "claude-sonnet-4-6"
    r.usage.input_tokens = 1240
    r.usage.output_tokens = 380
    del r.usage.prompt_tokens
    return r

@track(team="founder", feature="e2e", env="test")
def call():
    return fake_response()

call()
time.sleep(1)  # laisse le worker daemon flusher l'envoi HTTP
print("  event envoyé")
PYEOF

echo "→ Vérification en base…"
COUNT=$(docker compose exec -T db psql -U postgres -d wastelessia -tA \
  -c "SELECT count(*) FROM events WHERE tag_feature = 'e2e';")
echo "  events 'e2e' en base : $COUNT"

if [ "$COUNT" -ge 1 ]; then
  echo "✓ END-TO-END OK"
  docker compose exec -T db psql -U postgres -d wastelessia \
    -c "SELECT model, tokens_in, tokens_out, cost_usd, tag_team, tag_feature FROM events WHERE tag_feature='e2e' ORDER BY created_at DESC LIMIT 1;"
else
  echo "✗ ÉCHEC : aucun event trouvé"
  exit 1
fi

if [ "${1:-}" = "--down" ]; then
  echo "→ Arrêt de la stack…"
  docker compose down
fi
