from sqlalchemy.orm import Session

from app.collectors.base import BaseCollector
from app.enrichers.official_page import OfficialPageEnricher
from app.models import RaceModel
from app.schemas.race import RaceDetail


class SyncService:
    def __init__(self, session: Session, enricher: OfficialPageEnricher | None = None) -> None:
        self.session = session
        self.enricher = enricher or OfficialPageEnricher()

    def sync_races(self, collector: BaseCollector, limit: int | None = None) -> dict[str, int]:
        races = collector.collect(limit=limit)
        created = 0
        updated = 0
        enriched = 0

        for race in races:
            race = self.enricher.enrich(race)
            enriched += 1
            existing = self.session.get(RaceModel, race.slug)
            if existing is None:
                self.session.add(self._to_model(race))
                created += 1
                continue

            self._update_model(existing, race)
            updated += 1

        self.session.commit()
        return {"fetched": len(races), "enriched": enriched, "created": created, "updated": updated}

    def _to_model(self, race: RaceDetail) -> RaceModel:
        return RaceModel(
            slug=race.slug,
            title=race.title,
            region=race.region,
            venue=race.venue,
            event_date=race.event_date,
            registration_status=race.registration_status,
            distances="|".join(race.distances),
            thumbnail_url=str(race.thumbnail_url) if race.thumbnail_url else None,
            is_bookmarked=race.is_bookmarked,
            start_time=race.start_time,
            registration_open_at=race.registration_open_at,
            registration_close_at=race.registration_close_at,
            event_status=race.event_status,
            official_url=str(race.official_url) if race.official_url else None,
            apply_url=str(race.apply_url) if race.apply_url else None,
            contact_email=race.contact_email,
            contact_phone=race.contact_phone,
            organizer=race.organizer,
            entry_fee_note=race.entry_fee_note,
            cutoff_note=race.cutoff_note,
            course_note=race.course_note,
            description=race.description,
            source_url=str(race.source_url) if race.source_url else None,
            last_checked_at=race.last_checked_at,
        )

    def _update_model(self, model: RaceModel, race: RaceDetail) -> None:
        model.title = race.title
        model.region = race.region
        model.venue = race.venue
        model.event_date = race.event_date
        model.registration_status = race.registration_status
        model.distances = "|".join(race.distances)
        model.thumbnail_url = str(race.thumbnail_url) if race.thumbnail_url else None
        model.start_time = race.start_time
        model.registration_open_at = race.registration_open_at
        model.registration_close_at = race.registration_close_at
        model.event_status = race.event_status
        model.official_url = str(race.official_url) if race.official_url else None
        model.apply_url = str(race.apply_url) if race.apply_url else None
        model.contact_email = race.contact_email
        model.contact_phone = race.contact_phone
        model.organizer = race.organizer
        model.entry_fee_note = race.entry_fee_note
        model.cutoff_note = race.cutoff_note
        model.course_note = race.course_note
        model.description = race.description
        model.source_url = str(race.source_url) if race.source_url else None
        model.last_checked_at = race.last_checked_at
