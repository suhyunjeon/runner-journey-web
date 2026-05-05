from fastapi import APIRouter

from app.api.v1.onboarding import router as onboarding_router
from app.api.v1.profile import router as profile_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.races import router as races_router


api_router = APIRouter()
api_router.include_router(races_router, prefix="/races", tags=["races"])
api_router.include_router(profile_router, prefix="/profiles", tags=["profiles"])
api_router.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(onboarding_router, prefix="/onboarding", tags=["onboarding"])
