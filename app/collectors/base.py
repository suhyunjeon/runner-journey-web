from abc import ABC, abstractmethod

from app.schemas.race import RaceDetail


class BaseCollector(ABC):
    source_name: str

    @abstractmethod
    def collect(self, limit: int | None = None) -> list[RaceDetail]:
        raise NotImplementedError
