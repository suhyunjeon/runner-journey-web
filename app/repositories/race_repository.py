from abc import ABC, abstractmethod

from app.schemas.race import RaceDetail, RaceSearchParams


class RaceRepository(ABC):
    @abstractmethod
    def list_races(self, params: RaceSearchParams) -> list[RaceDetail]:
        raise NotImplementedError

    @abstractmethod
    def get_race(self, slug: str) -> RaceDetail | None:
        raise NotImplementedError

    @abstractmethod
    def set_bookmark(self, slug: str, is_bookmarked: bool) -> RaceDetail | None:
        raise NotImplementedError
