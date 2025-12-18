"""
AI 聊天服务 - DeepSeek API
支持流式响应
"""
import httpx
from typing import AsyncGenerator, List
from app.config import get_settings

settings = get_settings()


async def stream_chat_completion(
    messages: List[dict],
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    system_prompt: str | None = None
) -> AsyncGenerator[str, None]:
    """
    流式聊天完成

    Args:
        messages: 消息列表 [{"role": "user", "content": "..."}]
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大token数
        system_prompt: 系统提示（可选）

    Yields:
        str: 增量文本内容
    """
    # 构建消息列表
    full_messages = []

    # 添加系统提示
    if system_prompt:
        full_messages.append({
            "role": "system",
            "content": system_prompt
        })
    else:
        full_messages.append({
            "role": "system",
            "content": "你是一位知识渊博的历史助手，擅长用生动有趣的方式讲解历史知识。"
        })

    # 添加用户消息
    full_messages.extend(messages)

    # 请求体
    payload = {
        "model": model,
        "messages": full_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }

    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            f"{settings.deepseek_base_url}/chat/completions",
            json=payload,
            headers=headers
        ) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                raise Exception(f"API Error: {response.status_code} - {error_text.decode()}")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # 去掉 "data: " 前缀

                    if data == "[DONE]":
                        break

                    try:
                        import json
                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")

                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue


async def chat_completion(
    messages: List[dict],
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    system_prompt: str | None = None
) -> str:
    """
    非流式聊天完成（返回完整响应）
    """
    full_content = ""
    async for chunk in stream_chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt
    ):
        full_content += chunk

    return full_content
