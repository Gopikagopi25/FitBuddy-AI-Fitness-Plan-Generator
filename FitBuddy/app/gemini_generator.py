from .config import WORKOUT_MODEL
from .gemini_client import get_client
from .schemas import UserInput, WorkoutPlanResponse

SYSTEM_INSTRUCTION = """
You are FitBuddy, a fitness plan assistant.

Create a simple beginner-friendly 7-day workout plan.
Do not diagnose medical conditions or prescribe treatment.

Return ONLY valid JSON.
"""

def generate_workout_gemini(user: UserInput) -> WorkoutPlanResponse:

    prompt = f"""
Create a personalized 7-day workout plan for this user.

Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}

Return JSON in exactly this format:

{{
  "days": [
    {{
      "day": "Day 1",
      "focus": "Full Body",
      "warm_up": "5 minutes",
      "main_workout": [
        "Squats - 3 sets of 10",
        "Push-ups - 3 sets of 8",
        "Walking - 10 minutes"
      ],
      "cooldown": "5 minutes stretching",
      "recovery_tip": "Drink enough water and rest."
    }}
  ]
}}

Create exactly 7 days.
Use simple exercises.
Include rest or recovery days.
"""

    client = get_client()

    response = client.models.generate_content(
        model=WORKOUT_MODEL,
        contents=prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.5,
            "max_output_tokens": 3000,
        },
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty workout plan.")

    import json

    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned an invalid JSON workout plan."
        ) from exc

    return WorkoutPlanResponse.model_validate(data)