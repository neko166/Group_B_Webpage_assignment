"""
schemas.py – Pydantic スキーマ定義（リクエスト / レスポンス）
"""

from __future__ import annotations
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: int
    name: str
    email: str
    current_role: Optional[str] = None
    target_role: Optional[str] = None

    class Config:
        from_attributes = True

# ══════════════════════════════════════════════
# Skill
# ══════════════════════════════════════════════
class SkillBase(BaseModel):
    skill_name: str  = Field(..., max_length=100, example="Python")
    category:   Optional[str] = Field(None, max_length=50, example="バックエンド")


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    skill_id: int

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════
# UserSkill  （ユーザーが保有するスキル）
# ══════════════════════════════════════════════
class UserSkillBase(BaseModel):
    skill_id:    int = Field(..., example=1)
    skill_level: int = Field(..., ge=1, le=5, example=4)


class UserSkillCreate(UserSkillBase):
    pass


class UserSkillUpdate(BaseModel):
    skill_level: int = Field(..., ge=1, le=5)


class UserSkillResponse(BaseModel):
    id:          int
    skill_id:    int
    skill_name:  str          # Skill.skill_name を JOIN して返す
    category:    Optional[str]
    skill_level: int

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════
# CareerHistory  （職務経歴）
# ══════════════════════════════════════════════
class CareerHistoryBase(BaseModel):
    project_name: str           = Field(..., max_length=200, example="ECサイト開発")
    role:         Optional[str] = Field(None, max_length=100, example="バックエンドエンジニア")
    tech_stack:   Optional[str] = Field(None, example="Python,FastAPI,PostgreSQL")
    period_start: Optional[date] = Field(None, example="2023-04-01")
    period_end:   Optional[date] = Field(None, example="2024-03-31")
    description:  Optional[str] = Field(None)


class CareerHistoryCreate(CareerHistoryBase):
    pass


class CareerHistoryUpdate(CareerHistoryBase):
    pass


class CareerHistoryResponse(CareerHistoryBase):
    career_id: int
    user_id:   int

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════
# User
# ══════════════════════════════════════════════
class UserBase(BaseModel):
    name:         str           = Field(..., max_length=100, example="山田 太郎")
    email:        str           = Field(..., max_length=255, example="yamada@example.com")
    current_role: Optional[str] = Field(None, max_length=100, example="インフラエンジニア")
    target_role:  Optional[str] = Field(None, max_length=100, example="機械学習エンジニア")
    #username:     Optional[str] = Field(None, max_length=100, example="yamada")
    #password:     Optional[str] = Field(None, max_length=255, example="dummy_password")


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    current_role: Optional[str] = Field(None, max_length=100)
    target_role:  Optional[str] = Field(None, max_length=100)


class UserResponse(UserBase):
    user_id: int

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════
# Training
# ══════════════════════════════════════════════
class TrainingBase(BaseModel):
    title:       str            = Field(..., max_length=200)
    description: Optional[str] = None
    tags:        Optional[str] = None
    held_at:     Optional[str] = Field(None, max_length=100)
    location:    Optional[str] = Field(None, max_length=100)
    target:      Optional[str] = Field(None, max_length=200)


class TrainingResponse(TrainingBase):
    training_id: int
    match:       Optional[int] = Field(None, description="マッチ度（%）※ AI 算出値")

    class Config:
        from_attributes = True

# ══════════════════════════════════════════════
# Project
# ══════════════════════════════════════════════
class ProjectBase(BaseModel):
    required_skills: str
    project_name: str
    company: str
    project_overview: str
    match_rate: int
    employ_type: str
    project_duration: date


# 登録用
class ProjectCreate(ProjectBase):
    pass


# 更新用
class ProjectUpdate(ProjectBase):
    pass


# レスポンス用
class Project(ProjectBase):
    project_id: int

    class Config:
        from_attributes = True

# --- 認証関連スキーマ ---------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ══════════════════════════════════════════════
# Roadmap
# ══════════════════════════════════════════════
class RoadmapResponse(BaseModel):
    roadmap_id:  int
    user_id:     int
    target_role: str
    content_json: str                # JSON文字列をそのまま返す
    created_at:  Optional[str] = None

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════
# Dashboard  （画面初期表示用まとめレスポンス）
# ══════════════════════════════════════════════
class DashboardResponse(BaseModel):
    user:      UserResponse
    skills:    List[UserSkillResponse]
    careers:   List[CareerHistoryResponse]
    trainings: List[TrainingResponse]
    projects:  List[Project]