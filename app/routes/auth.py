from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import create_access_token, hash_password, verify_password
from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import LoginRequest, RegisterRequest

router = APIRouter()


@router.post("/api/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        return {"ok": False, "message": "An account with that email already exists."}
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True, "message": "Registration successful."}


@router.post("/api/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        return {"ok": False, "message": "Invalid email or password."}
    token = create_access_token(user.id)
    response = {"ok": True, "message": "Login successful."}
    return LoginResponse(response, token)


class LoginResponse(dict):
    def __init__(self, response: dict, token: str):
        super().__init__(response)
        self["token"] = token


@router.post("/api/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/api/session-info")
def session_info(user: User = Depends(get_current_user)):
    return {"logged_in": True, "user_id": user.id, "email": user.email}
