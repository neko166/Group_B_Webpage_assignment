from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@router.get("/login", response_class=HTMLResponse, tags=["auth"])
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse, tags=["auth"])
def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or user.password != password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "メールアドレスまたはパスワードが正しくありません。"},
            status_code=401,
        )
    request.session["user_id"] = user.user_id
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/logout", tags=["auth"])
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
