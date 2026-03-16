from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

router = APIRouter()

# --- パスとテンプレート設定 ---
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# --- Jinja2テンプレート用のサンプルデータモデル ---
class Item(BaseModel):
    id: int
    name: str

# --- HTMLページを返すエンドポイント ---
@router.get("/", response_class=HTMLResponse, tags=["pages"])
async def read_root(request: Request):
    context = {
        "request": request, # テンプレートでurl_forを使うために必須
        "page_title": "Jinja2 サンプル",
        "current_user": {"name": "山田 太郎"},
        "items": [Item(id=1, name="リンゴ"), Item(id=2, name="バナナ"), Item(id=3, name="オレンジ")]
    }
    return templates.TemplateResponse("index.html", context)


@router.get("/test", response_class=HTMLResponse, tags=["pages"])
async def read_test(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

@router.get("/chat", response_class=HTMLResponse, tags=["pages"])
async def read_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@router.get("/sample-page-1", response_class=HTMLResponse, tags=["pages"])
async def read_sample1(request: Request):
    return templates.TemplateResponse("sample-page-1.html", {"request": request})

@router.get("/sample-page-2", response_class=HTMLResponse, tags=["pages"])
async def read_sample2(request: Request):
    return templates.TemplateResponse("sample-page-2.html", {"request": request})

@router.get("/sample-page-3", response_class=HTMLResponse, tags=["pages"])
async def read_sample3(request: Request):
    return templates.TemplateResponse("sample-page-3.html", {"request": request})

@router.get("/training", response_class=HTMLResponse, tags=["pages"])
async def read_training(request: Request):
    ###########################################################
    # ダミーデータ
    trainings_data = [
        {"id": 1, "title": "Python基礎研修", "description": "Pythonの基本的な文法から関数、クラスまでを学びます。", "category": "Programming", "level": "初級", "duration": "3日間"},
        {"id": 2, "title": "応用SQL講座", "description": "複雑な結合やウィンドウ関数など、実践的なSQLスキルを習得します。", "category": "Database", "level": "中級", "duration": "2日間"},
        {"id": 3, "title": "Gitチーム開発入門", "description": "ブランチ戦略やコンフリクト解消など、チーム開発に必要なGit操作を学びます。", "category": "DevOps", "level": "初級", "duration": "1日間"},
    ]
    user_skills_data = ["Python", "SQL", "Git"]
    ###########################################################
    return templates.TemplateResponse("training.html", {
        "request": request,
        "trainings_data": trainings_data,
        "user_skills_data": user_skills_data
    })

@router.get("/skill-check", response_class=HTMLResponse, tags=["pages"])
async def read_skill_check(request: Request):
    ###########################################################
    # ダミーデータ
    user_skills_data = ["Python", "SQL", "Git", "JavaScript"]
    ###########################################################
    return templates.TemplateResponse("skill-check.html", {
        "request": request,
        "user_skills_data": user_skills_data
    })

@router.get("/practice", response_class=HTMLResponse, tags=["pages"])
async def read_practice(request: Request):
    return templates.TemplateResponse("practice.html", {"request": request})
