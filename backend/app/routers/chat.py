"""
AI 聊天相关 API
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.database import get_db
from app.models import ChatHistory
from app.schemas import ChatRequest, ChatHistoryResponse, MessageResponse
from app.utils import CurrentUser, get_current_user
from app.services.ai import stream_chat_completion

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    流式聊天 API
    返回 Server-Sent Events (SSE) 格式的流式响应
    """
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    async def generate():
        try:
            async for chunk in stream_chat_completion(
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                # SSE 格式
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            # 发送结束标记
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
        }
    )


@router.post("/complete", response_model=MessageResponse)
async def chat_complete(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    非流式聊天 API（返回完整响应）
    """
    from app.services.ai import chat_completion

    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    try:
        response = await chat_completion(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return MessageResponse(message=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=list[ChatHistoryResponse])
async def get_chat_history(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的聊天历史"""
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .where(ChatHistory.figure_id.is_(None))  # 普通聊天，非历史人物
        .order_by(ChatHistory.updated_at.desc())
    )
    histories = result.scalars().all()
    return histories


@router.post("/history/save", response_model=MessageResponse)
async def save_chat_history(
    messages: list[dict],
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """保存聊天历史"""
    # 查找现有记录
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .where(ChatHistory.figure_id.is_(None))
    )
    history = result.scalar_one_or_none()

    if history:
        history.messages = messages
    else:
        history = ChatHistory(
            user_id=current_user.id,
            messages=messages
        )
        db.add(history)

    await db.commit()
    return MessageResponse(message="Chat history saved")


@router.delete("/history", response_model=MessageResponse)
async def clear_chat_history(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """清空聊天历史"""
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .where(ChatHistory.figure_id.is_(None))
    )
    history = result.scalar_one_or_none()

    if history:
        await db.delete(history)
        await db.commit()

    return MessageResponse(message="Chat history cleared")
