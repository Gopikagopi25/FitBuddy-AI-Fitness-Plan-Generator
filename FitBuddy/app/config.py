import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "FitBuddy"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitbuddy.db")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
WORKOUT_MODEL = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-3.8-flash")
NUTRITION_MODEL = os.getenv("GEMINI_NUTRITION_MODEL", "gemini-3.8-flash")
GEMINI_TIMEOUT_SECONDS = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "60"))
