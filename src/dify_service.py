import os
import httpx
import logging
from fastapi import HTTPException

from schemas import DifyChatRequest

logger = logging.getLogger(__name__)


async def call_dify_chat_api(req: DifyChatRequest) -> dict:
    """
    DifyのチャットAPIを呼び出し、結果を返却する。
    """
    DIFY_API_KEY = os.getenv("DIFY_API_KEY_N")
    DIFY_API_URL = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1/chat-messages")

    if not DIFY_API_KEY:
        # APIキーが環境変数に設定されていない場合はサーバーエラーを返す
        raise HTTPException(status_code=500, detail="DIFY_API_KEY environment variable is not set.")

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": {k: v for k, v in req.model_dump().items() if k not in ["message", "conversation_id", "user_id"]},
        "query": req.message,
        "response_mode": "blocking",
        "conversation_id": req.conversation_id,
        "user": req.user_id
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(DIFY_API_URL, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Dify API Error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail="External API call failed.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while calling Dify API: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="An internal error occurred.")