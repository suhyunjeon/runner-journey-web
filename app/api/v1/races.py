from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_race_service
from app.schemas.race import RaceBookmarkUpdate, RaceDetail, RaceListItem, RaceSearchParams
from app.services.race_service import RaceService


router = APIRouter()


@router.get("", response_model=list[RaceListItem])
def list_races(
    service: Annotated[RaceService, Depends(get_race_service)],
    region: str | None = Query(default=None),
    status: str | None = Query(default=None),
    distance: str | None = Query(default=None),
    month: int | None = Query(default=None, ge=1, le=12),
    q: str | None = Query(default=None),
    bookmarked_only: bool = Query(default=False),
) -> list[RaceListItem]:
    params = RaceSearchParams(
        region=region,
        status=status,
        distance=distance,
        month=month,
        q=q,
        bookmarked_only=bookmarked_only,
    )
    return service.list_races(params)


@router.get("/{slug}", response_model=RaceDetail)
def get_race(
    slug: str,
    service: Annotated[RaceService, Depends(get_race_service)],
) -> RaceDetail:
    race = service.get_race(slug)
    if race is None:
        raise HTTPException(status_code=404, detail="Race not found")
    return race


@router.put("/{slug}/bookmark", response_model=RaceDetail)
def set_race_bookmark(
    slug: str,
    payload: RaceBookmarkUpdate,
    service: Annotated[RaceService, Depends(get_race_service)],
) -> RaceDetail:
    race = service.set_bookmark(slug, payload.is_bookmarked)
    if race is None:
        raise HTTPException(status_code=404, detail="Race not found")
    return race
