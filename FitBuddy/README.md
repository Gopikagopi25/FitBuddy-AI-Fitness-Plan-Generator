# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI web application based on the supplied project documentation. It accepts a user's name, ID, age, weight, fitness goal, and workout intensity, then uses Gemini to generate a structured 7-day workout plan and a nutrition/recovery tip. Users can submit feedback to regenerate the plan, and a local admin page shows stored users and plans.

The original document describes Gemini 1.5 Pro and Gemini Flash. Those model IDs are not used here because the current Gemini API has moved to the Google GenAI SDK and newer model families. The code therefore uses configurable current model IDs. Change them in `.env` if your Google AI account exposes a different model.

## Features

- FastAPI backend
- Jinja2 HTML frontend
- SQLite + SQLAlchemy persistence
- Gemini structured JSON output
- 7-day workout generation
- Nutrition/recovery tip generation
- Feedback-based plan regeneration
- Admin dashboard
- JSON API endpoints
- FastAPI Swagger docs
- Input validation and friendly error page
- Automated smoke tests

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── gemini_client.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   ├── plan_utils.py
│   └── routes.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── all_users.html
│   └── error.html
├── static/
│   └── css/
│       └── style.css
├── tests/
│   └── test_app.py
├── data/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## VS Code setup – Windows

### 1. Open the project

Open the `FitBuddy` folder in VS Code.

### 2. Create a virtual environment

Open the VS Code terminal:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Gemini

Copy `.env.example` to `.env`.

PowerShell:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace:

```text
GEMINI_API_KEY=your_api_key_here
```

with your real Gemini API key.

Do not commit `.env` to Git.

### 5. Start the application

From the project root:

```powershell
uvicorn app.main:app --reload
```

Open:

- Website: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs
- Admin dashboard: http://127.0.0.1:8000/view-all-users
- Health check: http://127.0.0.1:8000/health

## Testing without Gemini

The basic smoke tests do not call Gemini:

```powershell
pytest -q
```

They verify that the application starts, the homepage loads, and the health/users API routes respond.

## Testing the complete AI flow

1. Open http://127.0.0.1:8000
2. Enter:
   - Name: Priya
   - User ID: FB001
   - Age: 20
   - Weight: 55
   - Goal: General wellness
   - Intensity: Medium
3. Click **Generate 7-Day Plan**.
4. Wait for Gemini to return the structured plan.
5. Check the seven day cards and nutrition tip.
6. Enter feedback such as:
   `Add more cardio and keep one extra rest day.`
7. Click **Update Plan with AI**.
8. Open **Admin Dashboard** and verify the stored user and updated plan.

## API examples

### Generate

POST `/api/generate`

```json
{
  "username": "Priya",
  "user_id": "FB001",
  "age": 20,
  "weight": 55,
  "goal": "general wellness",
  "intensity": "medium"
}
```

### Feedback

POST `/api/feedback`

```json
{
  "user_id": "FB001",
  "feedback": "Add more cardio and one extra rest day."
}
```

### List users

GET `/api/users`

### Get one user

GET `/api/users/FB001`

## Database

SQLite is created automatically as `fitbuddy.db` in the project root on first startup.

Tables:

- `users`
- `workout_plans`

A user's original plan is kept separately from the feedback-generated updated plan.

## Important production note

The supplied project documentation describes an admin page but does not specify authentication. This implementation therefore keeps `/view-all-users` as a local/demo dashboard. Before deploying publicly, add authentication/authorization, HTTPS, rate limiting, secret management, audit logging, and a production database.

The application provides general fitness/wellness guidance and is not a substitute for individualized medical or exercise-professional advice.
