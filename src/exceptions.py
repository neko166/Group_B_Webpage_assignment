from __future__ import annotations
from enum import Enum
from typing import Optional


class ErrorCode(Enum):
    """
    エラーコードとデフォルトメッセージ、HTTPステータスコードを定義するEnum
    """
    # 認証・認可 (400, 401)
    INCORRECT_USERNAME_OR_PASSWORD = (400, "ユーザー名またはパスワードが正しくありません。")
    INVALID_TOKEN = (401, "無効なトークンです。")
    TOKEN_HAS_EXPIRED = (401, "トークンの有効期限が切れています。")
    RESOURCE_NOT_FOUND = (404, "リソースが見つかりません。")

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class AppException(Exception):
    def __init__(self, error_code: ErrorCode, detail: Optional[str] = None):
        self.status_code = error_code.status_code
        self.detail = detail or error_code.detail
        super().__init__(self.detail)