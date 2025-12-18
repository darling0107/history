"""
好友和 PK 对战 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from datetime import datetime
from uuid import UUID
import random

from app.database import get_db
from app.models import UserProfile, Friendship, PKMatch, UserStats
from app.schemas import (
    FriendRequest,
    FriendResponse,
    PKStartRequest,
    PKAnswerSubmit,
    PKMatchResponse,
    MessageResponse
)
from app.utils import CurrentUser, get_current_user
from app.services.lessons import LESSONS

router = APIRouter(prefix="/social", tags=["social"])


# ============ 好友相关 ============

@router.get("/friends", response_model=list[FriendResponse])
async def get_friends(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取好友列表"""
    # 查询已接受的好友关系
    result = await db.execute(
        select(Friendship)
        .where(
            or_(
                Friendship.user_id == current_user.id,
                Friendship.friend_id == current_user.id
            )
        )
        .where(Friendship.status == "accepted")
    )
    friendships = result.scalars().all()

    # 获取好友的用户信息
    friends = []
    for friendship in friendships:
        # 确定好友ID
        friend_id = (
            friendship.friend_id
            if friendship.user_id == current_user.id
            else friendship.user_id
        )

        # 获取好友信息
        user_result = await db.execute(
            select(UserProfile).where(UserProfile.id == friend_id)
        )
        friend_user = user_result.scalar_one_or_none()

        if friend_user:
            friends.append(FriendResponse(
                id=friend_user.id,
                username=friend_user.username,
                avatar_url=friend_user.avatar_url,
                status="offline"  # 简化处理，实际可以用 Redis 追踪在线状态
            ))

    return friends


