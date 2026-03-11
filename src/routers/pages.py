from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

router = APIRouter()

# --- パスとテンプレート設定 ---
# このルーターファイルからの相対パスでテンプレートディレクトリを解決します。
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# --- Jinja2テンプレート用のサンプルデータモデル ---
class Item(BaseModel):
    id: int
    name: str

# --- HTMLページを返すエンドポイント ---
@router.get("/", response_class=HTMLResponse, tags=["pages"])
async def read_root(request: Request):
    # テンプレートに渡すデータ
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