from pydantic import BaseModel

from app.schemas.profile import RunnerProfile
from app.schemas.race import RaceListItem


class RaceRecommendation(BaseModel):
    race: RaceListItem
    score: int
    confidence: str
    difficulty_level: str
    surface_hint: str
    course_style: str
    seasonal_tag: str
    weather_risk: str
    cost_band: str
    cost_display: str
    cutoff_pressure: str
    recommendation_reason: str
    training_weeks_left: int
    fit_labels: list[str]
    score_breakdown: dict[str, int]


class RecommendationResponse(BaseModel):
    profile: RunnerProfile
    recommendations: list[RaceRecommendation]


class HomeInsight(BaseModel):
    title: str
    body: str
    tone: str


class TrainingStep(BaseModel):
    title: str
    subtitle: str
    is_current: bool


class HomeQuickStats(BaseModel):
    target_distance: str
    days_until_goal: int
    open_races_count: int
    local_match_count: int


class RecommendationHomeResponse(BaseModel):
    profile: RunnerProfile
    hero_recommendation: RaceRecommendation | None
    quick_stats: HomeQuickStats
    next_actions: list[str]
    insights: list[HomeInsight]
    training_timeline: list[TrainingStep]
    nearby_open_races: list[RaceRecommendation]
    long_term_matches: list[RaceRecommendation]


class RecommendationDetailResponse(BaseModel):
    recommendation: RaceRecommendation
    why_now: list[str]
    caution_notes: list[str]
    training_focus: list[str]
    action_checklist: list[str]
