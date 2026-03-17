from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy import DateTime


# ──────────────────────────────────────────────
# users
# ──────────────────────────────────────────────
class User(Base):
    __tablename__ = "Users"

    user_id          = Column(Integer, primary_key=True, index=True)
    name             = Column(String(100), nullable=False)
    email            = Column(String(255), unique=True, nullable=False)
    password         = Column(String(255), nullable=True)
    current_role     = Column(String(100), nullable=True)
    target_role      = Column(String(100), nullable=True)
    age              = Column(Integer,     nullable=True)             # 年齢
    experience_years = Column(Integer,     nullable=True)             # 経験年数
    available_from   = Column(String(50),  nullable=True)             # 稼働可能時期
    work_locations   = Column(String(500), nullable=True)             # 勤務地（カンマ区切り）
    desired_rate_min = Column(Integer,     nullable=True)             # 希望単価（下限）
    desired_rate_max = Column(Integer,     nullable=True)             # 希望単価（上限）

    # リレーション
    user_skills      = relationship("UserSkill",     back_populates="user", cascade="all, delete-orphan")
    career_histories = relationship("CareerHistory", back_populates="user", cascade="all, delete-orphan")
    roadmaps         = relationship("Roadmap",       back_populates="user", cascade="all, delete-orphan")
    chat_sessions    = relationship("ChatSession",   back_populates="user", cascade="all, delete-orphan")

# ──────────────────────────────────────────────
# skills  (マスタ)
# ──────────────────────────────────────────────
class Skill(Base):
    __tablename__ = "Skills"

    skill_id   = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(100), nullable=False, unique=True)
    category   = Column(String(50), nullable=True)   # バックエンド / インフラ 等

    user_skills = relationship("UserSkill", back_populates="skill")


# ──────────────────────────────────────────────
# user_skills  (ユーザー × スキル × レベル)
# ──────────────────────────────────────────────
class UserSkill(Base):
    __tablename__ = "User_Skills"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE"), nullable=False)
    skill_id    = Column(Integer, ForeignKey("Skills.skill_id", ondelete="CASCADE"), nullable=False)
    skill_level = Column(Integer, nullable=False, default=1)  # 1〜5

    user  = relationship("User",  back_populates="user_skills")
    skill = relationship("Skill", back_populates="user_skills")


# ──────────────────────────────────────────────
# career_history  (職務経歴)
# ──────────────────────────────────────────────
class CareerHistory(Base):
    __tablename__ = "Career_History"

    career_id    = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE"), nullable=False)
    project_name = Column(String(200), nullable=False)   # プロジェクト名
    role         = Column(String(100), nullable=True)    # 担当ポジション
    tech_stack   = Column(Text, nullable=True)           # 使用技術（カンマ区切りで保存）
    period_start = Column(Date, nullable=True)           # 開始年月
    period_end   = Column(Date, nullable=True)           # 終了年月（null = 現在）
    description  = Column(Text, nullable=True)           # 業務内容

    user = relationship("User", back_populates="career_histories")


# ──────────────────────────────────────────────
# trainings  (研修マスタ)
# ──────────────────────────────────────────────
class Training(Base):
    __tablename__ = "Trainings"

    training_id  = Column(Integer, primary_key=True, index=True)
    title        = Column(String(200), nullable=False)
    description  = Column(Text, nullable=True)
    tags         = Column(String(500), nullable=True)  # カンマ区切りタグ
    held_at      = Column(String(100), nullable=True)  # 開催日時（テキスト）
    location     = Column(String(100), nullable=True)  # 開催場所
    target       = Column(String(200), nullable=True)  # 対象者


# ──────────────────────────────────────────────
# projects  (案件マスタ)
# ──────────────────────────────────────────────
class Project(Base):
    __tablename__ = "Project"

    project_id  = Column(Integer, primary_key=True, index=True)
    required_skills        = Column(Text, nullable=False)       # 必須スキル（カンマ区切りで保存）
    project_name  = Column(String(200), nullable=False)         # プロジェクト名
    company         = Column(String(100), nullable=False)       # 企業名
    project_overview      = Column(String(200), nullable=False) # 案件概要
    match_rate     = Column(Integer, nullable=False)            # 適合率
    employ_type       = Column(String(50), nullable=False)      # 勤務形態
    project_duration = Column(Date, nullable=False)             # 勤務期間

# ──────────────────────────────────────────────
# roadmaps  (ロードマップ)
# ──────────────────────────────────────────────
class Roadmap(Base):
    __tablename__ = "Roadmaps"

    roadmap_id   = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    target_role  = Column(String(100), nullable=False)          # 生成時の目標ロール
    content_json = Column(Text, nullable=False)                 # AIが生成したロードマップ（JSON）
    created_at   = Column(DateTime, default=datetime.utcnow)   # 生成日時

    user = relationship("User", back_populates="roadmaps")


# ──────────────────────────────────────────────
# chat_sessions  (会話セッション)
# ──────────────────────────────────────────────
class ChatSession(Base):
    __tablename__ = "Chat_Sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE"), nullable=False)
    title      = Column(String(200), nullable=False, default="新しい相談")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    user     = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session",
                            cascade="all, delete-orphan",
                            order_by="ChatMessage.created_at")


# ──────────────────────────────────────────────
# chat_messages  (会話メッセージ)
# ──────────────────────────────────────────────
class ChatMessage(Base):
    __tablename__ = "Chat_Messages"

    message_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("Chat_Sessions.session_id", ondelete="CASCADE"), nullable=False)
    role       = Column(String(20),  nullable=False)   # 'user' or 'assistant'
    content    = Column(Text,        nullable=False)
    created_at = Column(DateTime,    nullable=True)

    session = relationship("ChatSession", back_populates="messages")