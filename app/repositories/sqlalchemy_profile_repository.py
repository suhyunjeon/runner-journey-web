from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RunnerProfileModel
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import RunnerProfile, RunnerProfileUpdate


class SqlAlchemyProfileRepository(ProfileRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_primary_profile(self) -> RunnerProfile | None:
        profile = self.session.scalar(select(RunnerProfileModel).order_by(RunnerProfileModel.id.asc()).limit(1))
        if profile is None:
            return None
        return self._to_schema(profile)

    def upsert_primary_profile(self, payload: RunnerProfileUpdate) -> RunnerProfile:
        profile = self.session.scalar(select(RunnerProfileModel).order_by(RunnerProfileModel.id.asc()).limit(1))
        if profile is None:
            profile = RunnerProfileModel(**payload.model_dump())
            self.session.add(profile)
            self.session.commit()
            self.session.refresh(profile)
            return self._to_schema(profile)

        for field, value in payload.model_dump().items():
            setattr(profile, field, value)
        self.session.commit()
        self.session.refresh(profile)
        return self._to_schema(profile)

    def _to_schema(self, model: RunnerProfileModel) -> RunnerProfile:
        return RunnerProfile(
            id=model.id,
            nickname=model.nickname,
            home_region=model.home_region,
            experience_level=model.experience_level,
            target_distance=model.target_distance,
            target_event_date=model.target_event_date,
            weekly_run_days=model.weekly_run_days,
            preferred_surface=model.preferred_surface,
            travel_willingness=model.travel_willingness,
            notes=model.notes,
        )
