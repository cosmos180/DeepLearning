#!/usr/bin/env python3
"""
测试告警邮件模板
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.email_notifier import EmailNotifier, EmailConfig


def test_alert_templates():
    """测试各种告警场景的邮件模板"""

    # 加载配置
    try:
        config = EmailConfig.from_yaml()
    except Exception as e:
        print(f"❌ Failed to load email config: {e}")
        return False

    notifier = EmailNotifier(config)

    # 测试场景
    test_cases = [
        {
            "name": "CPU 告警 - Critical",
            "data": {
                "rule_name": "High CPU Usage",
                "device_id": "server-prod-01",
                "field": "cpu_percent",
                "value": 95.5,
                "threshold": 80.0,
                "severity": "critical",
                "timestamp": "2025-01-22 12:30:45"
            }
        },
        {
            "name": "内存告警 - Warning",
            "data": {
                "rule_name": "Memory Usage High",
                "device_id": "db-server-03",
                "field": "memory_percent",
                "value": 85.2,
                "threshold": 80.0,
                "severity": "warning",
                "timestamp": "2025-01-22 12:31:20"
            }
        },
        {
            "name": "磁盘空间 - Critical",
            "data": {
                "rule_name": "Disk Space Low",
                "device_id": "storage-node-05",
                "field": "disk_percent",
                "value": 92.8,
                "threshold": 90.0,
                "severity": "critical",
                "timestamp": "2025-01-22 12:32:10"
            }
        },
        {
            "name": "网络延迟 - Warning",
            "data": {
                "rule_name": "High Network Latency",
                "device_id": "router-edge-02",
                "field": "latency_ms",
                "value": 180.5,
                "threshold": 150.0,
                "severity": "warning",
                "timestamp": "2025-01-22 12:33:00"
            }
        },
    ]

    print("=" * 60)
    print("告警邮件模板测试")
    print("=" * 60)
    print()

    # 询问用户要测试哪个场景
    print("请选择要测试的告警场景:")
    for i, case in enumerate(test_cases, 1):
        print(f"  {i}. {case['name']}")
    print(f"  {len(test_cases) + 1}. 全部测试")
    print(f"  0. 退出")

    try:
        choice = input("\n请输入选项 (0-{}): ".format(len(test_cases) + 1))
        choice = int(choice)
    except (ValueError, EOFError):
        print("\n使用默认选项: 全部测试")
        choice = len(test_cases) + 1

    print()

    # 根据选择执行测试
    if choice == 0:
        print("已取消测试")
        return True
    elif choice == len(test_cases) + 1:
        # 测试全部
        cases_to_test = test_cases
    elif 1 <= choice <= len(test_cases):
        cases_to_test = [test_cases[choice - 1]]
    else:
        print(f"❌ 无效选项: {choice}")
        return False

    # 执行测试
    success_count = 0
    for i, case in enumerate(cases_to_test, 1):
        print(f"[{i}/{len(cases_to_test)}] 发送: {case['name']}")
        success = notifier.send_alert(**case['data'])
        if success:
            success_count += 1
        print()

    # 汇总
    print("=" * 60)
    print(f"测试完成: {success_count}/{len(cases_to_test)} 封邮件发送成功")
    print("=" * 60)

    return success_count == len(cases_to_test)


def test_alert_summary():
    """测试告警摘要邮件"""
    print("\n是否测试告警摘要邮件? (y/n): ", end="")
    try:
        answer = input().strip().lower()
    except EOFError:
        answer = 'n'

    if answer != 'y':
        return True

    # 加载配置
    try:
        config = EmailConfig.from_yaml()
    except Exception as e:
        print(f"❌ Failed to load email config: {e}")
        return False

    notifier = EmailNotifier(config)

    # 模拟多条告警
    alerts = [
        {
            "rule_name": "High CPU Usage",
            "device_id": "server-prod-01",
            "severity": "critical",
            "value": 95.5,
            "threshold": 80.0,
            "timestamp": "2025-01-22 12:30:45"
        },
        {
            "rule_name": "Memory Usage High",
            "device_id": "db-server-03",
            "severity": "warning",
            "value": 85.2,
            "threshold": 80.0,
            "timestamp": "2025-01-22 12:31:20"
        },
        {
            "rule_name": "Disk Space Low",
            "device_id": "storage-node-05",
            "severity": "critical",
            "value": 92.8,
            "threshold": 90.0,
            "timestamp": "2025-01-22 12:32:10"
        },
    ]

    print("\n发送告警摘要邮件...")
    success = notifier.send_alert_summary(alerts)
    if success:
        print("✅ 告警摘要邮件发送成功")
    else:
        print("❌ 告警摘要邮件发送失败")

    return success


if __name__ == "__main__":
    # 测试单个告警邮件
    test_alert_templates()

    # 测试告警摘要邮件
    test_alert_summary()
