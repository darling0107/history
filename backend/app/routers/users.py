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


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户资料"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # 如果用户不存在，创建一个新的用户资料
        user = UserProfile(id=current_user.id, username=current_user.email)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    username: Optional[str] = None,
    avatar_url: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户资料"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

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
        total_study_time=stats.total_study_time,
        correct_answers=stats.correct_answers,
        total_answers=stats.total_answers,
        current_streak=stats.current_streak,
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
    result = await db.execute(
        select(UserStats).where(UserStats.user_id == current_user.id)
    )
    stats = result.scalar_one_or_none()

    if not stats:
        stats = UserStats(user_id=current_user.id, total_study_time=minutes)
        db.add(stats)
    else:
        stats.total_study_time += minutes

    await db.commit()
    return MessageResponse(message=f"Added {minutes} minutes of study time")
