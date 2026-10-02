import json
from .schemas import WorkoutPlanResponse

def plan_to_text(plan: WorkoutPlanResponse) -> str:
    return json.dumps(plan.model_dump(), indent=2, ensure_ascii=False)

def plan_from_text(value: str) -> WorkoutPlanResponse:
    return WorkoutPlanResponse.model_validate_json(value)
