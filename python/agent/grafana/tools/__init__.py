"""
Grafana 告警邮件发送工具

核心功能：为每个 platform 变量值生成包含所有 Panel 截图的告警邮件
"""

from .alert_email_reporter import (
    send_alert_report_email,
    AlertEmailReporter,
    GrafanaConfig,
    EmailConfig,
    AlertReportConfig,
)

__all__ = [
    # 核心工具：批量发送告警邮件
    "send_alert_report_email",
    "AlertEmailReporter",
    # 配置类
    "GrafanaConfig",
    "EmailConfig",
    "AlertReportConfig",
]
