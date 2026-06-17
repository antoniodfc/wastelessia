from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import db
from .deps import set_repository
from .repository import PostgresRepository
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.pool = db.make_pool()
    await db.pool.open()
    set_repository(PostgresRepository(db.pool))
    try:
        yield
    finally:
        await db.pool.close()


app = FastAPI(title="Wastelessia API", version="0.1.0", lifespan=lifespan)
app.include_router(router)
