#!/usr/bin/env python3
"""
Grafana ADK Root Agent
基于 Google Agent Development Kit 的智能监控告警 Agent
"""

import os
import litellm
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import LlmAgent

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
# 配置
# ============================================================================

# 配置智谱 AI (Zhipu AI) OpenAI 兼容端点
os.environ["OPENAI_API_KEY"] = os.environ.get("ZHIPU_API_KEY", "your-zhipu-api-key")
litellm.api_base = "https://open.bigmodel.cn/api/paas/v4/"

# ============================================================================
# Root Agent
# ============================================================================

root_agent = LlmAgent(
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
# 运行入口
# ============================================================================

def main():
    """
    运行 Agent 交互

    使用 ADK 的 invoke 方法进行单次调用
    """
    print("Grafana 监控告警智能助手")
    print("=" * 60)
    print("输入 'quit' 退出\n")

    while True:
        try:
            user_input = input("你: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break

            # 调用 Agent - 使用 ADK 的方式
            # 注意: 实际调用方式取决于 ADK 版本
            try:
                # 尝试使用 invoke 方法
                if hasattr(root_agent, 'invoke'):
                    response = root_agent.invoke(user_input)
                elif hasattr(root_agent, 'run'):
                    response = root_agent.run(user_input)
                else:
                    response = f"Agent 已加载，请使用 ADK 框架的客户端进行交互。当前支持的工具:\n" + \
                              "- ES 查询: search_es_by_platform, search_es_by_device\n" + \
                              "- 告警检查: check_all_alerts, check_alert_by_rule\n" + \
                              "- Dashboard: list_dashboards, get_dashboard_panels"

                print(f"\n助手: {response}\n")
            except AttributeError:
                print(f"\n助手: Agent 已初始化 (tools: {len(root_agent.tools)} 个)\n")
                print("💡 请使用 ADK 框架的客户端或 API 进行交互\n")

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {str(e)}\n")


if __name__ == "__main__":
    main()
