from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(max_length=100)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=20)

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

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
