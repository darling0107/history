from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class UserProfile(Base):
    """用户资料表"""
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=True)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LessonProgress(Base):
    """课程学习进度表"""
    __tablename__ = "lesson_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    lesson_id = Column(String(50), nullable=False)
    completed = Column(Boolean, default=False)
    score = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatHistory(Base):
    """聊天历史表"""
    __tablename__ = "chat_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    figure_id = Column(String(50), nullable=True)  # 历史人物ID，为空表示普通AI聊天
    messages = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserPreferences(Base):
    """用户偏好设置表"""
    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), primary_key=True)
    preferences = Column(JSON, default=dict)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserStats(Base):
    """用户学习统计表"""
    __tablename__ = "user_stats"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), primary_key=True)
    total_study_time = Column(Integer, default=0)  # 总学习时长（分钟）
    correct_answers = Column(Integer, default=0)   # 正确答题数
    total_answers = Column(Integer, default=0)     # 总答题数
    current_streak = Column(Integer, default=0)    # 连续学习天数
    last_study_date = Column(DateTime(timezone=True), nullable=True)
    badges = Column(JSON, default=list)            # 已获得勋章
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Friendship(Base):
    """好友关系表"""
    __tablename__ = "friendships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    friend_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PKMatch(Base):
    """PK对战记录表"""
    __tablename__ = "pk_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user1_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    user2_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    user1_score = Column(Integer, default=0)
    user2_score = Column(Integer, default=0)
    winner_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(20), default="ongoing")  # ongoing, completed
    questions = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
