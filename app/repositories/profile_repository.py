from abc import ABC, abstractmethod

from app.schemas.profile import RunnerProfile, RunnerProfileUpdate


class ProfileRepository(ABC):
    @abstractmethod
    def get_primary_profile(self) -> RunnerProfile | None:
        raise NotImplementedError

    @abstractmethod
    def upsert_primary_profile(self, payload: RunnerProfileUpdate) -> RunnerProfile:
        raise NotImplementedError
