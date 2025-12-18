"""
课程和答题相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List

from app.database import get_db
from app.models import LessonProgress, UserStats
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


@router.post("/complete", response_model=MessageResponse)
async def complete_lesson(
    data: QuizResult,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """完成课程并记录成绩"""
    # 查找现有进度
    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == data.lesson_id
        )
    )
    progress = result.scalar_one_or_none()

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
            total_answers=data.total_count
        )
        db.add(stats)
    else:
        stats.correct_answers += data.correct_count
        stats.total_answers += data.total_count

    await db.commit()
    return MessageResponse(message=f"Lesson {data.lesson_id} completed with score {data.score}")


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
