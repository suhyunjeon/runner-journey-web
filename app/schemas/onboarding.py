from pydantic import BaseModel


class OnboardingStatus(BaseModel):
    has_profile: bool
    completed: bool
    next_step: str
