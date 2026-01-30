#!/usr/bin/env python3
"""
Alert Checker Agent Tool
智能告警检查和分析的 Agent Tool

集成 Tupu BI MCP - 获取告警设备的基本配置信息
"""

import asyncio
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import nest_asyncio
import yaml

# 允许嵌套事件循环 (ADK 运行在已有事件循环中)
nest_asyncio.apply()

# 添加父目录到路径以导入 email_notifier
script_dir = Path(__file__).parent.parent.parent / "monitoring" / "scripts"
sys.path.insert(0, str(script_dir))

# 添加 tupu_bi 模块路径
tupu_bi_path = Path(__file__).parent.parent.parent.parent / "mcp" / "tupu" / "bi"
if tupu_bi_path.exists():
    sys.path.insert(0, str(tupu_bi_path))

try:
    from email_notifier import EmailNotifier, EmailConfig
except ImportError:
    EmailNotifier = None
    EmailConfig = None

try:
    from tupu_bi.client import TupuBiClient
    TUPI_BI_AVAILABLE = True
except ImportError:
    TupuBiClient = None
    TUPI_BI_AVAILABLE = False


# ============================================================================
# 配置
# ============================================================================

ES_HOST = "172.26.2.88"
ES_PORT = 39202
ES_URL = f"http://{ES_HOST}:{ES_PORT}"

# 规则目录
RULES_DIR = Path(__file__).parent.parent.parent / "monitoring" / "alert_rules"

# Tupu BI API 配置
TUPI_BI_API_BASE = os.getenv("TUPI_BI_API_BASE", "https://api.bi.tuputech.com")
TUPI_BI_AUTH_SECRET = os.getenv("TUPI_BI_AUTH_SECRET", "")
TUPI_BI_TOKEN_ID = os.getenv("TUPI_BI_TOKEN_ID", "")


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
    camera_config: Dict[str, Any] = field(default_factory=dict)
    customer_info: Dict[str, Any] = field(default_factory=dict)
    store_info: Dict[str, Any] = field(default_factory=dict)
    device_full_info: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Agent Tool Functions
# ============================================================================

def check_all_alerts(
    platform: str = None,
    severity: str = None,
    enrich_with_camera_config: bool = False,
) -> str:
    """
    检查所有告警规则

    Args:
        platform: 可选的平台过滤 (如 'sdc')
        severity: 可选的严重级别过滤 ('critical', 'warning', 'info')
        enrich_with_camera_config: 是否补充摄像头配置信息 (需要 Tupu BI API)

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

    # 补充摄像头配置信息
    if enrich_with_camera_config and alerts and TUPI_BI_AVAILABLE:
        _enrich_alerts_with_camera_config(alerts)

    return _format_alerts_summary(alerts)


def check_alert_by_rule(
    rule_name: str,
    enrich_with_camera_config: bool = False,
) -> str:
    """
    检查指定的告警规则

    Args:
        rule_name: 规则名称 (如 'cache_info_json', 'disk_used_ratio')
        enrich_with_camera_config: 是否补充摄像头配置信息 (需要 Tupu BI API)

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

        # 补充摄像头配置信息
        if enrich_with_camera_config and alerts and TUPI_BI_AVAILABLE:
            _enrich_alerts_with_camera_config(alerts)

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


def get_camera_config(
    device_id: str,
) -> str:
    """
    获取摄像头基本参数配置（独立工具）

    Args:
        device_id: 设备标识符，支持 MAC 地址（如 a8:3f:a1:30:16:fb）或序列号（如 6AB2F0C3E97DD45610FE4C45EA1E71B1）

    Returns:
        摄像头配置信息
    """
    if not TUPI_BI_AVAILABLE:
        return "❌ Tupu BI 客户端不可用，请确保 tupu_bi 模块已正确安装"

    try:
        client = TupuBiClient(base_url=TUPI_BI_API_BASE)
        result = _run_async(client.get_camera_config(device_id))

        lines = [
            f"📹 摄像头配置信息",
            f"{'='*60}",
            f"  设备 ID: {device_id}",
            f"{'='*60}",
        ]

        # 格式化返回的配置信息
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, dict):
                    lines.append(f"\n🔹 {key}:")
                    for k, v in value.items():
                        lines.append(f"    {k}: {v}")
                else:
                    lines.append(f"  {key}: {value}")
        else:
            lines.append(f"\n{result}")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 获取摄像头配置失败: {str(e)}"


