from app.repositories.profile_repository import ProfileRepository
from app.schemas.onboarding import OnboardingStatus
from app.schemas.profile import RunnerProfile, RunnerProfileUpdate


class ProfileService:
    def __init__(self, repository: ProfileRepository) -> None:
        self.repository = repository

    def get_primary_profile(self) -> RunnerProfile | None:
        return self.repository.get_primary_profile()

    def upsert_primary_profile(self, payload: RunnerProfileUpdate) -> RunnerProfile:
        return self.repository.upsert_primary_profile(payload)

    def get_onboarding_status(self) -> OnboardingStatus:
        profile = self.repository.get_primary_profile()
        if profile is None:
            return OnboardingStatus(has_profile=False, completed=False, next_step="create_profile")
        return OnboardingStatus(has_profile=True, completed=True, next_step="view_recommendations")
