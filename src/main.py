from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
# .envファイルをロードします。他のモジュールが環境変数を読み込む前に実行する必要があります。
load_dotenv()

# E402:「モジュールのインポートはファイルの先頭で行うべき」という警告を無視
from routers import users, pages  # noqa: E402
from database import engine, Base  # noqa: E402
from exceptions import AppException  # noqa: E402

Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- パス設定 ---
# アプリケーションの起動場所に関わらず、main.pyからの相対パスで静的ファイルやテンプレートを解決します。
BASE_DIR = Path(__file__).resolve().parent

# 静的ファイル（CSS, JS, 画像など）を /static パスで配信します。
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# --- カスタム例外ハンドラ ---
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

app.include_router(pages.router)
app.include_router(users.router, prefix="/users", tags=["users"])
