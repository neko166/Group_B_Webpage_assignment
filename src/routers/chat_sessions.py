from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from database import get_db
import models, schemas

router = APIRouter(prefix="/api/chat/sessions", tags=["chat_sessions"])


# ══════════════════════════════════════════════
# セッション一覧取得
# ══════════════════════════════════════════════
@router.get("", response_model=List[schemas.ChatSessionResponse])
def list_sessions(user_id: int = 1, db: DBSession = Depends(get_db)):
    sessions = (
        db.query(models.ChatSession)
        .filter(models.ChatSession.user_id == user_id)
        .order_by(models.ChatSession.updated_at.desc())
        .all()
    )
    result = []
    for s in sessions:
        count = (
            db.query(func.count(models.ChatMessage.message_id))
            .filter(models.ChatMessage.session_id == s.session_id)
            .scalar()
        )
        result.append(schemas.ChatSessionResponse(
            session_id=s.session_id,
            user_id=s.user_id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=count or 0,
        ))
    return result


# ══════════════════════════════════════════════
# セッション作成
# ══════════════════════════════════════════════
@router.post("", response_model=schemas.ChatSessionResponse)
def create_session(payload: schemas.ChatSessionCreate, db: DBSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    session = models.ChatSession(
        user_id=payload.user_id,
        title="新しい相談",
        created_at=now,
        updated_at=now,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return schemas.ChatSessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0,
    )


# ══════════════════════════════════════════════
# セッション詳細取得（メッセージ含む）
# ══════════════════════════════════════════════
@router.get("/{session_id}", response_model=schemas.ChatSessionDetail)
def get_session(session_id: int, db: DBSession = Depends(get_db)):
    session = (
        db.query(models.ChatSession)
        .filter(models.ChatSession.session_id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msgs = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session_id)
        .order_by(models.ChatMessage.created_at)
        .all()
    )
    return schemas.ChatSessionDetail(
        session_id=session.session_id,
        user_id=session.user_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(msgs),
        messages=[
            schemas.ChatMessageResponse(
                message_id=m.message_id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in msgs
        ],
    )


# ══════════════════════════════════════════════
# メッセージ追加
# ══════════════════════════════════════════════
@router.post("/{session_id}/messages", response_model=schemas.ChatMessageResponse)
def add_message(
    session_id: int,
    payload: schemas.ChatMessageCreate,
    db: DBSession = Depends(get_db),
):
    session = (
        db.query(models.ChatSession)
        .filter(models.ChatSession.session_id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 最初のユーザーメッセージをセッションタイトルに設定
    if payload.role == "user":
        user_count = (
            db.query(func.count(models.ChatMessage.message_id))
            .filter(
                models.ChatMessage.session_id == session_id,
                models.ChatMessage.role == "user",
            )
            .scalar()
        )
        if user_count == 0:
            session.title = payload.content[:60]

    now = datetime.now(timezone.utc)
    message = models.ChatMessage(
        session_id=session_id,
        role=payload.role,
        content=payload.content,
        created_at=now,
    )
    session.updated_at = now
    db.add(message)
    db.commit()
    db.refresh(message)
    return schemas.ChatMessageResponse(
        message_id=message.message_id,
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
    )


# ══════════════════════════════════════════════
# セッション削除
# ══════════════════════════════════════════════
@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, db: DBSession = Depends(get_db)):
    session = (
        db.query(models.ChatSession)
        .filter(models.ChatSession.session_id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
