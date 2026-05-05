from app.repositories.race_repository import RaceRepository
from app.schemas.race import RaceDetail, RaceSearchParams
from app.seed.races import SEED_RACES


class InMemoryRaceRepository(RaceRepository):
    def __init__(self) -> None:
        self._races = [RaceDetail(**race) for race in SEED_RACES]

    def list_races(self, params: RaceSearchParams) -> list[RaceDetail]:
        races = self._races

        if params.region:
            races = [race for race in races if race.region == params.region]

        if params.status:
            races = [race for race in races if race.registration_status == params.status]

        if params.distance:
            races = [race for race in races if params.distance in race.distances]

        if params.month:
            races = [race for race in races if race.event_date.month == params.month]

        if params.q:
            keyword = params.q.casefold()
            races = [
                race
                for race in races
                if keyword in race.title.casefold()
                or keyword in race.venue.casefold()
                or keyword in race.description.casefold()
            ]

        if params.bookmarked_only:
            races = [race for race in races if race.is_bookmarked]

        return sorted(races, key=lambda race: race.event_date)

    def get_race(self, slug: str) -> RaceDetail | None:
        for race in self._races:
            if race.slug == slug:
                return race
        return None

    def set_bookmark(self, slug: str, is_bookmarked: bool) -> RaceDetail | None:
        for race in self._races:
            if race.slug == slug:
                race.is_bookmarked = is_bookmarked
                return race
        return None
