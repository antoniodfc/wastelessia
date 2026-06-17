import os

from psycopg_pool import AsyncConnectionPool

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/wastelessia"
)

# Created lazily on app startup (see main.lifespan).
pool: AsyncConnectionPool | None = None


def make_pool() -> AsyncConnectionPool:
    # open=False so the pool is opened explicitly in the lifespan handler.
    return AsyncConnectionPool(DATABASE_URL, open=False)
