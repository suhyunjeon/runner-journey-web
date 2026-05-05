from datetime import date

from pydantic import BaseModel


class RunnerProfile(BaseModel):
    id: int
    nickname: str
    home_region: str
    experience_level: str
    target_distance: str
    target_event_date: date
    weekly_run_days: int
    preferred_surface: str
    travel_willingness: str
    notes: str = ""


class RunnerProfileUpdate(BaseModel):
    nickname: str
    home_region: str
    experience_level: str
    target_distance: str
    target_event_date: date
    weekly_run_days: int
    preferred_surface: str
    travel_willingness: str
    notes: str = ""
