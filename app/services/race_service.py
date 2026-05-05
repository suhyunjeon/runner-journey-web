from app.repositories.race_repository import RaceRepository
from app.schemas.race import RaceDetail, RaceListItem, RaceSearchParams


class RaceService:
    def __init__(self, repository: RaceRepository) -> None:
        self.repository = repository

    def list_races(self, params: RaceSearchParams) -> list[RaceListItem]:
        races = self.repository.list_races(params)
        return [RaceListItem.model_validate(race.model_dump()) for race in races]

    def get_race(self, slug: str) -> RaceDetail | None:
        return self.repository.get_race(slug)

    def set_bookmark(self, slug: str, is_bookmarked: bool) -> RaceDetail | None:
        return self.repository.set_bookmark(slug, is_bookmarked)
