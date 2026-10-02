from typing import Literal
from pydantic import BaseModel, Field, field_validator

Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]

class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=120)
    user_id: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=300)
    goal: Goal
    intensity: Intensity

    @field_validator("username", "user_id")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value

class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=80)
    feedback: str = Field(min_length=3, max_length=1500)

class DayPlan(BaseModel):
    day: str
    focus: str
    warm_up: str
    main_workout: list[str]
    cooldown: str
    recovery_tip: str

class WorkoutPlanResponse(BaseModel):
    days: list[DayPlan] = Field(min_length=7, max_length=7)

class NutritionResponse(BaseModel):
    tip: str = Field(min_length=10, max_length=1000)