#!/usr/bin/env python3
"""
Alert Checker - 基于规则的告警检查器
支持 YAML 配置文件定义告警规则，定时检查 Elasticsearch 数据
"""

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import yaml

# 添加脚本目录到路径以导入 email_notifier
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from email_notifier import EmailNotifier, EmailConfig
except ImportError:
    EmailNotifier = None
    EmailConfig = None


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    description: str
    index: str
    query: str
    alert_field: str
    threshold_type: str
    threshold: float
    aggregation: str
    aggregation_field: str
    time_range: str
    schedule: str
    severity: str
    notification_type: str
    notification_template: str

    def get_aggregation_field(self) -> str:
        """获取聚合字段（自动添加 .keyword 后缀）"""
        field = self.aggregation_field
        # 如果字段名没有 .keyword 且是常见文本字段，自动添加
        if not field.endswith('.keyword') and field in ['deviceId', 'device_id']:
            return field + '.keyword'
        return field

    @classmethod
    def from_yaml(cls, file_path: str) -> 'AlertRule':
        """从 YAML 文件加载规则"""
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return cls(
            name=config.get('name', 'Unnamed Alert'),
            description=config.get('description', ''),
            index=config.get('index', 'tupu-metrics-production-tp_ipc-*'),
            query=config.get('query', ''),
            alert_field=config['alert']['field'],
            threshold_type=config['alert']['threshold_type'],
            threshold=float(config['alert']['threshold']),
            aggregation=config['alert'].get('aggregation', 'terms'),
            aggregation_field=config['alert'].get('aggregation_field', 'deviceId'),
            time_range=config['time_window']['range'],
            schedule=config['time_window']['schedule'],
            severity=config.get('severity', 'warning'),
            notification_type=config['notification']['type'],
            notification_template=config['notification'].get('template', ''),
        )


@dataclass
class Alert:
    """告警事件"""
    rule_name: str
    device_id: str
    field: str
    value: float
    threshold: float
    severity: str
    timestamp: str
    message: str


# ============================================================================
# ES 查询
# ============================================================================

ES_HOST = "172.26.2.88"
ES_PORT = 39202
ES_URL = f"http://{ES_HOST}:{ES_PORT}"


def build_aggregation_query(rule: AlertRule) -> Dict[str, Any]:
    """构建聚合查询 DSL"""
    # 判断是否是文档计数告警
    is_count_alert = rule.alert_field == "_count"

    if is_count_alert:
        # 文档计数告警：只按设备聚合，使用 doc_count
        return {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": rule.query}},
                        {"range": {"@timestamp": {"gte": rule.time_range, "lte": "now"}}}
                    ]
                }
            },
            "aggs": {
                "by_device": {
                    "terms": {
                        "field": rule.get_aggregation_field(),
                        "size": 1000,
                        "order": {"latest_time": "desc"}  # 按最新时间排序
                    },
                    "aggs": {
                        "latest_time": {
                            "max": {"field": "@timestamp"}  # 获取最新时间戳
                        }
                    }
                }
            }
        }
    else:
        # 数值字段告警：聚合后取最大值
        return {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": rule.query}},
                        {"range": {"@timestamp": {"gte": rule.time_range, "lte": "now"}}}
                    ]
                }
            },
            "aggs": {
                "by_device": {
                    "terms": {
                        "field": rule.get_aggregation_field(),
                        "size": 1000
                    },
                    "aggs": {
                        "max_value": {
                            "max": {"field": rule.alert_field}
                        },
                        "latest_time": {
                            "max": {"field": "@timestamp"}  # 获取最新时间戳
                        }
                    }
                }
            }
        }


async def query_aggregation(rule: AlertRule) -> List[Dict[str, Any]]:
    """执行聚合查询"""
    query = build_aggregation_query(rule)
    url = f"{ES_URL}/{rule.index}/_search"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=query)
            response.raise_for_status()
            data = response.json()

            # 提取聚合结果
            buckets = data.get("aggregations", {}).get("by_device", {}).get("buckets", [])
            return buckets
        except httpx.HTTPStatusError as e:
            print(f"❌ Error querying ES: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text[:500]}")
            return []
        except httpx.HTTPError as e:
            print(f"❌ Error querying ES: {e}")
            return []


# ============================================================================
# 告警检查
# ============================================================================

