from datetime import date

from sqlalchemy import Boolean, Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RaceModel(Base):
    __tablename__ = "races"

    slug: Mapped[str] = mapped_column(String(120), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    venue: Mapped[str] = mapped_column(String(200), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    registration_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    distances: Mapped[str] = mapped_column(String(120), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    start_time: Mapped[str | None] = mapped_column(String(20), nullable=True)
    registration_open_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    registration_close_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    event_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    official_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    apply_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    organizer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    entry_fee_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cutoff_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    course_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_checked_at: Mapped[date | None] = mapped_column(Date, nullable=True)


class RunnerProfileModel(Base):
    __tablename__ = "runner_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(80), nullable=False)
    home_region: Mapped[str] = mapped_column(String(40), nullable=False)
    experience_level: Mapped[str] = mapped_column(String(20), nullable=False)
    target_distance: Mapped[str] = mapped_column(String(20), nullable=False)
    target_event_date: Mapped[date] = mapped_column(Date, nullable=False)
    weekly_run_days: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    preferred_surface: Mapped[str] = mapped_column(String(20), nullable=False, default="road")
    travel_willingness: Mapped[str] = mapped_column(String(20), nullable=False, default="regional")
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
