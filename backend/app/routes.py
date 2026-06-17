from typing import Annotated

from fastapi import APIRouter, Depends, status

from .deps import get_project_id, get_repository
from .repository import Repository
from .schemas import EventAccepted, EventIn

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post(
    "/v1/events",
    response_model=EventAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_event(
    event: EventIn,
    project_id: Annotated[str, Depends(get_project_id)],
    repo: Annotated[Repository, Depends(get_repository)],
) -> EventAccepted:
    event_id = await repo.insert_event(project_id, event)
    return EventAccepted(id=event_id)
