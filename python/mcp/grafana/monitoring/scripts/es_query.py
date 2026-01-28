#!/usr/bin/env python3
"""
Elasticsearch Query Tool
直接查询 ES 索引，支持自定义查询条件和时间范围
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx


# ES 配置
ES_HOST = "172.26.2.88"
ES_PORT = 39202
ES_URL = f"http://{ES_HOST}:{ES_PORT}"

# 默认索引
DEFAULT_INDEX = "tupu-metrics-production-tp_ipc-*"


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
                    {
                        "query_string": {
                            "query": query_string
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": time_from,
                                "lte": time_to
                            }
                        }
                    }
                ]
            }
        },
        "sort": [{"@timestamp": {"order": "desc"}}]
    }


def format_hit(hit: Dict[str, Any], index: int) -> str:
    """格式化单条查询结果"""
    source = hit.get("_source", {})
    timestamp = source.get("@timestamp", "N/A")
    device_id = source.get("deviceId", "N/A")
    platform = source.get("metrics", {}).get("platform", "N/A")

    lines = [
        f"\n{'='*60}",
        f"[{index}] Document ID: {hit.get('_id')}",
        f"{'='*60}",
        f"  Timestamp: {timestamp}",
        f"  Device ID: {device_id}",
        f"  Platform: {platform}",
    ]

    # 展开主要字段
    metrics = source.get("metrics", {})
    if metrics:
        lines.append(f"  Metrics:")
        for key, value in metrics.items():
            if key == "cache_info":
                lines.append(f"    {key}: {json.dumps(value, ensure_ascii=False)[:200]}")
            elif isinstance(value, (str, int, float, bool)):
                lines.append(f"    {key}: {value}")
            else:
                lines.append(f"    {key}: {json.dumps(value, ensure_ascii=False)[:100]}")

    return "\n".join(lines)


async def query_elasticsearch(
    query_string: str,
    index: str = DEFAULT_INDEX,
    time_from: str = "now-1h",
    time_to: str = "now",
    size: int = 100,
    explain: bool = False,
) -> Dict[str, Any]:
    """执行 ES 查询"""
    es_query = build_es_query(query_string, time_from, time_to, size)

    if explain:
        print(f"\n📋 Elasticsearch Query:")
        print(f"  URL: {ES_URL}/{index}/_search")
        print(f"  Query DSL:")
        print(json.dumps(es_query, indent=2, ensure_ascii=False))
        print()

    url = f"{ES_URL}/{index}/_search"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=es_query)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"❌ Error querying Elasticsearch: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            sys.exit(1)


def print_summary(results: Dict[str, Any], query_string: str, time_from: str, time_to: str):
    """打印查询摘要"""
    hits = results.get("hits", {}).get("hits", [])
    total = results.get("hits", {}).get("total", {}).get("value", 0)

    print(f"\n{'='*60}")
    print(f"🔍 Elasticsearch Query Results")
    print(f"{'='*60}")
    print(f"  Index:    {DEFAULT_INDEX}")
    print(f"  Query:    {query_string}")
    print(f"  Time:     {time_from} to {time_to}")
    print(f"  Total:    {total} hits")
    print(f"  Returned: {len(hits)} documents")
    print(f"{'='*60}")


def aggregate_by_device(hits: List[Dict]) -> Dict[str, int]:
    """按设备 ID 聚合统计"""
    device_counts = {}
    for hit in hits:
        source = hit.get("_source", {})
        device_id = source.get("deviceId", "unknown")
        device_counts[device_id] = device_counts.get(device_id, 0) + 1
    return device_counts


def print_aggregation(hits: List[Dict]):
    """打印聚合统计"""
    device_counts = aggregate_by_device(hits)

    if device_counts:
        print(f"\n📊 Aggregation by Device:")
        print(f"{'-'*60}")
        # 按数量排序
        sorted_devices = sorted(device_counts.items(), key=lambda x: x[1], reverse=True)
        for device_id, count in sorted_devices[:20]:  # 最多显示 20 个
            print(f"  {device_id}: {count} documents")
        if len(sorted_devices) > 20:
            print(f"  ... and {len(sorted_devices) - 20} more devices")


async def main():
    parser = argparse.ArgumentParser(
        description="Query Elasticsearch directly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 默认查询 (最近 1 小时)
  %(prog)s '(metrics.platform: "sdc") AND (metrics.cache_info.json)'

  # 指定时间范围
  %(prog)s '(metrics.platform: "sdc")' --time-from "now-24h" --time-to "now"

  # 显示完整 JSON
  %(prog)s '(metrics.platform: "sdc")' --json

  # 显示查询 DSL
  %(prog)s '(metrics.platform: "sdc")' --explain
        """
    )
    parser.add_argument(
        "query",
        help="Lucene query string (e.g., 'metrics.platform: \"sdc\"')"
    )
    parser.add_argument(
        "--index",
        default=DEFAULT_INDEX,
        help=f"Elasticsearch index pattern (default: {DEFAULT_INDEX})"
    )
    parser.add_argument(
        "--time-from",
        default="now-1h",
        help="Start time (default: now-1h)"
    )
    parser.add_argument(
        "--time-to",
        default="now",
        help="End time (default: now)"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=100,
        help="Maximum number of results (default: 100)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON"
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Show query DSL before executing"
    )
    parser.add_argument(
        "--aggregate",
        action="store_true",
        help="Show aggregation by device"
    )

    args = parser.parse_args()

    # 执行查询
    results = await query_elasticsearch(
        query_string=args.query,
        index=args.index,
        time_from=args.time_from,
        time_to=args.time_to,
        size=args.size,
        explain=args.explain,
    )

    # 输出结果
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        hits = results.get("hits", {}).get("hits", [])

        # 打印摘要
        print_summary(results, args.query, args.time_from, args.time_to)

        # 打印聚合
        if args.aggregate:
            print_aggregation(hits)

        # 打印详细结果 (最多 10 条)
        print(f"\n📄 Sample Documents (first 10):")
        for i, hit in enumerate(hits[:10]):
            print(format_hit(hit, i + 1))

        if len(hits) > 10:
            print(f"\n... and {len(hits) - 10} more documents (use --size to show more)")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
