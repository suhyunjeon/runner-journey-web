from sqlalchemy import Select, extract, select
from sqlalchemy.orm import Session

from app.models import RaceModel
from app.repositories.race_repository import RaceRepository
from app.schemas.race import RaceDetail, RaceSearchParams


class SqlAlchemyRaceRepository(RaceRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_races(self, params: RaceSearchParams) -> list[RaceDetail]:
        query = select(RaceModel)
        query = self._apply_filters(query, params)
        query = query.order_by(RaceModel.event_date.asc())
        races = self.session.scalars(query).all()
        return [self._to_schema(race) for race in races]

    def get_race(self, slug: str) -> RaceDetail | None:
        race = self.session.get(RaceModel, slug)
        if race is None:
            return None
        return self._to_schema(race)

    def set_bookmark(self, slug: str, is_bookmarked: bool) -> RaceDetail | None:
        race = self.session.get(RaceModel, slug)
        if race is None:
            return None
        race.is_bookmarked = is_bookmarked
        self.session.commit()
        self.session.refresh(race)
        return self._to_schema(race)

    def _apply_filters(self, query: Select[tuple[RaceModel]], params: RaceSearchParams) -> Select[tuple[RaceModel]]:
        if params.region:
            query = query.where(RaceModel.region == params.region)

        if params.status:
            query = query.where(RaceModel.registration_status == params.status)

        if params.distance:
            query = query.where(RaceModel.distances.like(f"%{params.distance}%"))

        if params.month:
            query = query.where(extract("month", RaceModel.event_date) == params.month)

        if params.q:
            keyword = f"%{params.q}%"
            query = query.where(
                RaceModel.title.ilike(keyword)
                | RaceModel.venue.ilike(keyword)
                | RaceModel.description.ilike(keyword)
            )

        if params.bookmarked_only:
            query = query.where(RaceModel.is_bookmarked.is_(True))

        return query

    def _to_schema(self, race: RaceModel) -> RaceDetail:
        return RaceDetail(
            slug=race.slug,
            title=race.title,
            region=race.region,
            venue=race.venue,
            event_date=race.event_date,
            registration_status=race.registration_status,
            distances=race.distances.split("|") if race.distances else [],
            thumbnail_url=race.thumbnail_url,
            is_bookmarked=race.is_bookmarked,
            start_time=race.start_time,
            registration_open_at=race.registration_open_at,
            registration_close_at=race.registration_close_at,
            event_status=race.event_status,
            official_url=race.official_url,
            apply_url=race.apply_url,
            contact_email=race.contact_email,
            contact_phone=race.contact_phone,
            organizer=race.organizer,
            entry_fee_note=race.entry_fee_note,
            cutoff_note=race.cutoff_note,
            course_note=race.course_note,
            description=race.description,
            source_url=race.source_url,
            last_checked_at=race.last_checked_at,
        )