def check_threshold(value: float, threshold_type: str, threshold: float) -> bool:
    """检查是否触发阈值"""
    if threshold_type == "greater_than":
        return value > threshold
    elif threshold_type == "less_than":
        return value < threshold
    elif threshold_type == "equal":
        return value == threshold
    elif threshold_type == "greater_equal":
        return value >= threshold
    elif threshold_type == "less_equal":
        return value <= threshold
    return False


def format_alert_message(alert: Alert, template: str) -> str:
    """格式化告警消息"""
    return template.format(
        name=alert.rule_name,
        device_id=alert.device_id,
        value=alert.value,
        threshold=alert.threshold,
        timestamp=alert.timestamp,
        severity=alert.severity,
    )


def check_rule(rule: AlertRule) -> List[Alert]:
    """检查单个规则"""
    alerts = []
    buckets = asyncio.run(query_aggregation(rule))

    # 判断是否是文档计数告警
    is_count_alert = rule.alert_field == "_count"

    for bucket in buckets:
        device_id = bucket["key"]

        # 根据告警类型获取值
        if is_count_alert:
            value = bucket["doc_count"]  # 文档计数
        else:
            value = bucket["max_value"]["value"]  # 字段最大值
            if value is None:
                continue  # 跳过无值的设备

        # 检查阈值
        if check_threshold(value, rule.threshold_type, rule.threshold):
            # 获取该设备的最新时间戳（来自 ES 文档）
            latest_time_value = bucket.get("latest_time", {}).get("value")
            if latest_time_value:
                # ES 返回的是毫秒时间戳，需要转换
                timestamp = datetime.fromtimestamp(latest_time_value / 1000).isoformat()
            else:
                timestamp = datetime.now().isoformat()

            # 格式化消息
            message = format_alert_message(
                Alert(
                    rule_name=rule.name,
                    device_id=device_id,
                    field=rule.alert_field,
                    value=value,
                    threshold=rule.threshold,
                    severity=rule.severity,
                    timestamp=timestamp,
                    message="",
                ),
                rule.notification_template or "{name}: {device_id} = {value} (threshold: {threshold})"
            )

            alerts.append(Alert(
                rule_name=rule.name,
                device_id=device_id,
                field=rule.alert_field,
                value=value,
                threshold=rule.threshold,
                severity=rule.severity,
                timestamp=timestamp,
                message=message
            ))

    return alerts


# ============================================================================
# 通知输出
# ============================================================================

# 全局邮件通知器实例
_email_notifier = None


def init_email_notifier(config_path: str = "monitoring/config/email.yaml") -> bool:
    """初始化邮件通知器"""
    global _email_notifier
    if EmailNotifier is None:
        print("⚠️ Email notification not available")
        return False

    try:
        config = EmailConfig.from_yaml(config_path)
        _email_notifier = EmailNotifier(config)
        print("✅ Email notification initialized")
        return True
    except Exception as e:
        print(f"⚠️ Failed to initialize email: {e}")
        return False


def send_alert(alert: Alert, send_email: bool = False):
    """发送告警"""
    # 根据严重级别选择图标
    icon = "🔴" if alert.severity == "critical" else "🟡" if alert.severity == "warning" else "🔵"

    print(f"\n{icon} ALERT TRIGGERED")
    print(f"{'='*60}")
    print(alert.message)
    print(f"{'='*60}")

    # 发送邮件
    if send_email and _email_notifier:
        try:
            _email_notifier.send_alert(
                rule_name=alert.rule_name,
                device_id=alert.device_id,
                field=alert.field,
                value=alert.value,
                threshold=alert.threshold,
                severity=alert.severity,
                timestamp=alert.timestamp,
            )
        except Exception as e:
            print(f"⚠️ Failed to send email: {e}")


def send_summary(alerts: List[Alert], send_email: bool = False):
    """发送摘要"""
    if not alerts:
        print("\n✅ No alerts triggered")
        return

    print(f"\n{'='*60}")
    print(f"📊 Alert Summary")
    print(f"{'='*60}")
    print(f"  Total Alerts: {len(alerts)}")
    print(f"  Critical: {sum(1 for a in alerts if a.severity == 'critical')}")
    print(f"  Warning: {sum(1 for a in alerts if a.severity == 'warning')}")
    print(f"{'='*60}")

    # 发送摘要邮件
    if send_email and _email_notifier and len(alerts) > 0:
        try:
            alerts_data = [
                {
                    "rule_name": a.rule_name,
                    "device_id": a.device_id,
                    "value": a.value,
                    "threshold": a.threshold,
                    "severity": a.severity,
                    "timestamp": a.timestamp,
                }
                for a in alerts
            ]
            _email_notifier.send_alert_summary(alerts_data)
        except Exception as e:
            print(f"⚠️ Failed to send summary email: {e}")


