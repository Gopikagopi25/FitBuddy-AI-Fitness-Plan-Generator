from .config import NUTRITION_MODEL
from .gemini_client import get_client
from .schemas import NutritionResponse, UserInput

def generate_nutrition_tip_with_flash(user: UserInput) -> NutritionResponse:
    prompt = f"""
Give one concise, practical nutrition or recovery tip for a fitness user.

Goal: {user.goal}
Age: {user.age}
Weight: {user.weight} kg
Intensity: {user.intensity}

Keep it general wellness guidance, not medical advice.
Avoid calorie prescriptions or unsafe restrictive dieting.
Return one useful tip only.
"""
    client = get_client()
    response = client.models.generate_content(
        model=NUTRITION_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": NutritionResponse,
            "temperature": 0.5,
            "max_output_tokens": 700,
        },
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty nutrition tip.")
    return NutritionResponse.model_validate_json(response.text)
