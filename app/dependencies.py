from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.repositories.sqlalchemy_profile_repository import SqlAlchemyProfileRepository
from app.repositories.sqlalchemy_race_repository import SqlAlchemyRaceRepository
from app.services.profile_service import ProfileService
from app.services.recommendation_service import RecommendationService
from app.services.race_service import RaceService


def get_race_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> RaceService:
    return RaceService(repository=SqlAlchemyRaceRepository(session=session))


def get_profile_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> ProfileService:
    return ProfileService(repository=SqlAlchemyProfileRepository(session=session))


def get_recommendation_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> RecommendationService:
    race_service = RaceService(repository=SqlAlchemyRaceRepository(session=session))
    profile_service = ProfileService(repository=SqlAlchemyProfileRepository(session=session))
    return RecommendationService(race_service=race_service, profile_service=profile_service)
