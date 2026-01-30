#!/usr/bin/env python3
"""
Elasticsearch Agent Tool
支持自然语言查询 Elasticsearch 的 Agent Tool
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
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

# 北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))


# ============================================================================
# 北京时间辅助函数
# ============================================================================

def get_beijing_time() -> datetime:
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)


def format_beijing_time(dt: datetime = None, format_type: str = "iso") -> str:
    """
    格式化北京时间为字符串

    Args:
        dt: 时间对象，默认为当前北京时间
        format_type: 格式类型 ('iso', 'readable', 'date', 'time')

    Returns:
        格式化后的时间字符串
    """
    if dt is None:
        dt = get_beijing_time()

    if format_type == "iso":
        return dt.isoformat()
    elif format_type == "readable":
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "date":
        return dt.strftime("%Y-%m-%d")
    elif format_type == "time":
        return dt.strftime("%H:%M:%S")
    else:
        return dt.isoformat()


def get_beijing_time_str() -> str:
    """获取当前北京时间字符串（可读格式）"""
    return format_beijing_time(get_beijing_time(), "readable")


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


async def query_elasticsearch_aggregation(
    query_string: str,
    agg_field: str,
    index: str = DEFAULT_INDEX,
    time_from: str = "now-1h",
    time_to: str = "now",
    agg_size: int = 100,  # 聚合返回的唯一值数量
) -> Dict[str, Any]:
    """
    执行 ES 聚合查询 (异步)

    使用 terms aggregation 统计字段的所有唯一值及其数量

    Args:
        query_string: Lucene 查询字符串
        agg_field: 要聚合的字段名 (如 'metrics.payload.code', 'metrics.msg')
        index: ES 索引
        time_from: 开始时间
        time_to: 结束时间
        agg_size: 返回的唯一值数量 (默认 100，可设为更大获取更多)

    Returns:
        包含聚合结果的 JSON
    """
    es_query = {
        "size": 0,  # 不返回具体文档，只返回聚合结果
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": query_string}},
                    {"range": {"@timestamp": {"gte": time_from, "lte": time_to}}},
                ]
            }
        },
        "aggs": {
            "field_values": {
                "terms": {
                    "field": agg_field,
                    "size": agg_size,
                }
            }
        },
    }

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


def format_aggregation_results(
    results: Dict[str, Any],
    query: str = None,
    agg_field: str = None,
    time_from: str = None,
    time_to: str = "now",
) -> str:
    """
    格式化 ES 聚合查询结果为固定格式的文本

    返回格式固定为：
    ```
    📊 字段统计结果
    ============================================================
    查询条件: metrics.msg: "uploadTrack" AND metrics.msg: "reason"
    统计字段: metrics.payload.code
    时间范围: now/d ~ now
    ============================================================
    总命中: 1,234 条
    唯一值数量: 15 种
    ============================================================

    📌 错误类型统计 (按数量降序):
    ┌─────────────┬────────┬────────┐
    │ 错误代码    │ 数量   │ 占比   │
    ├─────────────┼────────┼────────┤
    │ 502         │ 456    │ 36.9%  │
    │ 401         │ 234    │ 19.0%  │
    │ 404         │ 123    │ 10.0%  │
    └─────────────┴────────┴────────┘
    ```
    """
    if "error" in results:
        return f"❌ 查询失败: {results.get('message', 'Unknown error')}"

    total = results.get("hits", {}).get("total", {}).get("value", 0)
    buckets = results.get("aggregations", {}).get("field_values", {}).get("buckets", [])

    lines = [
        f"📊 字段统计结果",
        f"{'='*60}",
    ]

    # 添加搜索条件
    if query:
        lines.append(f"查询条件: {query}")
    if agg_field:
        lines.append(f"统计字段: {agg_field}")
    if time_from:
        lines.append(f"时间范围: {time_from} ~ {time_to}")
    lines.append(f"{'='*60}")
    lines.append(f"总命中: {total:,} 条")
    lines.append(f"唯一值数量: {len(buckets)} 种")
    lines.append(f"{'='*60}")

    if not buckets:
        lines.append("\n⚠️ 未找到匹配数据")
        return "\n".join(lines)

    # 计算百分比
    lines.append(f"\n📌 字段值统计 (按数量降序):")
    lines.append(f"┌{'─'*40}┬{'─'*10}┬{'─'*10}┐")

    # 确定表头宽度
    max_value_width = max(20, max(len(str(bucket.get("key", "N/A"))) for bucket in buckets[:20]))

    header = f"│ {'字段值':<{max_value_width}} │ {'数量':>8} │ {'占比':>8} │"
    lines.append(header)
    lines.append(f"├{'─'*40}┼{'─'*10}┼{'─'*10}┤")

    for bucket in buckets[:50]:  # 最多显示 50 个唯一值
        key = bucket.get("key", "N/A")
        count = bucket.get("doc_count", 0)
        percent = (count / total * 100) if total > 0 else 0

        # 截断过长的 key
        display_key = str(key)[:max_value_width] if len(str(key)) > max_value_width else str(key)

        lines.append(f"│ {display_key:<{max_value_width}} │ {count:>8} │ {percent:>7.1f}% │")

    lines.append(f"└{'─'*40}┴{'─'*10}┴{'─'*10}┘")

    if len(buckets) > 50:
        lines.append(f"\n... 还有 {len(buckets) - 50} 种唯一值未显示")

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


def search_es_aggregation(
    lucene_query: str,
    agg_field: str,
    time_range: str = "24h",
    agg_size: int = 100,
) -> str:
    """
    使用聚合查询统计字段的所有唯一值及其数量

    与 search_es_custom 不同，此工具使用 ES 的聚合功能，可以：
    - 获取字段的所有唯一值（不受 size 限制）
    - 统计每个唯一值的出现次数
    - 以固定格式返回结果

    适用场景：
    - "查询今天 metrics.msg: 'uploadTrack' 的告警中，有哪些错误类型？"
    - "统计 metrics.payload.code 字段的所有可能值"
    - "按错误码统计数量"

    Args:
        lucene_query: Lucene 查询字符串，如 'metrics.msg: "uploadTrack" AND metrics.msg: "reason"'
        agg_field: 要统计的字段名，如 'metrics.payload.code', 'metrics.platform'
        time_range: 时间范围，如 '1h', '24h', 'today'
        agg_size: 返回的唯一值数量（默认 100，可设为更大如 500）

    Returns:
        固定格式的统计结果（表格形式）

    示例:
        search_es_aggregation(
            lucene_query='metrics.msg: "uploadTrack" AND metrics.msg: "reason"',
            agg_field='metrics.payload.code',
            time_range='today',
            agg_size=100
        )
    """
    # 解析时间范围
    if time_range == "today":
        time_from = "now/d"
    else:
        time_from = f"now-{time_range}"

    # 执行聚合查询
    results = _run_async(query_elasticsearch_aggregation(
        query_string=lucene_query,
        agg_field=agg_field,
        time_from=time_from,
        agg_size=agg_size,
    ))

    return format_aggregation_results(
        results,
        query=lucene_query,
        agg_field=agg_field,
        time_from=time_from,
    )


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


def get_current_beijing_time(format_type: str = "readable") -> str:
    """
    获取当前北京时间

    Args:
        format_type: 时间格式类型
            - "iso": ISO 8601 格式 (如 2026-01-29T18:30:45+08:00)
            - "readable": 可读格式 (如 2026-01-29 18:30:45)
            - "date": 日期格式 (如 2026-01-29)
            - "time": 时间格式 (如 18:30:45)

    Returns:
        格式化后的北京时间字符串

    示例:
        get_current_beijing_time() -> "2026-01-29 18:30:45"
        get_current_beijing_time("iso") -> "2026-01-29T18:30:45+08:00"
        get_current_beijing_time("date") -> "2026-01-29"
    """
    now = get_beijing_time()
    return format_beijing_time(now, format_type)


# 导出所有工具函数
__all__ = [
    "search_es_by_platform",
    "search_es_by_device",
    "search_es_by_metric",
    "search_es_custom",
    "search_es_aggregation",  # 新增：聚合查询统计
    "get_es_summary",
    "get_current_beijing_time",  # 获取当前北京时间
]
