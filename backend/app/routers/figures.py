"""
历史人物对话 API
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
from app.services.figures import get_figure_by_id, get_all_figures, HISTORICAL_FIGURES

router = APIRouter(prefix="/figures", tags=["figures"])


@router.get("")
async def list_figures():
    """获取所有历史人物列表"""
    return get_all_figures()


@router.get("/{figure_id}")
async def get_figure(figure_id: str):
    """获取单个历史人物详情"""
    figure = get_figure_by_id(figure_id)
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")

    # 不返回 systemPrompt
    return {
        "id": figure["id"],
        "name": figure["name"],
        "title": figure["title"],
        "era": figure["era"],
        "avatar": figure["avatar"],
        "description": figure["description"],
        "greeting": figure["greeting"]
    }


@router.post("/{figure_id}/chat/stream")
async def chat_with_figure_stream(
    figure_id: str,
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    与历史人物进行流式对话
    """
    figure = get_figure_by_id(figure_id)
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")

    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    async def generate():
        try:
            async for chunk in stream_chat_completion(
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                system_prompt=figure["systemPrompt"]
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/{figure_id}/history", response_model=ChatHistoryResponse | None)
async def get_figure_chat_history(
    figure_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取与特定历史人物的聊天历史"""
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .where(ChatHistory.figure_id == figure_id)
    )
    history = result.scalar_one_or_none()

    if not history:
        return None

    return history


@router.post("/{figure_id}/history/save", response_model=MessageResponse)
async def save_figure_chat_history(
    figure_id: str,
    messages: list[dict],
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """保存与历史人物的聊天历史"""
    # 验证人物存在
    figure = get_figure_by_id(figure_id)
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")

    # 查找现有记录
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .where(ChatHistory.figure_id == figure_id)
    )
    history = result.scalar_one_or_none()

    if history:
        history.messages = messages
    else:
        history = ChatHistory(
            user_id=current_user.id,
            figure_id=figure_id,
            messages=messages
        )
        db.add(history)

    await db.commit()
    return MessageResponse(message=f"Chat history with {figure['name']} saved")


@router.delete("/{figure_id}/history", response_model=MessageResponse)
async def clear_figure_chat_history(
    figure_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """清空与特定历史人物的聊天历史"""
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .where(ChatHistory.figure_id == figure_id)
    )
    history = result.scalar_one_or_none()

    if history:
        await db.delete(history)
        await db.commit()

    return MessageResponse(message="Chat history cleared")
