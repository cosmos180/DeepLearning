"""
llm_client.py — LLM 调用客户端
封装 OpenAI 调用，支持流式输出、Token 统计和可观测性追踪
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
import time
import httpx
from openai import AsyncOpenAI
from typing import Optional, AsyncGenerator

# 从环境变量读取默认模型
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4.1-mini")
FAST_MODEL = os.getenv("FAST_MODEL", "gpt-4.1-mini")

# Cherry Studio 配置
CHERRY_API_URL = os.getenv("CHERRY_API_URL", "http://127.0.0.1:23333/v1")
CHERRY_API_KEY = os.getenv("CHERRY_API_KEY", "")

# 代理配置（支持 HTTP_PROXY 或 HTTPS_PROXY）
proxy_url = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
http_client = None
if proxy_url:
    http_client = httpx.AsyncClient(proxy=proxy_url)

# OpenRouter Client (Default)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

_client = None
if OPENROUTER_API_KEY:
    _client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        max_retries=0,
        timeout=600.0,  # 增加到 10 分钟
        http_client=http_client
    )
else:
    # 兼容没有配置时的 fallback
    _client = AsyncOpenAI(
        max_retries=0,
        timeout=600.0,  # 增加到 10 分钟
        http_client=http_client
    )

# Cherry Studio 客户端
_cherry_client = None
if CHERRY_API_URL and CHERRY_API_KEY:
    _cherry_client = AsyncOpenAI(
        base_url=CHERRY_API_URL,
        api_key=CHERRY_API_KEY,
        max_retries=0,
        timeout=180.0  # 增加到 3 分钟
    )


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = None,
    temperature: float = 0.8,
    max_tokens: int = 4000,
    stream: bool = False,
    api_source: str = "openrouter",  # openrouter 或 cherry
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

    # 解析前端可能附带的自定义 provider 前缀
    if model and model.startswith("cherry/"):
        api_source = "cherry"
        model = model[7:]

    # 根据 api_source 选择客户端
    if api_source == "cherry" and _cherry_client:
        client = _cherry_client
        if "/" in model and ":" not in model:
            model = model.replace("/", ":")
    else:
        client = _client
        if ":" in model:
            model = model.replace(":", "/")

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0
        return content, tokens
    except Exception as e:
        import traceback
        error_msg = f"LLM Connection Error ({api_source} / {model}): {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise Exception(error_msg)


async def call_llm_stream(
    system_prompt: str,
    user_prompt: str,
    model: str = None,
    temperature: float = 0.8,
    max_tokens: int = 4000,
    api_source: str = "openrouter",
) -> AsyncGenerator[str, None]:
    """流式调用 LLM，逐 chunk 返回内容"""
    if model is None:
        model = DEFAULT_MODEL
    elif "gpt-4.1-nano" in model or "mini" in model:
        model = FAST_MODEL
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # 解析前端可能附带的自定义 provider 前缀
    if model and model.startswith("cherry/"):
        api_source = "cherry"
        model = model[7:]

    # 根据 api_source 选择客户端
    if api_source == "cherry" and _cherry_client:
        client = _cherry_client
        if "/" in model and ":" not in model:
            model = model.replace("/", ":")
    else:
        client = _client
        if ":" in model:
            model = model.replace(":", "/")

    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

    print(f"DEBUG [{api_source}/{model}]: stream generator started", flush=True)
    try:
        async for chunk in stream:
            try:
                if not getattr(chunk, "choices", None):
                    continue
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                # Some APIs expose reasoning_content as an attribute or in model_extra
                reasoning = getattr(delta, "reasoning_content", None)
                if not reasoning and hasattr(delta, "model_extra") and delta.model_extra:
                    reasoning = delta.model_extra.get("reasoning_content")

                if content:
                    yield content
                elif reasoning:
                    yield reasoning
            except Exception as e:
                print(f"DEBUG ERROR in chunk parsing: {e}, chunk={chunk}", flush=True)
    except Exception as e:
        print(f"DEBUG ERROR in async generator: {e}", flush=True)


async def get_cherry_models() -> list:
    """获取 Cherry Studio 可用模型列表"""
    if not _cherry_client:
        return []
    try:
        response = await _cherry_client.models.list()
        if not response or not response.data:
            return []
        models = []
        for m in response.data:
            # 格式化为 provider:model_id
            model_id = m.id
            # 简化显示名称
            name = m.name if hasattr(m, 'name') else model_id
            models.append({
                "value": model_id,
                "label": name
            })
        return models
    except Exception as e:
        print(f"获取 Cherry Studio 模型失败: {e}")
        return []
