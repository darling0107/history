"""
课程和答题相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List

from app.database import get_db
from app.models import LessonProgress, UserStats, UserProfile
from app.schemas import (
    LessonProgressCreate,
    LessonProgressResponse,
    AnswerSubmit,
    QuizResult,
    MessageResponse
)
from app.utils import CurrentUser, get_current_user
from app.services.lessons import LESSONS, get_lesson_by_id

router = APIRouter(prefix="/lessons", tags=["lessons"])


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


@router.get("")
async def get_all_lessons():
    """获取所有课程列表"""
    return LESSONS


@router.get("/{lesson_id}")
async def get_lesson(lesson_id: str):
    """获取单个课程详情"""
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    return lesson


@router.get("/progress/all", response_model=List[LessonProgressResponse])
async def get_all_progress(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户所有课程进度"""
    result = await db.execute(
        select(LessonProgress).where(LessonProgress.user_id == current_user.id)
    )
    progress_list = result.scalars().all()
    return progress_list


@router.get("/progress/{lesson_id}", response_model=LessonProgressResponse)
async def get_lesson_progress(
    lesson_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取指定课程的进度"""
    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson_id
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found"
        )
    return progress


@router.post("/complete")
async def complete_lesson(
    data: QuizResult,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """完成课程并记录成绩，同时检查勋章解锁"""
    # 确保用户资料存在
    await ensure_user_profile_exists(current_user.id, current_user.email, db)

    # 查找现有进度
    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == data.lesson_id
        )
    )
    progress = result.scalar_one_or_none()

    is_first_complete = progress is None or not progress.completed

    if progress:
        # 更新现有进度
        progress.completed = True
        progress.score = data.score
        progress.completed_at = datetime.utcnow()
    else:
        # 创建新进度
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=data.lesson_id,
            completed=True,
            score=data.score,
            completed_at=datetime.utcnow()
        )
        db.add(progress)

    # 更新用户统计
    stats_result = await db.execute(
        select(UserStats).where(UserStats.user_id == current_user.id)
    )
    stats = stats_result.scalar_one_or_none()

    if not stats:
        stats = UserStats(
            user_id=current_user.id,
            correct_answers=data.correct_count,
            total_answers=data.total_count,
            total_study_time=0,
            badges=[]
        )
        db.add(stats)
    else:
        current_correct = stats.correct_answers or 0
        current_total = stats.total_answers or 0
        stats.correct_answers = current_correct + data.correct_count
        stats.total_answers = current_total + data.total_count

    # 检查并解锁勋章
    new_badges = []
    current_badges = stats.badges or []

    # 获取已完成课程数量
    completed_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.completed == True
        )
    )
    completed_lessons = completed_result.scalars().all()
    completed_count = len(completed_lessons) + (1 if is_first_complete else 0)

    # 计算正确率
    correct_rate = data.correct_count / data.total_count if data.total_count > 0 else 0

    # 历史初学者 - 完成第1门课程
    if completed_count >= 1 and 'badge-1' not in current_badges:
        current_badges.append('badge-1')
        new_badges.append('badge-1')

    # 历史探索者 - 完成3门课程
    if completed_count >= 3 and 'badge-2' not in current_badges:
        current_badges.append('badge-2')
        new_badges.append('badge-2')

    # 完美答题者 - 答题正确率100%
    if correct_rate == 1.0 and 'badge-3' not in current_badges:
        current_badges.append('badge-3')
        new_badges.append('badge-3')

    # 知识积累者 - 完成5门课程
    if completed_count >= 5 and 'badge-4' not in current_badges:
        current_badges.append('badge-4')
        new_badges.append('badge-4')

    # 历史大师 - 完成所有课程(14门)
    if completed_count >= 14 and 'badge-5' not in current_badges:
        current_badges.append('badge-5')
        new_badges.append('badge-5')

    # 时间旅行者 - 学习时长达到600分钟
    total_study = stats.total_study_time or 0
    if total_study >= 600 and 'badge-6' not in current_badges:
        current_badges.append('badge-6')
        new_badges.append('badge-6')

    stats.badges = current_badges

    await db.commit()

    # 返回更详细的结果，包含勋章信息
    return {
        "message": f"Lesson {data.lesson_id} completed with score {data.score}",
        "success": True,
        "completed_lessons_count": completed_count,
        "new_badges": new_badges,
        "all_badges": current_badges
    }


@router.post("/submit-answer", response_model=MessageResponse)
async def submit_answer(
    data: AnswerSubmit,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """提交单个答案（可选，用于实时记录）"""
    # 验证课程和问题是否存在
    lesson = get_lesson_by_id(data.lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    # 找到问题并验证答案
    question = None
    for q in lesson.get("questions", []):
        if q["id"] == data.question_id:
            question = q
            break

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    is_correct = data.answer == question.get("correctAnswer")

    return MessageResponse(
        message="Answer submitted",
        success=is_correct
    )
