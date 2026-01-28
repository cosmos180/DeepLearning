#!/usr/bin/env python3
"""
Elasticsearch Agent Tool
支持自然语言查询 Elasticsearch 的 Agent Tool
"""

import asyncio
import json
from typing import Any, Dict

import httpx
import nest_asyncio

# 允许嵌套事件循环 (ADK 运行在已有事件循环中)
nest_asyncio.apply()


# ES 配置
ES_HOST = "172.26.2.88"
ES_PORT = 39202
ES_URL = f"http://{ES_HOST}:{ES_PORT}"
DEFAULT_INDEX = "tupu-metrics-production-tp_ipc-*"


def _run_async(coro):
    """运行异步代码 (nest_asyncio 已启用)"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


def build_es_query(
    query_string: str,
    time_from: str = "now-1h",
    time_to: str = "now",
    size: int = 100,
) -> Dict[str, Any]:
    """构建 ES 查询 DSL"""
    return {
        "size": size,
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": query_string}},
                    {"range": {"@timestamp": {"gte": time_from, "lte": time_to}}},
                ]
            }
        },
        "sort": [{"@timestamp": {"order": "desc"}}],
    }


async def query_elasticsearch(
    query_string: str,
    index: str = DEFAULT_INDEX,
    time_from: str = "now-1h",
    time_to: str = "now",
    size: int = 100,
) -> Dict[str, Any]:
    """执行 ES 查询 (异步)"""
    es_query = build_es_query(query_string, time_from, time_to, size)
    url = f"{ES_URL}/{index}/_search"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=es_query)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "message": f"Failed to query Elasticsearch: {str(e)}",
            }


def format_es_results(results: Dict[str, Any], query: str = None, time_from: str = None, time_to: str = "now") -> str:
    """格式化 ES 查询结果为可读文本"""
    if "error" in results:
        return f"❌ 查询失败: {results.get('message', 'Unknown error')}"

    hits = results.get("hits", {}).get("hits", [])
    total = results.get("hits", {}).get("total", {}).get("value", 0)

    lines = [
        f"🔍 Elasticsearch 查询结果",
        f"{'='*60}",
    ]

    # 添加搜索条件
    if query:
        lines.append(f"  查询条件: {query}")
    if time_from:
        lines.append(f"  时间范围: {time_from} ~ {time_to}")
    lines.append(f"{'='*60}")
    lines.append(f"  总命中: {total} 条")
    lines.append(f"  返回: {len(hits)} 条文档")
    lines.append(f"{'='*60}")

    # 按设备聚合统计
    device_counts = {}
    for hit in hits:
        source = hit.get("_source", {})
        device_id = source.get("deviceId", "unknown")
        device_counts[device_id] = device_counts.get(device_id, 0) + 1

    if device_counts:
        lines.append(f"\n📊 按设备聚合统计:")
        sorted_devices = sorted(device_counts.items(), key=lambda x: x[1], reverse=True)
        for device_id, count in sorted_devices[:10]:
            lines.append(f"  {device_id}: {count} 条")

    # 显示前 5 条详细文档
    lines.append(f"\n📄 详细文档 (前 5 条):")
    for i, hit in enumerate(hits[:5]):
        source = hit.get("_source", {})
        timestamp = source.get("@timestamp", "N/A")
        device_id = source.get("deviceId", "N/A")
        metrics = source.get("metrics", {})

        lines.append(f"\n[{i+1}] 设备: {device_id}")
        lines.append(f"    时间: {timestamp}")
        lines.append(f"    指标: {json.dumps(metrics, ensure_ascii=False)[:200]}")

    return "\n".join(lines)


# ============================================================================
# Agent Tool Functions (同步包装器)
# ============================================================================

def search_es_by_platform(
    platform: str,
    time_range: str = "1h",
) -> str:
    """
    搜索指定平台的 Elasticsearch 数据

    Args:
        platform: 平台名称，如 'sdc', 'ipc'
        time_range: 时间范围，如 '1h', '24h', '7d', 'today'

    Returns:
        格式化的查询结果
    """
    # 解析时间范围
    if time_range == "today":
        time_from = "now/d"
    else:
        time_from = f"now-{time_range}"

    # 构建查询
    query = f'metrics.platform: "{platform}"'

    results = _run_async(query_elasticsearch(
        query_string=query,
        time_from=time_from,
        size=50,
    ))

    return format_es_results(results, query=query, time_from=time_from)


def search_es_by_device(
    device_id: str,
    platform: str = None,
    time_range: str = "24h",
) -> str:
    """
    搜索指定设备的 Elasticsearch 数据

    Args:
        device_id: 设备 ID
        platform: 可选的平台过滤
        time_range: 时间范围，如 '24h', 'today'

    Returns:
        格式化的查询结果
    """
    if time_range == "today":
        time_from = "now/d"
    else:
        time_from = f"now-{time_range}"

    # 构建查询
    if platform:
        query = f'deviceId: "{device_id}" AND metrics.platform: "{platform}"'
    else:
        query = f'deviceId: "{device_id}"'

    results = _run_async(query_elasticsearch(
        query_string=query,
        time_from=time_from,
        size=100,
    ))

    return format_es_results(results, query=query, time_from=time_from)


def search_es_by_metric(
    metric_name: str,
    platform: str = None,
    min_value: float = None,
    time_range: str = "24h",
) -> str:
    """
    搜索指定指标的数据

    Args:
        metric_name: 指标名称，如 'cache_info.json', 'disk.used_ratio'
        platform: 可选的平台过滤
        min_value: 可选的最小值过滤
        time_range: 时间范围，如 '24h', 'today'

    Returns:
        格式化的查询结果
    """
    if time_range == "today":
        time_from = "now/d"
    else:
        time_from = f"now-{time_range}"

    # 构建 Lucene 查询
    if "." in metric_name:
        query_parts = [f'metrics.{metric_name}:[* TO *]']
    else:
        query_parts = [f'metrics.{metric_name}:[* TO *]']

    if platform:
        query_parts.append(f'metrics.platform: "{platform}"')

    query = " AND ".join(query_parts)

    results = _run_async(query_elasticsearch(
        query_string=query,
        time_from=time_from,
        size=100,
    ))

    return format_es_results(results, query=query, time_from=time_from)


def search_es_custom(
    lucene_query: str,
    time_range: str = "1h",
    size: int = 100,
) -> str:
    """
    使用自定义 Lucene 查询语法搜索 Elasticsearch

    Args:
        lucene_query: Lucene 查询字符串
        time_range: 时间范围，如 '1h', '24h', 'today'
        size: 返回结果数量

    Returns:
        格式化的查询结果
    """
    if time_range == "today":
        time_from = "now/d"
    else:
        time_from = f"now-{time_range}"

    results = _run_async(query_elasticsearch(
        query_string=lucene_query,
        time_from=time_from,
        size=size,
    ))

    return format_es_results(results, query=lucene_query, time_from=time_from)


def get_es_summary(
    platform: str = None,
    time_range: str = "24h",
) -> str:
    """
    获取 Elasticsearch 数据摘要

    Args:
        platform: 可选的平台过滤
        time_range: 时间范围，如 '24h', 'today'

    Returns:
        数据摘要信息
    """
    if time_range == "today":
        time_from = "now/d"
    else:
        time_from = f"now-{time_range}"

    if platform:
        query = f'metrics.platform: "{platform}"'
    else:
        query = "*"

    results = _run_async(query_elasticsearch(
        query_string=query,
        time_from=time_from,
        size=0,
    ))

    if "error" in results:
        return f"❌ 查询失败: {results.get('message', 'Unknown error')}"

    total = results.get("hits", {}).get("total", {}).get("value", 0)

    lines = [
        f"📊 Elasticsearch 数据摘要",
        f"{'='*60}",
        f"  查询条件: {query}",
        f"  时间范围: {time_from}",
        f"  平台: {platform or '全部'}",
        f"  文档总数: {total:,} 条",
    ]

    if total > 0:
        lines.append(f"\n💡 提示: 使用 search_es_by_platform 查看详细数据")

    return "\n".join(lines)


# 导出所有工具函数
__all__ = [
    "search_es_by_platform",
    "search_es_by_device",
    "search_es_by_metric",
    "search_es_custom",
    "get_es_summary",
]
