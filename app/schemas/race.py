from datetime import date

from pydantic import BaseModel, Field, HttpUrl


class RaceSearchParams(BaseModel):
    region: str | None = None
    status: str | None = None
    distance: str | None = None
    month: int | None = None
    q: str | None = None
    bookmarked_only: bool = False


class RaceListItem(BaseModel):
    slug: str
    title: str
    region: str
    venue: str
    event_date: date
    registration_status: str
    distances: list[str]
    thumbnail_url: HttpUrl | None = None
    is_bookmarked: bool = False


class RaceDetail(RaceListItem):
    start_time: str | None = None
    registration_open_at: date | None = None
    registration_close_at: date | None = None
    event_status: str
    official_url: HttpUrl | None = None
    apply_url: HttpUrl | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    organizer: str | None = None
    entry_fee_note: str | None = None
    cutoff_note: str | None = None
    course_note: str | None = None
    description: str = Field(default="")
    source_url: HttpUrl | None = None
    last_checked_at: date | None = None


class RaceBookmarkUpdate(BaseModel):
    is_bookmarked: bool
