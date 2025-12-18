from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


# ============ 用户相关 ============
class UserBase(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    total_study_time: int = 0
    correct_answers: int = 0
    total_answers: int = 0
    current_streak: int = 0
    badges: List[str] = []
    correct_rate: float = 0.0

    class Config:
        from_attributes = True


# ============ 课程相关 ============
class LessonProgressCreate(BaseModel):
    lesson_id: str
    completed: bool = False
    score: int = 0


class LessonProgressResponse(BaseModel):
    id: UUID
    lesson_id: str
    completed: bool
    score: int
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    lesson_id: str
    question_id: str
    answer: int


class QuizResult(BaseModel):
    lesson_id: str
    correct_count: int
    total_count: int
    score: int


# ============ 聊天相关 ============
class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    figure_id: Optional[str] = None  # 历史人物ID
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2000, ge=1, le=4000)


class ChatHistoryResponse(BaseModel):
    id: UUID
    figure_id: Optional[str]
    messages: List[dict]
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 好友相关 ============
class FriendRequest(BaseModel):
    friend_id: UUID


class FriendResponse(BaseModel):
    id: UUID
    username: Optional[str]
    avatar_url: Optional[str]
    status: str  # online, offline, in_game

    class Config:
        from_attributes = True


# ============ PK 对战相关 ============
class PKStartRequest(BaseModel):
    opponent_id: UUID


class PKAnswerSubmit(BaseModel):
    match_id: UUID
    question_index: int
    answer: int


class PKMatchResponse(BaseModel):
    id: UUID
    opponent_id: UUID
    opponent_name: Optional[str]
    my_score: int
    opponent_score: int
    status: str
    questions: List[dict]
    current_question: int = 0

    class Config:
        from_attributes = True


# ============ 通用响应 ============
class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    success: bool = False
