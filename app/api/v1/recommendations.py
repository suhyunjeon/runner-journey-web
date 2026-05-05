from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_recommendation_service
from app.schemas.recommendation import (
    RecommendationDetailResponse,
    RecommendationHomeResponse,
    RecommendationResponse,
)
from app.services.recommendation_service import RecommendationService


router = APIRouter()


@router.get("/me", response_model=RecommendationResponse)
def get_my_recommendations(
    service: Annotated[RecommendationService, Depends(get_recommendation_service)],
) -> RecommendationResponse:
    result = service.get_home_feed()
    if result is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result


@router.get("/me/home", response_model=RecommendationHomeResponse)
def get_my_recommendation_home(
    service: Annotated[RecommendationService, Depends(get_recommendation_service)],
) -> RecommendationHomeResponse:
    result = service.get_mobile_home()
    if result is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result


@router.get("/me/{slug}", response_model=RecommendationDetailResponse)
def get_recommendation_detail(
    slug: str,
    service: Annotated[RecommendationService, Depends(get_recommendation_service)],
) -> RecommendationDetailResponse:
    result = service.get_recommendation_detail(slug)
    if result is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return result
