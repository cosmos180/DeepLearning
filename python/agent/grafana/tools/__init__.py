"""
Agent Tools Package
导出所有 agent 工具函数
"""

from .es_query_tool import (
    search_es_by_platform,
    search_es_by_device,
    search_es_by_metric,
    search_es_custom,
    get_es_summary,
)

from .alert_tool import (
    check_all_alerts,
    check_alert_by_rule,
    get_alert_rules,
    analyze_alert_trend,
    get_alert_suggestions,
)

from .dashboard_tool import (
    list_dashboards,
    get_dashboard_panels,
    search_panels,
    get_panel_info,
    get_dashboard_recommendations,
)

from .alert_email_reporter import (
    send_alert_report_email,
    AlertEmailReporter,
)

__all__ = [
    # ES 查询工具
    "search_es_by_platform",
    "search_es_by_device",
    "search_es_by_metric",
    "search_es_custom",
    "get_es_summary",
    # 告警工具
    "check_all_alerts",
    "check_alert_by_rule",
    "get_alert_rules",
    "analyze_alert_trend",
    "get_alert_suggestions",
    # Dashboard 工具
    "list_dashboards",
    "get_dashboard_panels",
    "search_panels",
    "get_panel_info",
    "get_dashboard_recommendations",
    # 告警邮件报告工具
    "send_alert_report_email",
    "AlertEmailReporter",
]