def get_device_full_info(
    device_id: str,
    token_id: str = None,
    secret: str = None,
) -> str:
    """
    获取设备完整信息（整合接口）- 包含摄像头配置、客户信息、门店信息

    此工具自动完成以下流程：
    1. 获取摄像头配置（包含 UID 和 SID）
    2. 获取认证 Token
    3. 获取客户信息
    4. 获取门店信息

    Args:
        device_id: 设备标识符，支持 MAC 地址（如 a8:3f:a1:30:16:fb）或序列号（如 6AB2F0C3E97DD45610FE4C45EA1E71B1）
        token_id: Token ID（用于获取认证 Token，如不提供则使用环境变量 TUPI_BI_TOKEN_ID）
        secret: 认证密钥（如不提供则使用环境变量 TUPI_BI_AUTH_SECRET）

    Returns:
        设备完整信息，包含摄像头配置、客户信息、门店信息

    环境变量:
        TUPI_BI_TOKEN_ID: 默认 Token ID
        TUPI_BI_AUTH_SECRET: 认证密钥（推荐使用环境变量）
    """
    if not TUPI_BI_AVAILABLE:
        return "❌ Tupu BI 客户端不可用，请确保 tupu_bi 模块已正确安装"

    # 使用环境变量作为默认值
    token_id = token_id or TUPI_BI_TOKEN_ID
    secret = secret or TUPI_BI_AUTH_SECRET

    if not token_id:
        return "❌ 缺少 token_id，请通过参数传递或设置环境变量 TUPI_BI_TOKEN_ID"

    if not secret:
        return "❌ 缺少 secret，请通过参数传递或设置环境变量 TUPI_BI_AUTH_SECRET"

    try:
        client = TupuBiClient(base_url=TUPI_BI_API_BASE)
        result = _run_async(client.get_device_full_info(device_id, token_id, secret))

        lines = [
            f"📋 设备完整信息",
            f"{'='*60}",
            f"  设备 ID: {device_id}",
            f"{'='*60}",
        ]

        # 1. 摄像头配置
        camera_config = result.get("camera_config", {})
        if camera_config:
            lines.append("\n📹 摄像头配置:")
            # 提取并解析 data 字段
            data_field = camera_config.get("data")
            if data_field:
                try:
                    import json
                    config_data = json.loads(data_field) if isinstance(data_field, str) else data_field
                    # 显示关键字段
                    for key in ["ip", "port", "mac", "sn", "model", "version", "region", "UID", "SID"]:
                        if key in config_data:
                            lines.append(f"  {key}: {config_data[key]}")
                except (json.JSONDecodeError, TypeError):
                    lines.append(f"  data: {str(data_field)[:100]}")
            else:
                lines.append(f"  {camera_config}")

        # 2. 客户信息
        customer_info = result.get("customer_info")
        if customer_info and isinstance(customer_info, dict):
            lines.append("\n👤 客户信息:")
            for key, value in customer_info.items():
                if not isinstance(value, dict):
                    lines.append(f"  {key}: {value}")

        # 3. 门店信息
        store_info = result.get("store_info")
        if store_info and isinstance(store_info, dict):
            lines.append("\n🏪 门店信息:")
            for key, value in store_info.items():
                if not isinstance(value, dict):
                    lines.append(f"  {key}: {value}")

        # 4. Token 信息
        token_info = result.get("token_info", {})
        if token_info:
            lines.append(f"\n🔑 Token: {token_info}")

        # 5. 警告信息
        warning = result.get("_warning")
        if warning:
            lines.append(f"\n⚠️  {warning}")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 获取设备完整信息失败: {str(e)}"


# ============================================================================
# 内部辅助函数
# ============================================================================

