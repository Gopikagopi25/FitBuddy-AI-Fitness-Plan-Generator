from functools import lru_cache
from .config import GEMINI_API_KEY

class GeminiNotConfiguredError(RuntimeError):
    pass

@lru_cache(maxsize=1)
def get_client():
    if not GEMINI_API_KEY:
        raise GeminiNotConfiguredError(
            "GEMINI_API_KEY is not configured. Add it to the .env file."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "The Gemini SDK is not installed. Run: pip install -r requirements.txt"
        ) from exc

    return genai.Client(api_key=GEMINI_API_KEY)
