"""
llm_client.py — LLM 调用客户端
封装 OpenAI 调用，支持流式输出、Token 统计和可观测性追踪
"""

import os
import time
from openai import AsyncOpenAI
from typing import Optional, AsyncGenerator

# 从环境变量读取默认模型
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4.1-mini")
FAST_MODEL = os.getenv("FAST_MODEL", "gpt-4.1-mini")

_client = AsyncOpenAI()


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = None,
    temperature: float = 0.8,
    max_tokens: int = 4000,
    stream: bool = False,
) -> tuple[str, int]:
    """
    调用 LLM 并返回 (content, token_count)
    model 路由策略：
      - 创意写作（高温）: 默认模型 (DEFAULT_MODEL)
      - 逻辑评审（低温）: 默认模型 (DEFAULT_MODEL)
      - 快速分类/摘要: 快速模型 (FAST_MODEL)
    """
    if model is None:
        model = DEFAULT_MODEL
    elif "gpt-4.1-nano" in model or "mini" in model:
        # 兼容旧代码传入的 "gpt-4.1-nano"
        model = FAST_MODEL

    start = time.time()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = await _client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content or ""
    tokens = response.usage.total_tokens if response.usage else 0
    return content, tokens


async def call_llm_stream(
    system_prompt: str,
    user_prompt: str,
    model: str = None,
    temperature: float = 0.8,
    max_tokens: int = 4000,
) -> AsyncGenerator[str, None]:
    """流式调用 LLM，逐 chunk 返回内容"""
    if model is None:
        model = DEFAULT_MODEL
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    stream = await _client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
