#!/usr/bin/env python3
"""
Grafana 监控告警智能助手 - 简化版
直接支持自然语言调用工具
"""

import asyncio
import json
import os
import re
from typing import Optional

# 配置 API
os.environ["OPENAI_API_KEY"] = os.environ.get("ZHIPU_API_KEY", "")

# 导入工具
from tools.es_query_tool import (
    search_es_by_platform,
    search_es_by_device,
    search_es_by_metric,
    search_es_custom,
    get_es_summary,
)

from tools.alert_tool import (
    check_all_alerts,
    check_alert_by_rule,
    get_alert_rules,
    analyze_alert_trend,
    get_alert_suggestions,
)

from tools.dashboard_tool import (
    list_dashboards,
    get_dashboard_panels,
    search_panels,
    get_panel_info,
    get_dashboard_recommendations,
)


def parse_time_range(text: str) -> str:
    """从文本中解析时间范围"""
    # 匹配 "最近 X 小时/天" 或 "Xh/Xd"
    patterns = [
        r'(\d+)\s*(小时|hour|h)',
        r'(\d+)\s*(天|day|d)',
        r'(\d+)h',
        r'(\d+)d',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1)
            unit = match.group(2) if len(match.groups()) > 1 else ''
            if 'h' in unit.lower() or pattern.endswith('h'):
                return f"now-{value}h"
            else:
                return f"now-{value}d"

    # 默认返回 24h
    return "now-24h"


def parse_platform(text: str) -> Optional[str]:
    """从文本中解析平台名称"""
    platforms = ['sdc', 'ipc', 'bi-api', 'doppelganger', 'image-go-api-queue']
    text_lower = text.lower()
    for platform in platforms:
        if platform in text_lower:
            return platform
    return None


def parse_device_id(text: str) -> Optional[str]:
    """从文本中解析设备 ID"""
    # 匹配常见的设备 ID 格式 (32位十六进制)
    match = re.search(r'[a-fA-F0-9]{32}', text)
    if match:
        return match.group(0)
    return None


def parse_rule_name(text: str) -> Optional[str]:
    """从文本中解析规则名称"""
    rules = ['cache_info_json', 'cache_info', 'disk_used_ratio', 'disk', 'crash', 'error']
    text_lower = text.lower()
    for rule in rules:
        if rule in text_lower:
            # 返回完整的规则名
            if 'cache' in rule and 'json' in text_lower:
                return 'cache_info_json'
            return rule
    return None


def process_query(user_input: str) -> str:
    """
    处理用户查询，自动路由到合适的工具

    支持的自然语言格式:
    - "查询 sdc 平台最近 12 小时的告警数据"
    - "检查 sdc 的 cache 告警"
    - "设备 ABC123 有什么问题"
    - "列出 ipc 文件夹的仪表板"
    """
    user_input_lower = user_input.lower()

    # ==================== ES 查询 ====================
    if any(kw in user_input_lower for kw in ['查询', '搜索', 'search', 'query', '数据', '']):
        platform = parse_platform(user_input)
        device_id = parse_device_id(user_input)

        # 按设备查询
        if device_id:
            time_range = parse_time_range(user_input)
            print(f"🔍 执行: search_es_by_device(device_id={device_id[:8]}..., platform={platform}, time_range={time_range})")
            return search_es_by_device(device_id=device_id, platform=platform, time_range=time_range.replace("now-", ""))

        # 按平台查询
        if platform:
            time_range = parse_time_range(user_input)
            print(f"🔍 执行: search_es_by_platform(platform={platform}, time_range={time_range})")
            return search_es_by_platform(platform=platform, time_range=time_range.replace("now-", ""))

        # 按指标查询
        if 'cache' in user_input_lower or 'disk' in user_input_lower or 'crash' in user_input_lower:
            metric = 'cache_info.json' if 'cache' in user_input_lower else 'disk.used_ratio' if 'disk' in user_input_lower else ''
            if metric:
                time_range = parse_time_range(user_input)
                print(f"🔍 执行: search_es_by_metric(metric_name={metric}, platform={platform})")
                return search_es_by_metric(metric_name=metric, platform=platform, time_range=time_range.replace("now-", ""))

    # ==================== 告警检查 ====================
    if any(kw in user_input_lower for kw in ['告警', 'alert', '异常', '检查', '触发']):
        rule_name = parse_rule_name(user_input)
        platform = parse_platform(user_input)

        # 检查特定规则
        if rule_name:
            print(f"🔍 执行: check_alert_by_rule(rule_name={rule_name})")
            return check_alert_by_rule(rule_name=rule_name)

        # 检查所有告警 (可能带平台过滤)
        print(f"🔍 执行: check_all_alerts(platform={platform})")
        return check_all_alerts(platform=platform)

    # ==================== Dashboard ====================
    if any(kw in user_input_lower for kw in ['仪表板', 'dashboard', '面板', 'panel']):
        if '列表' in user_input_lower or '列出' in user_input_lower or 'list' in user_input_lower:
            folder = parse_platform(user_input) or None
            print(f"🔍 执行: list_dashboards(folder={folder})")
            return list_dashboards(folder=folder)

        # 搜索面板
        if '搜索' in user_input_lower or 'search' in user_input_lower:
            keyword = user_input.split('搜索')[-1].strip() if '搜索' in user_input else ''
            if not keyword:
                keyword = user_input.split('search')[-1].strip() if 'search' in user_input else ''
            print(f"🔍 执行: search_panels(keyword={keyword})")
            return search_panels(keyword=keyword or 'monitoring')

    # ==================== 默认: 显示帮助 ====================
    return show_help()


def show_help() -> str:
    """显示帮助信息"""
    return """
📖 使用指南

【ES 查询】
  查询 sdc 平台最近 12 小时的数据
  搜索设备 ABC123 的问题
  cache 有什么异常？

【告警检查】
  有没有触发告警？
  检查 sdc 的 cache 告警
  disk 告警情况如何？

【Dashboard】
  列出 ipc 文件夹的仪表板
  搜索包含 crash 的面板

【直接调用工具】
  search_es_by_platform(platform='sdc', time_range='12h')
  check_alert_by_rule(rule_name='cache_info_json')
  list_dashboards(folder='ipc')
"""


def main():
    """运行交互式 Agent"""
    print("Grafana 监控告警智能助手")
    print("=" * 60)
    print("💡 输入自然语言查询，如:")
    print("   - 查询 sdc 平台最近 12 小时的告警数据")
    print("   - 检查 cache 告警")
    print("   - 设备 ABC123 有什么问题？")
    print("   - 输入 'help' 查看更多帮助")
    print("   - 输入 'quit' 退出")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("你: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            if user_input.lower() in ['help', 'h', '?']:
                print(show_help())
                continue

            # 处理查询
            result = process_query(user_input)
            print(f"\n助手: {result}\n")

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {str(e)}\n")


if __name__ == "__main__":
    main()