@router.post("/friends/request", response_model=MessageResponse)
async def send_friend_request(
    request: FriendRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """发送好友请求"""
    if request.friend_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add yourself as friend"
        )

    # 检查是否已经是好友或有待处理请求
    result = await db.execute(
        select(Friendship)
        .where(
            or_(
                and_(
                    Friendship.user_id == current_user.id,
                    Friendship.friend_id == request.friend_id
                ),
                and_(
                    Friendship.user_id == request.friend_id,
                    Friendship.friend_id == current_user.id
                )
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        if existing.status == "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already friends"
            )
        elif existing.status == "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Friend request already pending"
            )

    # 创建好友请求
    friendship = Friendship(
        user_id=current_user.id,
        friend_id=request.friend_id,
        status="pending"
    )
    db.add(friendship)
    await db.commit()

    return MessageResponse(message="Friend request sent")


@router.get("/friends/requests", response_model=list[dict])
async def get_friend_requests(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取收到的好友请求"""
    result = await db.execute(
        select(Friendship)
        .where(Friendship.friend_id == current_user.id)
        .where(Friendship.status == "pending")
    )
    requests = result.scalars().all()

    # 获取请求者信息
    request_list = []
    for req in requests:
        user_result = await db.execute(
            select(UserProfile).where(UserProfile.id == req.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            request_list.append({
                "id": str(req.id),
                "from_user": {
                    "id": str(user.id),
                    "username": user.username,
                    "avatar_url": user.avatar_url
                },
                "created_at": req.created_at.isoformat()
            })

    return request_list


@router.post("/friends/accept/{request_id}", response_model=MessageResponse)
async def accept_friend_request(
    request_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """接受好友请求"""
    result = await db.execute(
        select(Friendship)
        .where(Friendship.id == request_id)
        .where(Friendship.friend_id == current_user.id)
        .where(Friendship.status == "pending")
    )
    friendship = result.scalar_one_or_none()

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )

    friendship.status = "accepted"
    await db.commit()

    return MessageResponse(message="Friend request accepted")


@router.delete("/friends/{friend_id}", response_model=MessageResponse)
async def remove_friend(
    friend_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除好友"""
    result = await db.execute(
        select(Friendship)
        .where(
            or_(
                and_(
                    Friendship.user_id == current_user.id,
                    Friendship.friend_id == friend_id
                ),
                and_(
                    Friendship.user_id == friend_id,
                    Friendship.friend_id == current_user.id
                )
            )
        )
    )
    friendship = result.scalar_one_or_none()

    if friendship:
        await db.delete(friendship)
        await db.commit()

    return MessageResponse(message="Friend removed")


# ============ PK 对战相关 ============

def generate_pk_questions(count: int = 5) -> list[dict]:
    """生成PK题目"""
    all_questions = []
    for lesson in LESSONS:
        for q in lesson.get("questions", []):
            all_questions.append({
                "id": q["id"],
                "content": q["content"],
                "options": q["options"],
                "correctAnswer": q["correctAnswer"],
                "lessonTitle": lesson["title"]
            })

    # 随机选择题目
    return random.sample(all_questions, min(count, len(all_questions)))


@router.post("/pk/start", response_model=PKMatchResponse)
async def start_pk_match(
    request: PKStartRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """开始PK对战"""
    # 验证对手存在
    result = await db.execute(
        select(UserProfile).where(UserProfile.id == request.opponent_id)
    )
    opponent = result.scalar_one_or_none()

    if not opponent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opponent not found"
        )

    # 生成题目
    questions = generate_pk_questions(5)

    # 创建对战记录
    match = PKMatch(
        user1_id=current_user.id,
        user2_id=request.opponent_id,
        questions=questions,
        status="ongoing"
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)

    return PKMatchResponse(
        id=match.id,
        opponent_id=request.opponent_id,
        opponent_name=opponent.username,
        my_score=0,
        opponent_score=0,
        status="ongoing",
        questions=questions,
        current_question=0
    )


@router.post("/pk/answer", response_model=dict)
async def submit_pk_answer(
    data: PKAnswerSubmit,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """提交PK答案"""
    result = await db.execute(
        select(PKMatch).where(PKMatch.id == data.match_id)
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    if match.status != "ongoing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match already completed"
        )

    # 验证用户是参与者
    is_user1 = match.user1_id == current_user.id
    is_user2 = match.user2_id == current_user.id

    if not (is_user1 or is_user2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this match"
        )

    # 获取题目并验证答案
    questions = match.questions
    if data.question_index >= len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question index"
        )

    question = questions[data.question_index]
    is_correct = data.answer == question["correctAnswer"]

    # 更新分数
    if is_correct:
        if is_user1:
            match.user1_score += 1
        else:
            match.user2_score += 1

    # 模拟对手答题（简单AI）
    opponent_correct = random.random() < 0.6  # 60% 正确率
    if opponent_correct:
        if is_user1:
            match.user2_score += 1
        else:
            match.user1_score += 1

    await db.commit()

    return {
        "is_correct": is_correct,
        "correct_answer": question["correctAnswer"],
        "my_score": match.user1_score if is_user1 else match.user2_score,
        "opponent_score": match.user2_score if is_user1 else match.user1_score,
        "opponent_correct": opponent_correct
    }


@router.post("/pk/{match_id}/finish", response_model=dict)
async def finish_pk_match(
    match_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """结束PK对战"""
    result = await db.execute(
        select(PKMatch).where(PKMatch.id == match_id)
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    # 确定胜者
    if match.user1_score > match.user2_score:
        match.winner_id = match.user1_id
    elif match.user2_score > match.user1_score:
        match.winner_id = match.user2_id
    else:
        match.winner_id = None  # 平局

    match.status = "completed"
    match.completed_at = datetime.utcnow()

    await db.commit()

    # 判断当前用户是否获胜
    is_user1 = match.user1_id == current_user.id
    my_score = match.user1_score if is_user1 else match.user2_score
    opponent_score = match.user2_score if is_user1 else match.user1_score

    result_status = "win" if match.winner_id == current_user.id else (
        "lose" if match.winner_id else "draw"
    )

    return {
        "status": result_status,
        "my_score": my_score,
        "opponent_score": opponent_score,
        "winner_id": str(match.winner_id) if match.winner_id else None
    }


@router.get("/pk/history", response_model=list[dict])
async def get_pk_history(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取PK对战历史"""
    result = await db.execute(
        select(PKMatch)
        .where(
            or_(
                PKMatch.user1_id == current_user.id,
                PKMatch.user2_id == current_user.id
            )
        )
        .where(PKMatch.status == "completed")
        .order_by(PKMatch.completed_at.desc())
        .limit(20)
    )
    matches = result.scalars().all()

    history = []
    for match in matches:
        is_user1 = match.user1_id == current_user.id
        opponent_id = match.user2_id if is_user1 else match.user1_id

        # 获取对手信息
        user_result = await db.execute(
            select(UserProfile).where(UserProfile.id == opponent_id)
        )
        opponent = user_result.scalar_one_or_none()

        result_status = "win" if match.winner_id == current_user.id else (
            "lose" if match.winner_id else "draw"
        )

        history.append({
            "id": str(match.id),
            "opponent": {
                "id": str(opponent_id),
                "username": opponent.username if opponent else "Unknown"
            },
            "my_score": match.user1_score if is_user1 else match.user2_score,
            "opponent_score": match.user2_score if is_user1 else match.user1_score,
            "result": result_status,
            "completed_at": match.completed_at.isoformat() if match.completed_at else None
        })

    return history
