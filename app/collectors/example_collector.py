from app.collectors.base import BaseCollector
from app.schemas.race import RaceDetail
from app.seed.races import SEED_RACES


class ExampleCollector(BaseCollector):
    source_name = "example"

    def collect(self) -> list[RaceDetail]:
        return [RaceDetail(**race) for race in SEED_RACES]
