import json
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models import RecommendationHistory, User
from ..schemas import HomeRequest, PartyRequest, JewelryRequest
from ..services.planner_service import generate_home, generate_party, generate_jewelry

router = APIRouter()


def save_history(db: Session, user: User, planner: str, budget: float, request_data: dict, response_data: dict):
    row = RecommendationHistory(
        user_id=user.id,
        planner_type=planner,
        budget=budget,
        request_json=json.dumps(request_data),
        response_json=json.dumps(response_data),
    )
    db.add(row)
    db.commit()


@router.post("/api/generate-home")
async def generate_home_route(payload: HomeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = await generate_home(payload)
    save_history(db, user, "home", payload.budget, payload.model_dump(), result)
    return result


@router.post("/api/generate-party")
async def generate_party_route(payload: PartyRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = await generate_party(payload)
    save_history(db, user, "party", payload.budget, payload.model_dump(), result)
    return result


@router.post("/api/generate-jewelry")
async def generate_jewelry_route(
    budget: float,
    occasion: str,
    style: str = "elegant",
    outfit_color: str | None = None,
    preferences: str = "",
    outfit_image: UploadFile | None = File(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if budget <= 0:
        raise HTTPException(status_code=422, detail="Budget must be greater than zero.")
    image_bytes = None
    mime = "image/jpeg"
    if outfit_image:
        allowed = {"image/jpeg", "image/png", "image/webp"}
        if outfit_image.content_type not in allowed:
            raise HTTPException(status_code=400, detail="Upload a JPG, PNG or WEBP image.")
        image_bytes = await outfit_image.read()
        if len(image_bytes) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image must be 5 MB or smaller.")
        mime = outfit_image.content_type

    payload = JewelryRequest(
        budget=budget,
        occasion=occasion,
        style=style,
        outfit_color=outfit_color,
        preferences=preferences,
    )
    result = await generate_jewelry(payload, image_bytes, mime)
    save_history(db, user, "jewelry", budget, payload.model_dump(), result)
    return result


@router.get("/api/history")
def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.user_id == user.id)
        .order_by(RecommendationHistory.created_at.desc())
        .limit(50)
        .all()
    )
    return {
        "items": [
            {
                "id": x.id,
                "planner_type": x.planner_type,
                "budget": x.budget,
                "created_at": x.created_at.isoformat(),
                "request": json.loads(x.request_json),
                "response": json.loads(x.response_json),
            }
            for x in rows
        ]
    }
