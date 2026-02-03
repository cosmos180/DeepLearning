#!/usr/bin/env python3
"""
Grafana 告警邮件发送工具

一键发送所有 platform 的告警邮件到你的邮箱。

使用方式:
    python3 grafana_alert_tool.py                    # 发送所有平台（今天）
    python3 grafana_alert_tool.py --platforms sdc  # 发送指定平台
    python3 grafana_alert_tool.py --time-range 24h  # 自定义时间范围
    python3 grafana_alert_tool.py --help            # 查看帮助
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.alert_email_reporter import (
    AlertEmailReporter,
    GrafanaConfig,
    EmailConfig,
    AlertReportConfig,
    _run_async,
    RecipientsManager,
)
import os


def send_alerts(
    platforms: str = None,
    time_range: str = "today",
    recipients: str = None,
):
    """
    发送 Grafana 告警邮件

    核心功能:
    - ✅ 自动获取 Dashboard 面板
    - ✅ 按 platform 变量分发
    - ✅ 智能图片压缩 (10-50%)
    - ✅ 精美 HTML 邮件模板

    Args:
        platforms: 平台列表，逗号分隔（默认所有平台）
        time_range: 时间范围（today, 6h, 24h, 7d）
        recipients: 收件人邮箱，逗号分隔
    """
    # 默认平台列表
    default_platforms = ["sdc", "tpboxv3", "tpboxv2", "android_armv7", "1800A", "rv1109", "tpboxv1"]

    # 解析平台列表
    platform_list = [p.strip() for p in platforms.split(",")] if platforms else default_platforms

    # 解析收件人
    recipient_list = None
    if recipients:
        recipient_list = [r.strip() for r in recipients.split(",")]

    # 创建配置
    grafana_config = GrafanaConfig(
        url=os.getenv("GRAFANA_URL", "https://g.dev.tuputech.com"),
        api_key=os.getenv("GRAFANA_API_KEY", ""),
    )

    # 收件人配置
    recipients_manager = RecipientsManager()
    if recipient_list:
        email_recipients = recipient_list
    else:
        email_recipients = recipients_manager.load_recipients()
        if not email_recipients:
            recipients_str = os.getenv("RECIPIENTS_TO", "")
            email_recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]

    email_config = EmailConfig(
        sender_email=os.getenv("SENDER_EMAIL", ""),
        sender_password=os.getenv("SENDER_PASSWORD", ""),
        recipients=email_recipients,
    )

    report_config = AlertReportConfig(
        time_range=time_range,
        platforms=platform_list,
    )

    # 创建报告器并发送
    reporter = AlertEmailReporter(
        grafana_config=grafana_config,
        email_config=email_config,
        report_config=report_config,
    )

    print("=" * 70)
    print("🚨 Grafana 告警邮件发送工具")
    print("=" * 70)
    print(f"📊 平台数量: {len(platform_list)}")
    print(f"📅 时间范围: {time_range}")
    print(f"📧 收件人: {len(email_recipients)} 个")
    print("=" * 70)
    print()

    results = _run_async(reporter.send_all_platforms())

    # 汇总结果
    print()
    print("=" * 70)
    print("📊 发送结果汇总")
    print("=" * 70)

    success_count = sum(1 for r in results if r["success"])
    total_panels = sum(r["panels_count"] for r in results)
    total_screenshots = sum(r["screenshots_count"] for r in results)

    print(f"  成功: {success_count}/{len(results)} 个平台")
    print(f"  面板: {total_panels} 个")
    print(f"  截图: {total_screenshots} 张")
    print("=" * 70)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Grafana 告警邮件发送工具 - 一键发送所有 platform 的告警邮件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                              发送所有平台（今天）
  %(prog)s --platforms sdc,tpboxv3       发送指定平台
  %(prog)s --time-range 24h              发送最近24小时的数据
  %(prog)s --recipients user@example.com 发送到指定邮箱

核心功能:
  - 自动获取 Dashboard 面板
  - 按 platform 变量分发
  - 智能图片压缩 (10-50%%)
  - 精美 HTML 邮件模板
        """
    )

    parser.add_argument(
        "--platforms", "-p",
        type=str,
        help="平台列表，逗号分隔（默认：所有平台）"
    )

    parser.add_argument(
        "--time-range", "-t",
        type=str,
        default="today",
        choices=["today", "1h", "6h", "24h", "7d", "30d"],
        help="时间范围（默认：today）"
    )

    parser.add_argument(
        "--recipients", "-r",
        type=str,
        help="收件人邮箱，逗号分隔（默认：从配置读取）"
    )

    args = parser.parse_args()

    # 发送邮件
    send_alerts(
        platforms=args.platforms,
        time_range=args.time_range,
        recipients=args.recipients,
    )


if __name__ == "__main__":
    main()
