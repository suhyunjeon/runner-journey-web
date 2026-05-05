from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_profile_service
from app.schemas.onboarding import OnboardingStatus
from app.services.profile_service import ProfileService


router = APIRouter()


@router.get("/status", response_model=OnboardingStatus)
def get_onboarding_status(
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> OnboardingStatus:
    return service.get_onboarding_status()
