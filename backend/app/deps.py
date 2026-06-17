from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status

from .repository import Repository

# Set by main.py at startup. Tests override get_repository instead.
_repository: Optional[Repository] = None


def set_repository(repo: Repository) -> None:
    global _repository
    _repository = repo


def get_repository() -> Repository:
    if _repository is None:
        raise RuntimeError("Repository not configured")
    return _repository


async def get_project_id(
    repo: Annotated[Repository, Depends(get_repository)],
    authorization: Annotated[Optional[str], Header()] = None,
) -> str:
    """Resolve the caller's project from the Bearer token (PRD §5)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )
    api_key = authorization.removeprefix("Bearer ").strip()
    project_id = await repo.resolve_project(api_key)
    if project_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    return project_id
