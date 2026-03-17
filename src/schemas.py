from __future__ import annotations
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ══════════════════════════════════════════════
# Skill
# ══════════════════════════════════════════════
class SkillBase(BaseModel):
    skill_name: str         = Field(..., max_length=100, example="Python")
    category:   Optional[str] = Field(None, max_length=50, example="バックエンド")

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    skill_id: int
    class Config:
        from_attributes = True


# ══════════════════════════════════════════════
# UserSkill（ユーザー保有スキル）
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
    skill_name:  str
    category:    Optional[str]
    skill_level: int
    class Config:
        from_attributes = True


# ══════════════════════════════════════════════
# CareerHistory（職務経歴）
# ══════════════════════════════════════════════
class CareerHistoryBase(BaseModel):
    project_name: str            = Field(..., max_length=200, example="ECサイト開発")
    role:         Optional[str]  = Field(None, max_length=100, example="バックエンドエンジニア")
    tech_stack:   Optional[str]  = Field(None, example="Python,FastAPI,PostgreSQL")
    period_start: Optional[date] = Field(None, example="2023-04-01")
    period_end:   Optional[date] = Field(None, example="2024-03-31")
    description:  Optional[str]  = Field(None)

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
    current_role: Optional[str] = Field(None, max_length=100)
    target_role:  Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    current_role:     Optional[str] = None
    target_role:      Optional[str] = None
    name:             Optional[str] = None
    age:              Optional[int] = None
    experience_years: Optional[int] = None
    available_from:   Optional[str] = None
    work_locations:   Optional[str] = None
    desired_rate_min: Optional[int] = None
    desired_rate_max: Optional[int] = None

class UserResponse(UserBase):
    user_id:          int
    age:              Optional[int] = None
    experience_years: Optional[int] = None
    available_from:   Optional[str] = None
    work_locations:   Optional[str] = None
    desired_rate_min: Optional[int] = None
    desired_rate_max: Optional[int] = None
    class Config:
        from_attributes = True

User = UserResponse

# ══════════════════════════════════════════════
# Training（研修）
# ══════════════════════════════════════════════
class TrainingBase(BaseModel):
    title:       str            = Field(..., max_length=200)
    description: Optional[str] = None
    tags:        Optional[str]  = None
    held_at:     Optional[str]  = Field(None, max_length=100)
    location:    Optional[str]  = Field(None, max_length=100)
    target:      Optional[str]  = Field(None, max_length=200)

class TrainingResponse(TrainingBase):
    training_id: int
    match:       Optional[int] = Field(None, description="マッチ度（%）※ AI 算出値")
    class Config:
        from_attributes = True


# ══════════════════════════════════════════════
# Project（案件）
# ══════════════════════════════════════════════
class ProjectBase(BaseModel):
    project_name:     str           = Field(..., max_length=200)
    company:          str           = Field(..., max_length=100)
    project_overview: Optional[str] = Field(None, max_length=200)
    required_skills:  Optional[str] = None
    match_rate:       Optional[int] = None
    employ_type:      Optional[str] = Field(None, max_length=50)
    project_duration: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    project_id: int
    class Config:
        from_attributes = True


# ══════════════════════════════════════════════
# Roadmap（ロードマップ）
# ══════════════════════════════════════════════
class RoadmapStep(BaseModel):
    step_number:       int              = 0
    title:             str             = ""
    description:       str             = ""
    duration:          Optional[str]   = ""
    skills_to_acquire: List[str]       = []
    status:            str             = "upcoming"
    progress:          int             = 0

class RoadmapContent(BaseModel):
    steps:                    List[RoadmapStep] = []
    overall_progress:         int               = 0
    estimated_total_duration: Optional[str]     = ""

class RoadmapGenerateRequest(BaseModel):
    user_id:     int            = Field(..., example=1)
    target_role: Optional[str] = Field(None, description="目標ロール（省略時はDBから取得）")

class RoadmapResponse(BaseModel):
    roadmap_id:  int
    user_id:     int
    target_role: str
    content:     RoadmapContent
    created_at:  Optional[datetime] = None
    class Config:
        from_attributes = True

class StepProjectsResponse(BaseModel):
    step_number: int
    projects:    List[ProjectResponse]


# ══════════════════════════════════════════════
# Dashboard（画面初期表示用まとめレスポンス）
# ══════════════════════════════════════════════
class DashboardResponse(BaseModel):
    user:      UserResponse
    skills:    List[UserSkillResponse]
    careers:   List[CareerHistoryResponse]
    trainings: List[TrainingResponse]
    projects:  List[ProjectResponse]


# ══════════════════════════════════════════════
# Chat Session / Message（会話履歴）
# ══════════════════════════════════════════════
class ChatMessageCreate(BaseModel):
    role:    str = Field(..., example="user")
    content: str = Field(..., example="AIエンジニアになりたい")

class ChatMessageResponse(BaseModel):
    message_id: int
    session_id: int
    role:       str
    content:    str
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    user_id: int = Field(..., example=1)

class ChatSessionResponse(BaseModel):
    session_id:    int
    user_id:       int
    title:         str
    created_at:    Optional[datetime] = None
    updated_at:    Optional[datetime] = None
    message_count: int = 0
    class Config:
        from_attributes = True

class ChatSessionDetail(ChatSessionResponse):
    messages: List[ChatMessageResponse] = []


# ══════════════════════════════════════════════
# 認証
# ══════════════════════════════════════════════
class Token(BaseModel):
    access_token: str
    token_type:   str

class TokenData(BaseModel):
    username: Optional[str] = None
    
# --- Dify連携用モデル ---
class DifyChatRequest(BaseModel):
    message: str
    conversation_id: str = ""
    user_id: str
    mode: str = "general"
    current_conditions: str = ""
    training_sessions: str = ""
    user_skills: str = ""
    skillcheck_answer: Optional[str] = ""
    answer: Optional[str] = ""
    practice_answer: Optional[str] = ""
    hint_request: Optional[bool] = False
