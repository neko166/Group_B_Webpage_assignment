import json
from pathlib import Path
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from database import get_db
import models

router = APIRouter()

# --- パスとテンプレート設定 ---
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# --- Jinja2テンプレート用のサンプルデータモデル ---
class Item(BaseModel):
    id: int
    name: str


def get_current_user(request: Request, db: Session):
    """セッションからログイン中のユーザーを取得。未ログインなら None を返す"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(models.User).filter(models.User.user_id == user_id).first()


@router.get("/", tags=["pages"])
def index():
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/chat", response_class=HTMLResponse, tags=["pages"])
def read_chat(request: Request, db: Session = Depends(get_db)):
    """AIキャリアアドバイザー チャット画面"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("chat.html", {
        "request":     request,
        "active_page": "chat",
        "user":        user,
    })
 
 
@router.get("/roadmap", response_class=HTMLResponse, tags=["pages"])
def read_roadmap(request: Request, db: Session = Depends(get_db)):
    """パーソナライズロードマップ画面"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("roadmap.html", {
        "request":     request,
        "active_page": "roadmap",
        "user":        user,
    })


@router.get("/summary", response_class=HTMLResponse, tags=["pages"])
def read_summary(request: Request, db: Session = Depends(get_db)):
    """営業向けサマリー画面"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("summary.html", {
        "request":     request,
        "active_page": "summary",
        "user":        user,
    })


@router.get("/dashboard", response_class=HTMLResponse, tags=["pages"])
def read_dashboard(request: Request, db: Session = Depends(get_db)):
    """ダッシュボード画面"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    user_id = user.user_id

    user_skills = (
        db.query(models.UserSkill)
        .options(joinedload(models.UserSkill.skill))
        .filter(models.UserSkill.user_id == user_id)
        .all()
    )

    careers = (
        db.query(models.CareerHistory)
        .filter(models.CareerHistory.user_id == user_id)
        .order_by(models.CareerHistory.period_start.desc())
        .all()
    )

    skill_names = {us.skill.skill_name.lower() for us in user_skills}

    trainings_raw = db.query(models.Training).all()
    trainings_with_match = []
    for t in trainings_raw:
        tags = [tag.strip().lower() for tag in (t.tags or "").split(",") if tag.strip()]
        match = int(len(skill_names & set(tags)) / len(tags) * 100) if tags else 0
        trainings_with_match.append((t, match))
    trainings_with_match = sorted(trainings_with_match, key=lambda x: x[1], reverse=True)[:3]

    skills_json = json.dumps([
        {
            "id":          us.id,
            "skill_id":    us.skill_id,
            "skill_name":  us.skill.skill_name,
            "category":    us.skill.category or "",
            "skill_level": us.skill_level,
        }
        for us in user_skills
    ], ensure_ascii=False)

    careers_json = json.dumps([
        {
            "career_id":    c.career_id,
            "project_name": c.project_name,
            "role":         c.role or "",
            "tech_stack":   c.tech_stack or "",
            "period_start": c.period_start.strftime("%Y-%m") if c.period_start else "",
            "period_end":   c.period_end.strftime("%Y-%m")   if c.period_end   else "",
            "description":  c.description or "",
        }
        for c in careers
    ], ensure_ascii=False)

    trainings_json = json.dumps([
        {
            "training_id": t.training_id,
            "title":       t.title,
            "description": t.description or "",
            "target":      t.target or "",
            "tags":        t.tags or "",
            "held_at":     t.held_at or "",
            "location":    t.location or "",
            "match":       m,
        }
        for t, m in trainings_with_match
    ], ensure_ascii=False)

    return templates.TemplateResponse("dashboard.html", {
        "request":       request,
        "active_page":   "dashboard",
        "user":          user,
        "skills_json":   skills_json,
        "careers_json":  careers_json,
        "trainings_json": trainings_json,
    })