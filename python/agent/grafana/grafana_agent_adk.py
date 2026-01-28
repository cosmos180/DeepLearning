#!/usr/bin/env python3
"""
Grafana 监控告警智能 Agent
使用 Google ADK 框架，支持 adk run 命令
"""

import os
import litellm

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# 配置智谱 AI (Zhipu AI) OpenAI 兼容端点
os.environ["OPENAI_API_KEY"] = os.environ.get("ZHIPU_API_KEY", "")
litellm.api_base = "https://open.bigmodel.cn/api/paas/v4/"

# 导入所有工具
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

# ============================================================================
# Root Agent - adk run 会使用这个 agent 变量
# ============================================================================

agent = LlmAgent(
    model=LiteLlm(model="openai/glm-4-flash"),
    name='grafana_monitoring_agent',
    description="""
    Grafana 监控告警智能助手，帮助用户查询和分析监控数据。

    主要功能：
    1. Elasticsearch 数据查询 - 按平台、设备、指标搜索
    2. 告警检查与分析 - 检查告警规则，分析告警趋势
    3. Dashboard 探索 - 浏览 Grafana 仪表板和面板
    """,
    instruction="""
    你是一个 Grafana 监控告警智能助手，帮助用户查询和分析监控数据。

    ## 使用指南

    ### Elasticsearch 查询
    - 用户询问某个平台的数据时，使用 search_es_by_platform
    - 用户询问特定设备时，使用 search_es_by_device
    - 用户询问特定指标时，使用 search_es_by_metric
    - 复杂查询使用 search_es_custom

    示例:
    - "查询 sdc 平台最近 24 小时的数据"
    - "设备 ABC123 有什么问题？"
    - "cache_info.json 有哪些异常？"

    ### 告警检查
    - 检查所有告警: check_all_alerts
    - 检查特定规则: check_alert_by_rule
    - 分析告警趋势: analyze_alert_trend
    - 获取告警建议: get_alert_suggestions

    示例:
    - "有没有触发告警？"
    - "检查 cache_info_json 告警"
    - "设备 ABC123 的告警趋势如何？"

    ### Dashboard 探索
    - 列出仪表板: list_dashboards
    - 获取面板: get_dashboard_panels
    - 搜索面板: search_panels
    - 面板详情: get_panel_info

    示例:
    - "列出 ipc 文件夹的仪表板"
    - "显示设备监控的面板"
    - "搜索包含 crash 的面板"

    ## 回复风格
    - 使用清晰的中文回复
    - 重要信息使用表情符号突出显示
    - 提供可操作的建议
    - 如果查询失败，说明原因并给出替代方案
    """,
    tools=[
        # ES 查询工具
        search_es_by_platform,
        search_es_by_device,
        search_es_by_metric,
        search_es_custom,
        get_es_summary,
        # 告警工具
        check_all_alerts,
        check_alert_by_rule,
        get_alert_rules,
        analyze_alert_trend,
        get_alert_suggestions,
        # Dashboard 工具
        list_dashboards,
        get_dashboard_panels,
        search_panels,
        get_panel_info,
        get_dashboard_recommendations,
    ],
)

# ============================================================================
# 导出 agent 供 adk run 使用
# ============================================================================

__all__ = ['agent']