# ============================================================================
# 规则加载
# ============================================================================

def load_rules(rules_dir: str) -> List[AlertRule]:
    """加载规则目录下的所有 YAML 文件"""
    rules = []
    rules_path = Path(rules_dir)

    if not rules_path.exists():
        print(f"❌ Rules directory not found: {rules_dir}")
        return []

    # 递归查找所有 YAML 文件
    for yaml_file in rules_path.rglob("*.yaml"):
        try:
            rule = AlertRule.from_yaml(str(yaml_file))
            rules.append(rule)
            print(f"✅ Loaded rule: {rule.name} from {yaml_file.relative_to(rules_path)}")
        except Exception as e:
            print(f"❌ Error loading {yaml_file}: {e}")

    return rules


# ============================================================================
# 主程序
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Alert Checker - Check ES data against alert rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 检查所有规则
  %(prog)s --rules-dir monitoring/alert_rules

  # 检查单个规则并发送邮件
  %(prog)s --rule monitoring/alert_rules/sdc/cache_info_json.yaml --email

  # 显示规则详情
  %(prog)s --rule monitoring/alert_rules/sdc/cache_info_json.yaml --show-rule

  # 测试邮件发送
  %(prog)s --test-email
        """
    )
    parser.add_argument(
        "--rules-dir",
        default="monitoring/alert_rules",
        help="Directory containing alert rule YAML files"
    )
    parser.add_argument(
        "--rule",
        help="Single rule file to check"
    )
    parser.add_argument(
        "--show-rule",
        action="store_true",
        help="Show rule details and exit"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output alerts as JSON"
    )
    parser.add_argument(
        "--email",
        action="store_true",
        help="Send email notifications for alerts"
    )
    parser.add_argument(
        "--email-config",
        default="monitoring/config/email.yaml",
        help="Path to email configuration file"
    )
    parser.add_argument(
        "--test-email",
        action="store_true",
        help="Test email configuration by sending a test email"
    )

    args = parser.parse_args()

    # 测试邮件
    if args.test_email:
        print("📧 Testing email configuration...")
        init_email_notifier(args.email_config)
        return

    # 初始化邮件通知器
    email_enabled = False
    if args.email:
        email_enabled = init_email_notifier(args.email_config)

    # 加载规则
    if args.rule:
        try:
            rules = [AlertRule.from_yaml(args.rule)]
            print(f"✅ Loaded rule: {rules[0].name}")
        except Exception as e:
            print(f"❌ Error loading rule: {e}")
            sys.exit(1)
    else:
        rules = load_rules(args.rules_dir)

    if not rules:
        print("❌ No rules loaded")
        sys.exit(1)

    # 显示规则详情
    if args.show_rule:
        for rule in rules:
            print(f"\n{'='*60}")
            print(f"Rule: {rule.name}")
            print(f"{'='*60}")
            print(f"  Description: {rule.description}")
            print(f"  Index: {rule.index}")
            print(f"  Query: {rule.query}")
            print(f"  Field: {rule.alert_field}")
            print(f"  Threshold Type: {rule.threshold_type}")
            print(f"  Threshold: {rule.threshold}")
            print(f"  Aggregation: {rule.aggregation} by {rule.aggregation_field}")
            print(f"  Time Range: {rule.time_range}")
            print(f"  Schedule: {rule.schedule}")
            print(f"  Severity: {rule.severity}")
            print(f"  Notification: {rule.notification_type}")
        return

    # 检查规则
    all_alerts = []
    for rule in rules:
        print(f"\n🔍 Checking rule: {rule.name}")
        alerts = check_rule(rule)
        all_alerts.extend(alerts)

        # 打印告警到控制台（不发送邮件）
        for alert in alerts:
            send_alert(alert, send_email=False)

        print(f"  Found {len(alerts)} alerts")

    # 只发送摘要邮件（包含所有告警）
    send_summary(all_alerts, send_email=email_enabled)

    # JSON 输出
    if args.json:
        alerts_data = [
            {
                "rule_name": a.rule_name,
                "device_id": a.device_id,
                "field": a.field,
                "value": a.value,
                "threshold": a.threshold,
                "severity": a.severity,
                "timestamp": a.timestamp,
            }
            for a in all_alerts
        ]
        print("\n" + json.dumps(alerts_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
