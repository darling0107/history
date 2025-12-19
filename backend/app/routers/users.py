"""
用户相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.models import UserProfile, UserStats
from app.schemas import UserResponse, UserStatsResponse, MessageResponse
from app.utils import CurrentUser, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


async def ensure_user_profile_exists(user_id, email: str, db: AsyncSession) -> UserProfile:
    """确保用户资料存在，如果不存在则创建"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = UserProfile(id=user_id, username=email or "用户")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户资料"""
    user = await ensure_user_profile_exists(current_user.id, current_user.email, db)
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    username: Optional[str] = None,
    avatar_url: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户资料"""
    user = await ensure_user_profile_exists(current_user.id, current_user.email, db)

    if username is not None:
        user.username = username
    if avatar_url is not None:
        user.avatar_url = avatar_url

    await db.commit()
    await db.refresh(user)
    return user


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_current_user_stats(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户学习统计"""
    # 确保用户资料存在
    await ensure_user_profile_exists(current_user.id, current_user.email, db)

    result = await db.execute(
        select(UserStats).where(UserStats.user_id == current_user.id)
    )
    stats = result.scalar_one_or_none()

    if not stats:
        # 如果没有统计数据，返回默认值
        return UserStatsResponse()

    # 计算正确率
    correct_rate = 0.0
    if stats.total_answers > 0:
        correct_rate = stats.correct_answers / stats.total_answers

    return UserStatsResponse(
        total_study_time=stats.total_study_time or 0,
        correct_answers=stats.correct_answers or 0,
        total_answers=stats.total_answers or 0,
        current_streak=stats.current_streak or 0,
        badges=stats.badges or [],
        correct_rate=correct_rate
    )


@router.post("/me/study-time", response_model=MessageResponse)
async def add_study_time(
    minutes: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加学习时长"""
    # 确保用户资料存在
    await ensure_user_profile_exists(current_user.id, current_user.email, db)

    result = await db.execute(
        select(UserStats).where(UserStats.user_id == current_user.id)
    )
    stats = result.scalar_one_or_none()

    if not stats:
        stats = UserStats(user_id=current_user.id, total_study_time=minutes, badges=[])
        db.add(stats)
    else:
        current_time = stats.total_study_time or 0
        stats.total_study_time = current_time + minutes

    await db.commit()
    return MessageResponse(message=f"Added {minutes} minutes of study time")
