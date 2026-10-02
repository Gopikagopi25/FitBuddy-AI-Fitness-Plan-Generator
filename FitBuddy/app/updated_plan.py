from .config import WORKOUT_MODEL
from .gemini_client import get_client
from .schemas import WorkoutPlanResponse

def update_workout_plan(original_plan: str, feedback: str) -> WorkoutPlanResponse:
    prompt = f"""
Update the existing FitBuddy workout plan using the user's feedback.

Original plan:
{original_plan}

User feedback:
{feedback}

Rules:
- Keep exactly 7 days.
- Apply the feedback where it is reasonable.
- Preserve a safe balance of activity and recovery.
- Do not provide medical diagnosis or treatment.
- Return the complete revised plan, not only the changed days.
"""
    client = get_client()
    response = client.models.generate_content(
        model=WORKOUT_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": WorkoutPlanResponse,
            "temperature": 0.7,
            "max_output_tokens": 6000,
        },
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty updated plan.")
    return WorkoutPlanResponse.model_validate_json(response.text)
