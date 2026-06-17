# Wastelessia — Backend API

FastAPI + PostgreSQL. Reçoit les events envoyés par le SDK (PRD §5).

## Lancer en local

```bash
# 1. Postgres (Docker)
docker run -d --name wastelessia-pg \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=wastelessia \
  -p 5432:5432 postgres:16

# 2. Schéma
psql postgresql://postgres:postgres@localhost:5432/wastelessia -f schema.sql

# 3. Dépendances
pip install -r requirements.txt

# 4. Serveur
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wastelessia
uvicorn app.main:app --reload
```

API sur http://localhost:8000 — docs interactives sur `/docs`.

## Créer un projet (obtenir une clé API)

L'auth repose sur un Bearer token mappé à un `project_id`. Pour créer un projet de test :

```sql
INSERT INTO projects (name, api_key) VALUES ('demo', 'proj_demo123');
```

## Tester l'endpoint

```bash
curl -X POST http://localhost:8000/v1/events \
  -H "Authorization: Bearer proj_demo123" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-06-17T14:32:00Z",
    "model": "claude-sonnet-4-6",
    "tokens_in": 1240,
    "tokens_out": 380,
    "cost_usd": 0.0058,
    "duration_ms": 1240,
    "success": true,
    "tags": {"team": "backend", "feature": "search", "env": "prod"}
  }'
```

→ `202 Accepted` avec l'`id` de l'event.

## Brancher le SDK dessus

```bash
export WASTELESSIA_API_KEY=proj_demo123
export WASTELESSIA_ENDPOINT=http://localhost:8000
python examples/demo_claude.py   # depuis la racine du repo
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Les tests utilisent un dépôt en mémoire (`InMemoryRepository`) — aucune base requise.

## Endpoints

| Méthode | Chemin        | Auth   | Description                       |
|---------|---------------|--------|-----------------------------------|
| GET     | `/health`     | non    | Liveness check                    |
| POST    | `/v1/events`  | Bearer | Ingestion d'un event (202)        |
