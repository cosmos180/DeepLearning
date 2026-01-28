#!/usr/bin/env python3
"""
Alert Checker Agent Tool
智能告警检查和分析的 Agent Tool
"""

import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import httpx
import nest_asyncio
import yaml

# 允许嵌套事件循环 (ADK 运行在已有事件循环中)
nest_asyncio.apply()

# 添加父目录到路径以导入 email_notifier
script_dir = Path(__file__).parent.parent.parent / "monitoring" / "scripts"
sys.path.insert(0, str(script_dir))

try:
    from email_notifier import EmailNotifier, EmailConfig
except ImportError:
    EmailNotifier = None
    EmailConfig = None


# ============================================================================
# 配置
# ============================================================================

ES_HOST = "172.26.2.88"
ES_PORT = 39202
ES_URL = f"http://{ES_HOST}:{ES_PORT}"

# 规则目录
RULES_DIR = Path(__file__).parent.parent.parent / "monitoring" / "alert_rules"


def _run_async(coro):
    """运行异步代码 (nest_asyncio 已启用)"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class AlertResult:
    """告警结果"""
    rule_name: str
    device_id: str
    field: str
    value: float
    threshold: float
    severity: str
    timestamp: str
    message: str


# ============================================================================
# Agent Tool Functions
# ============================================================================

def check_all_alerts(
    platform: str = None,
    severity: str = None,
) -> str:
    """
    检查所有告警规则

    Args:
        platform: 可选的平台过滤 (如 'sdc')
        severity: 可选的严重级别过滤 ('critical', 'warning', 'info')

    Returns:
        告警检查结果摘要
    """
    alerts = []

    # 加载所有规则
    for yaml_file in RULES_DIR.rglob("*.yaml"):
        try:
            rule = _load_rule(yaml_file)
            # 可选过滤
            if platform and platform not in rule.get("index", "").lower():
                continue
            if severity and rule.get("severity") != severity:
                continue

            # 检查规则
            rule_alerts = _check_single_rule(rule)
            alerts.extend(rule_alerts)
        except Exception:
            continue

    return _format_alerts_summary(alerts)


def check_alert_by_rule(
    rule_name: str,
) -> str:
    """
    检查指定的告警规则

    Args:
        rule_name: 规则名称 (如 'cache_info_json', 'disk_used_ratio')

    Returns:
        该规则的告警检查结果
    """
    # 查找规则文件
    rule_file = None
    for yaml_file in RULES_DIR.rglob("*.yaml"):
        if rule_name in yaml_file.stem:
            rule_file = yaml_file
            break

    if not rule_file:
        return f"❌ 未找到规则: {rule_name}"

    try:
        rule = _load_rule(rule_file)
        alerts = _check_single_rule(rule)
        return _format_alerts_summary(alerts, show_details=True)
    except Exception as e:
        return f"❌ 检查规则失败: {str(e)}"


def get_alert_rules(
    platform: str = None,
) -> str:
    """
    获取所有告警规则列表

    Args:
        platform: 可选的平台过滤

    Returns:
        规则列表
    """
    rules = []

    for yaml_file in RULES_DIR.rglob("*.yaml"):
        try:
            rule = _load_rule(yaml_file)
            if platform and platform not in rule.get("index", "").lower():
                continue

            rules.append({
                "name": rule.get("name", "Unnamed"),
                "file": yaml_file.name,
                "severity": rule.get("severity", "unknown"),
                "threshold": rule.get("alert", {}).get("threshold", "N/A"),
                "field": rule.get("alert", {}).get("field", "N/A"),
            })
        except Exception:
            continue

    lines = [f"📋 告警规则列表 ({len(rules)} 条)", f"{'='*60}"]
    for rule in rules:
        icon = "🔴" if rule["severity"] == "critical" else "🟡" if rule["severity"] == "warning" else "🔵"
        lines.append(
            f"{icon} {rule['name']}\n"
            f"   文件: {rule['file']}\n"
            f"   阈值: {rule['field']} {rule['threshold']}\n"
        )

    return "\n".join(lines)


def analyze_alert_trend(
    device_id: str,
    platform: str = "sdc",
    hours: int = 24,
) -> str:
    """
    分析设备的告警趋势

    Args:
        device_id: 设备 ID
        platform: 平台名称
        hours: 分析时间范围（小时）

    Returns:
        趋势分析结果
    """
    time_from = f"now-{hours}h"

    # 查询该设备的数据
    query = f'deviceId.keyword: "{device_id}" AND metrics.platform: "{platform}"'
    es_query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": query}},
                    {"range": {"@timestamp": {"gte": time_from, "lte": "now"}}},
                ]
            }
        },
        "aggs": {
            "time_buckets": {
                "date_histogram": {
                    "field": "@timestamp",
                    "fixed_interval": f"{hours}h" if hours <= 24 else "1d",
                },
                "aggs": {
                    "avg_cache_error": {
                        "avg": {"field": "metrics.cache_info.json"},
                    }
                },
            }
        },
    }

    url = f"{ES_URL}/tupu-metrics-production-tp_ipc-*/_search"

    async def _query():
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=es_query)
            response.raise_for_status()
            return response.json()

    try:
        # 处理异步调用
        results = _run_async(_query())
        buckets = results.get("aggregations", {}).get("time_buckets", {}).get("buckets", [])

        lines = [
            f"📈 告警趋势分析",
            f"{'='*60}",
            f"  设备: {device_id}",
            f"  平台: {platform}",
            f"  时间范围: 最近 {hours} 小时",
            f"{'='*60}",
        ]

        if not buckets:
            lines.append("\n⚠️ 该时间段内无数据")
        else:
            lines.append(f"\n时间点: {len(buckets)} 个")
            for bucket in buckets[:10]:
                ts = bucket.get("key_as_string", "N/A")
                doc_count = bucket.get("doc_count", 0)
                avg_val = bucket.get("avg_cache_error", {}).get("value", 0)
                lines.append(f"  {ts}: {doc_count} 条, 平均值: {avg_val:.2f}")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 趋势分析失败: {str(e)}"


def get_alert_suggestions(
    platform: str = "sdc",
) -> str:
    """
    获取告警优化建议

    Args:
        platform: 平台名称

    Returns:
        优化建议
    """
    suggestions = [
        "📊 告警优化建议",
        f"{'='*60}",
        "",
        "🔧 阈值调整:",
        "  - 定期回顾告警阈值，确保与实际业务匹配",
        "  - 考虑设置分级阈值 (warning/critical)",
        "",
        "⏰ 时间窗口:",
        "  - 根据业务周期调整检查频率",
        "  - 避免业务高峰期误报",
        "",
        "📧 通知配置:",
        "  - 配置邮件通知以便及时响应",
        "  - 考虑添加钉钉/企业微信通知",
        "",
        "📈 监控覆盖:",
        f"  - 当前 {platform} 平台覆盖: cache_info.json, disk_used_ratio",
        "  - 可添加更多指标监控 (CPU, 内存, 网络)",
    ]

    return "\n".join(suggestions)


# ============================================================================
# 内部辅助函数
# ============================================================================

def _load_rule(yaml_file: Path) -> Dict[str, Any]:
    """加载 YAML 规则"""
    with open(yaml_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def _build_aggregation_query(rule: Dict[str, Any]) -> Dict[str, Any]:
    """构建聚合查询 DSL"""
    alert_config = rule.get("alert", {})
    field = alert_config.get("field", "")
    agg_field = alert_config.get("aggregation_field", "deviceId.keyword")

    es_query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": rule.get("query", "*")}},
                    {"range": {"@timestamp": {"gte": rule.get("time_window", {}).get("range", "now-1h"), "lte": "now"}}},
                ]
            }
        },
        "aggs": {
            "by_device": {
                "terms": {"field": agg_field, "size": 1000},
                "aggs": {
                    "max_value": {"max": {"field": field}} if field != "_count" else {},
                    "latest_time": {"max": {"field": "@timestamp"}},
                },
            }
        },
    }

    if field == "_count":
        es_query["aggs"]["by_device"]["aggs"].pop("max_value", None)

    return es_query


async def _query_aggregation(rule: Dict[str, Any]) -> List[Dict]:
    """执行聚合查询"""
    es_query = await _build_aggregation_query(rule)
    url = f"{ES_URL}/{rule.get('index', 'tupu-metrics-production-tp_ipc-*')}/_search"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=es_query)
            response.raise_for_status()
            data = response.json()
            return data.get("aggregations", {}).get("by_device", {}).get("buckets", [])
        except httpx.HTTPError:
            return []


def _check_single_rule(rule: Dict[str, Any]) -> List[AlertResult]:
    """检查单个规则"""
    alerts = []

    # 处理异步调用
    buckets = _run_async(_query_aggregation(rule))

    alert_config = rule.get("alert", {})
    field = alert_config.get("field", "")
    threshold = alert_config.get("threshold", 0)
    threshold_type = alert_config.get("threshold_type", "greater_than")

    for bucket in buckets:
        device_id = bucket["key"]

        if field == "_count":
            value = bucket["doc_count"]
        else:
            value = bucket.get("max_value", {}).get("value", 0)
            if value is None:
                continue

        # 检查阈值
        triggered = False
        if threshold_type == "greater_than" and value > threshold:
            triggered = True
        elif threshold_type == "less_than" and value < threshold:
            triggered = True

        if triggered:
            latest_ts = bucket.get("latest_time", {}).get("value", 0)
            ts = datetime.fromtimestamp(latest_ts / 1000).isoformat() if latest_ts else datetime.now().isoformat()

            alerts.append(AlertResult(
                rule_name=rule.get("name", "Unnamed"),
                device_id=device_id,
                field=field,
                value=value,
                threshold=threshold,
                severity=rule.get("severity", "warning"),
                timestamp=ts,
                message=f"{rule.get('name')}: 设备 {device_id} = {value} (阈值: {threshold})",
            ))

    return alerts


def _format_alerts_summary(alerts: List[AlertResult], show_details: bool = False) -> str:
    """格式化告警摘要"""
    if not alerts:
        return "✅ 未触发告警"

    lines = [
        f"🚨 告警检查结果",
        f"{'='*60}",
        f"  总计: {len(alerts)} 条告警",
        f"  严重: {sum(1 for a in alerts if a.severity == 'critical')} 条",
        f"  警告: {sum(1 for a in alerts if a.severity == 'warning')} 条",
        f"{'='*60}",
    ]

    for alert in alerts[:20]:  # 最多显示 20 条
        icon = "🔴" if alert.severity == "critical" else "🟡"
        lines.append(
            f"\n{icon} {alert.rule_name}\n"
            f"   设备: {alert.device_id}\n"
            f"   值: {alert.value} (阈值: {alert.threshold})\n"
            f"   时间: {alert.timestamp}"
        )

    if len(alerts) > 20:
        lines.append(f"\n... 还有 {len(alerts) - 20} 条告警")

    return "\n".join(lines)


# 导出所有工具函数
__all__ = [
    "check_all_alerts",
    "check_alert_by_rule",
    "get_alert_rules",
    "analyze_alert_trend",
    "get_alert_suggestions",
]
