import os
from typing import Type, TypeVar
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi import Depends

from exceptions import AppException, ErrorCode

# --- データベース接続設定 ---
# 環境変数 `SQLALCHEMY_DATABASE_URL` を読み込みます。
# 環境変数が存在しない場合は、デフォルトでSQLiteデータベース (`default.db`) を使用します。
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./default.db")

# SQLiteの場合のみ、FastAPIのマルチスレッドに関する問題を回避するための設定
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ジェネリクス型定義
T = TypeVar("T")

Base = declarative_base()

# DBセッション取得（共通依存関係）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 汎用的なモデル取得
def get_object_or_404(model: Type[T]):
    def _dependency(id: int, db: Session = Depends(get_db)) -> T:
        db_obj = db.get(model, id)
        if not db_obj:
            # 動的にメッセージを生成して詳細を上書きする例
            raise AppException(
                ErrorCode.RESOURCE_NOT_FOUND,
                detail=f"{model.__name__} が見つかりません。"
            )
        return db_obj
    return _dependency