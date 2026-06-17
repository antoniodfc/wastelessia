"""Data access layer.

Defines the repository protocol used by routes, the Postgres implementation,
and an in-memory fake used in tests (so the API can be tested without a live DB).
"""

import uuid
from typing import Optional, Protocol

from psycopg_pool import AsyncConnectionPool

from .schemas import EventIn


class Repository(Protocol):
    async def resolve_project(self, api_key: str) -> Optional[str]:
        """Return the project_id for an API key, or None if unknown."""
        ...

    async def insert_event(self, project_id: str, event: EventIn) -> str:
        """Persist an event and return its id."""
        ...


class PostgresRepository:
    def __init__(self, pool: AsyncConnectionPool):
        self._pool = pool

    async def resolve_project(self, api_key: str) -> Optional[str]:
        async with self._pool.connection() as conn:
            cur = await conn.execute(
                "SELECT id FROM projects WHERE api_key = %s", (api_key,)
            )
            row = await cur.fetchone()
            return str(row[0]) if row else None

    async def insert_event(self, project_id: str, event: EventIn) -> str:
        async with self._pool.connection() as conn:
            cur = await conn.execute(
                """
                INSERT INTO events (
                    project_id, timestamp, model, tokens_in, tokens_out,
                    cost_usd, duration_ms, success,
                    tag_team, tag_feature, tag_env, tag_client
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
                """,
                (
                    project_id,
                    event.timestamp,
                    event.model,
                    event.tokens_in,
                    event.tokens_out,
                    event.cost_usd,
                    event.duration_ms,
                    event.success,
                    event.tags.team,
                    event.tags.feature,
                    event.tags.env,
                    event.tags.client,
                ),
            )
            row = await cur.fetchone()
            return str(row[0])


class InMemoryRepository:
    """Test double — no database required."""

    def __init__(self, keys: Optional[dict[str, str]] = None):
        # api_key -> project_id
        self.keys = keys or {}
        self.events: list[tuple[str, EventIn]] = []

    async def resolve_project(self, api_key: str) -> Optional[str]:
        return self.keys.get(api_key)

    async def insert_event(self, project_id: str, event: EventIn) -> str:
        event_id = str(uuid.uuid4())
        self.events.append((project_id, event))
        return event_id
