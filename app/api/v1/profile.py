from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_profile_service
from app.schemas.profile import RunnerProfile, RunnerProfileUpdate
from app.services.profile_service import ProfileService


router = APIRouter()


@router.get("/me", response_model=RunnerProfile)
def get_my_profile(
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> RunnerProfile:
    profile = service.get_primary_profile()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/me", response_model=RunnerProfile)
def update_my_profile(
    payload: RunnerProfileUpdate,
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> RunnerProfile:
    return service.upsert_primary_profile(payload)
