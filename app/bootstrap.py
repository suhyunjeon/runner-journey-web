from datetime import date

from sqlalchemy import select, text

from app.database import Base, engine
from app.models import RaceModel, RunnerProfileModel
from app.seed.races import SEED_RACES


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_race_columns()


def seed_db(session) -> None:
    has_data = session.scalar(select(RaceModel.slug).limit(1))
    if not has_data:
        for race in SEED_RACES:
            session.add(
                RaceModel(
                    slug=race["slug"],
                    title=race["title"],
                    region=race["region"],
                    venue=race["venue"],
                    event_date=_parse_date(race["event_date"]),
                    registration_status=race["registration_status"],
                    distances="|".join(race["distances"]),
                    thumbnail_url=race["thumbnail_url"],
                    is_bookmarked=race["is_bookmarked"],
                    start_time=race["start_time"],
                    registration_open_at=_parse_date(race["registration_open_at"]),
                    registration_close_at=_parse_date(race["registration_close_at"]),
                    event_status=race["event_status"],
                    official_url=race["official_url"],
                    apply_url=race["apply_url"],
                    contact_email=race["contact_email"],
                    contact_phone=race["contact_phone"],
                    description=race["description"],
                    source_url=race["source_url"],
                    last_checked_at=_parse_date(race["last_checked_at"]),
                )
            )

    has_profile = session.scalar(select(RunnerProfileModel.id).limit(1))
    if not has_profile:
        session.add(
            RunnerProfileModel(
                nickname="Sub-3 도전자",
                home_region="서울",
                experience_level="intermediate",
                target_distance="Half",
                target_event_date=_parse_date("2026-09-20"),
                weekly_run_days=4,
                preferred_surface="road",
                travel_willingness="nationwide",
                notes="가을 시즌에 하프 기록 갱신이 목표예요.",
            )
        )

    session.commit()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _ensure_race_columns() -> None:
    required_columns = {
        "organizer": "ALTER TABLE races ADD COLUMN organizer VARCHAR(255)",
        "entry_fee_note": "ALTER TABLE races ADD COLUMN entry_fee_note VARCHAR(255)",
        "cutoff_note": "ALTER TABLE races ADD COLUMN cutoff_note VARCHAR(255)",
        "course_note": "ALTER TABLE races ADD COLUMN course_note VARCHAR(255)",
    }

    with engine.begin() as connection:
        table_info = connection.execute(text("PRAGMA table_info(races)")).fetchall()
        if not table_info:
            return
        existing = {row[1] for row in table_info}
        for column_name, ddl in required_columns.items():
            if column_name not in existing:
                connection.execute(text(ddl))