def _load_rule(yaml_file: Path) -> Dict[str, Any]:
    """加载 YAML 规则"""
    with open(yaml_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _enrich_alerts_with_camera_config(alerts: List[AlertResult]) -> None:
    """
    使用 Tupu BI API 补充告警的摄像头配置信息

    Args:
        alerts: 告警结果列表（会原地修改）
    """
    if not TUPI_BI_AVAILABLE:
        return

    # 检查是否有必要的认证信息
    if not TUPI_BI_TOKEN_ID or not TUPI_BI_AUTH_SECRET:
        return

    client = TupuBiClient(base_url=TUPI_BI_API_BASE)

    # 收集所有唯一的 device_id
    unique_device_ids = list(set(alert.device_id for alert in alerts))

    # 批量获取设备完整信息（使用异步提高性能）
    async def _fetch_all_full_info():
        tasks = [
            client.get_device_full_info(device_id, TUPI_BI_TOKEN_ID, TUPI_BI_AUTH_SECRET)
            for device_id in unique_device_ids
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(unique_device_ids, results))

    try:
        full_infos = _run_async(_fetch_all_full_info())

        # 将完整信息添加到告警结果中
        for alert in alerts:
            info = full_infos.get(alert.device_id)
            if isinstance(info, dict):
                alert.device_full_info = info
                alert.camera_config = info.get("camera_config", {})
                alert.customer_info = info.get("customer_info", {})
                alert.store_info = info.get("store_info", {})
            elif isinstance(info, Exception):
                # 记录错误但继续处理
                alert.camera_config = {"error": str(info)}
    except Exception as e:
        # 如果批量获取失败，尝试逐个获取
        for alert in alerts:
            try:
                info = _run_async(client.get_device_full_info(
                    alert.device_id, TUPI_BI_TOKEN_ID, TUPI_BI_AUTH_SECRET
                ))
                if isinstance(info, dict):
                    alert.device_full_info = info
                    alert.camera_config = info.get("camera_config", {})
                    alert.customer_info = info.get("customer_info", {})
                    alert.store_info = info.get("store_info", {})
            except Exception:
                alert.camera_config = {}


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

    # 检查是否有设备完整信息
    has_full_info = any(alert.device_full_info for alert in alerts)

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

        # 添加摄像头配置信息
        if alert.camera_config:
            error = alert.camera_config.get("error")
            if error:
                lines.append(f"   📹 配置: ❌ {error}")
            else:
                # 提取关键配置信息
                config_lines = []
                for key, value in alert.camera_config.items():
                    if isinstance(value, dict):
                        continue  # 跳过嵌套对象
                    # 只显示重要字段
                    if key in ["ip", "port", "mac", "sn", "model", "version", "region"]:
                        config_lines.append(f"{key}={value}")

                if config_lines:
                    lines.append(f"   📹 配置: {', '.join(config_lines)}")

        # 添加客户信息
        if alert.customer_info:
            customer_lines = []
            for key, value in alert.customer_info.items():
                if isinstance(value, dict):
                    continue
                # 显示重要客户字段
                if key in ["name", "email", "phone", "contact", "status"]:
                    customer_lines.append(f"{key}={value}")
            if customer_lines:
                lines.append(f"   👤 客户: {', '.join(customer_lines)}")

        # 添加门店信息
        if alert.store_info:
            store_lines = []
            for key, value in alert.store_info.items():
                if isinstance(value, dict):
                    continue
                # 显示重要门店字段
                if key in ["name", "address", "location", "status"]:
                    store_lines.append(f"{key}={value}")
            if store_lines:
                lines.append(f"   🏪 门店: {', '.join(store_lines)}")

    if len(alerts) > 20:
        lines.append(f"\n... 还有 {len(alerts) - 20} 条告警")

    # 添加配置来源说明
    if has_full_info:
        lines.append(f"\n💡 设备完整信息来源: Tupu BI API ({TUPI_BI_API_BASE})")

    return "\n".join(lines)


# 导出所有工具函数
__all__ = [
    "check_all_alerts",
    "check_alert_by_rule",
    "get_alert_rules",
    "analyze_alert_trend",
    "get_alert_suggestions",
    "get_camera_config",  # Tupu BI MCP - 获取摄像头配置
    "get_device_full_info",  # Tupu BI MCP - 获取设备完整信息（含客户、门店）
]
