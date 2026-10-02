from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .models import User, WorkoutPlan
from .plan_utils import plan_from_text, plan_to_text
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def render_error(request: Request, message: str, status_code: int = 400):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"message": message},
        status_code=status_code,
    )

def get_user_or_404(db: Session, user_id: str) -> User:
    user = db.scalar(select(User).where(User.user_id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        existing = db.scalar(select(User).where(User.user_id == data.user_id))
        if existing:
            user = existing
            user.username = data.username
            user.age = data.age
            user.weight = data.weight
            user.goal = data.goal
            user.intensity = data.intensity
        else:
            user = User(
                user_id=data.user_id,
                username=data.username,
                age=data.age,
                weight=data.weight,
                goal=data.goal,
                intensity=data.intensity,
            )
            db.add(user)
            db.flush()

        workout = generate_workout_gemini(data)
        nutrition = generate_nutrition_tip_with_flash(data)

        if user.plan:
            user.plan.original_plan = plan_to_text(workout)
            user.plan.updated_plan = None
            user.plan.feedback = None
            user.plan.nutrition_tip = nutrition.tip
            user.plan.updated_at = datetime.now(timezone.utc)
        else:
            db.add(
                WorkoutPlan(
                    user_id=user.id,
                    original_plan=plan_to_text(workout),
                    nutrition_tip=nutrition.tip,
                )
            )

        db.commit()
        db.refresh(user)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": workout,
                "nutrition_tip": nutrition.tip,
                "feedback_message": None,
            },
        )
    except ValueError as exc:
        db.rollback()
        return render_error(request, str(exc), 422)
    except Exception as exc:
        db.rollback()
        return render_error(request, f"Could not generate the plan: {exc}", 500)

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = get_user_or_404(db, data.user_id)
        if not user.plan:
            return render_error(request, "No workout plan exists for this user.", 404)

        updated = update_workout_plan(user.plan.original_plan, data.feedback)
        user.plan.updated_plan = plan_to_text(updated)
        user.plan.feedback = data.feedback
        user.plan.updated_at = datetime.now(timezone.utc)
        db.commit()

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": updated,
                "nutrition_tip": user.plan.nutrition_tip,
                "feedback_message": "Your plan was updated using your feedback.",
            },
        )
    except ValueError as exc:
        db.rollback()
        return render_error(request, str(exc), 422)
    except Exception as exc:
        db.rollback()
        return render_error(request, f"Could not update the plan: {exc}", 500)

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users},
    )

@router.post("/delete-user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = get_user_or_404(db, user_id)
    db.delete(user)
    db.commit()
    return RedirectResponse(url="/view-all-users", status_code=303)

@router.get("/health")
def health():
    return {"status": "ok", "service": "FitBuddy"}

@router.post("/api/generate")
def api_generate(payload: UserInput, db: Session = Depends(get_db)):
    try:
        workout = generate_workout_gemini(payload)
        nutrition = generate_nutrition_tip_with_flash(payload)

        user = db.scalar(select(User).where(User.user_id == payload.user_id))
        if not user:
            user = User(
                user_id=payload.user_id,
                username=payload.username,
                age=payload.age,
                weight=payload.weight,
                goal=payload.goal,
                intensity=payload.intensity,
            )
            db.add(user)
            db.flush()
        else:
            user.username = payload.username
            user.age = payload.age
            user.weight = payload.weight
            user.goal = payload.goal
            user.intensity = payload.intensity

        if user.plan:
            user.plan.original_plan = plan_to_text(workout)
            user.plan.updated_plan = None
            user.plan.feedback = None
            user.plan.nutrition_tip = nutrition.tip
        else:
            db.add(
                WorkoutPlan(
                    user_id=user.id,
                    original_plan=plan_to_text(workout),
                    nutrition_tip=nutrition.tip,
                )
            )
        db.commit()
        return {"user": payload.model_dump(), "workout_plan": workout.model_dump(), "nutrition_tip": nutrition.tip}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/api/feedback")
def api_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    try:
        user = get_user_or_404(db, payload.user_id)
        if not user.plan:
            raise HTTPException(status_code=404, detail="No workout plan exists for this user.")
        updated = update_workout_plan(user.plan.original_plan, payload.feedback)
        user.plan.updated_plan = plan_to_text(updated)
        user.plan.feedback = payload.feedback
        user.plan.updated_at = datetime.now(timezone.utc)
        db.commit()
        return {"user_id": payload.user_id, "updated_plan": updated.model_dump(), "feedback": payload.feedback}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/api/users")
def api_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [
        {
            "id": user.id,
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "created_at": user.created_at.isoformat(),
            "has_updated_plan": bool(user.plan and user.plan.updated_plan),
        }
        for user in users
    ]

@router.get("/api/users/{user_id}")
def api_user(user_id: str, db: Session = Depends(get_db)):
    user = get_user_or_404(db, user_id)
    plan = user.plan
    original = plan_from_text(plan.original_plan).model_dump() if plan else None
    updated = plan_from_text(plan.updated_plan).model_dump() if plan and plan.updated_plan else None
    return {
        "user": {
            "id": user.id,
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
        },
        "plan": {
            "original": original,
            "updated": updated,
            "nutrition_tip": plan.nutrition_tip if plan else None,
            "feedback": plan.feedback if plan else None,
        } if plan else None,
    }
