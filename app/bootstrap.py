from datetime import date

from sqlalchemy import inspect, select, text

from app.config import settings
from app.database import Base, engine
from app.models import RaceModel, RunnerProfileModel
from app.seed.races import SEED_RACES


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_race_columns()


def seed_db(session) -> None:
    if not _use_seed_races():
        session.query(RaceModel).filter(RaceModel.slug.in_(_seed_race_slugs())).delete(
            synchronize_session=False
        )
        session.commit()

    has_data = session.scalar(select(RaceModel.slug).limit(1))
    if not has_data and _use_seed_races():
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

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "races" not in table_names:
        return

    with engine.begin() as connection:
        race_columns = {column["name"] for column in inspector.get_columns("races")}
        for column_name, ddl in required_columns.items():
            if column_name not in race_columns and engine.dialect.name == "sqlite":
                connection.execute(text(ddl))

        if engine.dialect.name == "postgresql":
            connection.execute(text("ALTER TABLE races ALTER COLUMN start_time TYPE VARCHAR(80)"))
            if "runner_profiles" in table_names:
                connection.execute(
                    text("ALTER TABLE runner_profiles ALTER COLUMN target_distance TYPE VARCHAR(40)")
                )


def _use_seed_races() -> bool:
    return settings.database_url.startswith("sqlite")


def _seed_race_slugs() -> list[str]:
    return [race["slug"] for race in SEED_RACES]
