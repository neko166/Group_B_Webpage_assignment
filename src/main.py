import os
import json
import re
from pathlib import Path
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel as PydanticBase
from dotenv import load_dotenv

# .env をロード（他の import より前に実行）
load_dotenv()

from routers import users, pages, roadmap, chat_sessions, auth   # noqa: E402
from database import engine, Base  # noqa: E402
from exceptions import AppException  # noqa: E402

# テーブル自動作成
Base.metadata.create_all(bind=engine)

# ===== FastAPI アプリ =====
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="hcs-secret-key-2026")

# パス設定
BASE_DIR = Path(__file__).resolve().parent

# 静的ファイル配信
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# ルーター登録
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(users.router,         prefix="/users", tags=["users"])
app.include_router(roadmap.router)
app.include_router(chat_sessions.router)


# ===== リクエストスキーマ =====
class ChatRequest(PydanticBase):
    message:      str
    current_role: str = ""
    target_role:  str = ""
    user_name:    str = ""


class RoadmapRequest(PydanticBase):
    current_role: str
    target_role:  str
    user_name:    str = ""


# ===== Ollama ヘルパー =====
async def _get_ollama_model(client: httpx.AsyncClient, base_url: str) -> str:
    """環境変数のモデルが存在すれば使用、なければインストール済みの最初のモデルを返す"""
    configured = os.getenv("OLLAMA_MODEL", "qwen2.5")
    try:
        tags = await client.get(f"{base_url}/api/tags")
        models = [m["name"] for m in tags.json().get("models", [])]
        if not models:
            raise RuntimeError(
                "Ollamaにモデルがインストールされていません。"
                f"`ollama pull {configured}` を実行してください。"
            )
        # 設定モデルが存在すればそれを使用、なければ最初のモデルを使用
        for m in models:
            if m.startswith(configured.split(":")[0]):
                return m
        return models[0]
    except httpx.ConnectError:
        raise RuntimeError("Ollamaに接続できません。Ollamaが起動しているか確認してください。")


async def _call_ollama(prompt: str, max_tokens: int = 2000) -> str:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    async with httpx.AsyncClient(timeout=120) as client:
        model = await _get_ollama_model(client, base_url)
        resp = await client.post(
            f"{base_url}/api/chat",
            json={
                "model":    model,
                "messages": [{"role": "user", "content": prompt}],
                "stream":   False,
                "options":  {"num_predict": max_tokens},
            },
        )
        if resp.status_code == 404:
            # 旧バージョン対応: /api/generate にフォールバック
            resp = await client.post(
                f"{base_url}/api/generate",
                json={
                    "model":   model,
                    "prompt":  prompt,
                    "stream":  False,
                    "options": {"num_predict": max_tokens},
                },
            )
            resp.raise_for_status()
            return resp.json().get("response", "")
        resp.raise_for_status()
    return resp.json()["message"]["content"]


# ===== Ollama ストリーミングジェネレーター =====
async def _stream_ollama(messages: list, max_tokens: int = 1000):
    """Ollamaからトークンをストリームし Server-Sent Events 形式で yield する"""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    async with httpx.AsyncClient(timeout=120) as client:
        model = await _get_ollama_model(client, base_url)

        # /api/chat を試みる（Ollama 0.1.14+）
        use_generate = False
        async with client.stream("POST", f"{base_url}/api/chat", json={
            "model":    model,
            "messages": messages,
            "stream":   True,
            "options":  {"num_predict": max_tokens},
        }) as resp:
            if resp.status_code == 404:
                use_generate = True
            else:
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data  = json.loads(line)
                        token = data.get("message", {}).get("content", "")
                        if token:
                            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
                        if data.get("done"):
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue

        # 旧バージョン対応: /api/generate にフォールバック（messages を結合してプレーンテキストに）
        if use_generate:
            flat_prompt = "\n\n".join(m["content"] for m in messages)
            async with client.stream("POST", f"{base_url}/api/generate", json={
                "model":   model,
                "prompt":  flat_prompt,
                "stream":  True,
                "options": {"num_predict": max_tokens},
            }) as resp:
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data  = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
                        if data.get("done"):
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue

    yield "data: [DONE]\n\n"


# ===== チャット API（Ollama ストリーミング） =====
@app.post("/api/chat")
async def chat_api(payload: ChatRequest):
    system_content = (
        "あなたはプロのAIキャリアアドバイザーです。"
        "必ず日本語のみで回答してください。英語は絶対に使用しないでください。\n"
        f"ユーザー情報:\n"
        f"- 現在のロール: {payload.current_role or '未設定'}\n"
        f"- 目標ロール:   {payload.target_role or '未設定'}\n"
        f"- 名前:         {payload.user_name or '未設定'}\n"
        "回答は簡潔かつ具体的に日本語で述べてください。"
        "キャリアパス、必要なスキル、学習リソースについてアドバイスしてください。"
    )
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user",   "content": payload.message},
    ]
    return StreamingResponse(
        _stream_ollama(messages, max_tokens=1000),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ===== ロードマップ生成 API（簡易版・DB不使用・Ollama） =====
@app.post("/api/roadmap/simple-generate")
async def simple_generate_roadmap(payload: RoadmapRequest):
    """チャット画面から呼び出す簡易ロードマップ生成（DB保存なし）"""
    prompt = f"""以下の情報を元に、キャリアロードマップをJSON形式で生成してください。

現在のロール: {payload.current_role}
目標ロール:   {payload.target_role}

以下のJSON形式のみで回答してください（説明文・マークダウン不要）:
{{
  "steps": [
    {{
      "title": "職種名",
      "description": "この職種の説明（1〜2文）",
      "skills": ["スキル1", "スキル2", "スキル3"],
      "status": "done" または "active" または "pending",
      "months": 到達までの目安月数（数値）,
      "resources": "推奨学習リソース（任意）"
    }}
  ]
}}

ルール:
- steps は現在ロールから目標ロールまで3〜5段階で設定
- 最初のstepはstatusを"done"（現在地点）
- 2番目のstepはstatusを"active"（現在進行中）
- 残りはstatusを"pending"
- skillsは各ステップで3〜5個
- monthsは累積ではなく、そのステップへの到達目安
- 日本語で出力"""

    text  = await _call_ollama(prompt, max_tokens=2000)
    match = re.search(r'\{[\s\S]*\}', text)
    data  = json.loads(match.group()) if match else {"steps": []}
    return data


# ===== カスタム例外ハンドラ =====
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )