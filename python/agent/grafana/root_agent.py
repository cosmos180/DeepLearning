"""
Grafana 告警邮件 Agent

唯一功能：发送告警邮件到指定收件人

使用方式:
    adk run .
    > 发送 sdc 平台的告警邮件
    > 发送所有平台的告警邮件，时间范围是今天
"""

import os
import litellm

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .tools.alert_email_reporter import send_alert_report_email

# 配置智谱 AI (Zhipu AI) OpenAI 兼容端点
os.environ["OPENAI_API_KEY"] = os.environ.get("ZHIPU_API_KEY", "")
litellm.api_base = "https://open.bigmodel.cn/api/paas/v4/"


# 创建发送邮件工具
def send_alert_email(
    platforms: str = None,
    time_range: str = "today",
    recipients: str = None,
) -> str:
    """
    发送 Grafana 告警邮件

    此工具会自动获取 Dashboard 的所有 Panel，为每个 platform 生成独立的告警邮件并发送。

    Args:
        platforms: 平台列表，逗号分隔（默认所有平台）
        time_range: 时间范围（如 "today", "6h", "24h", "7d"）
        recipients: 收件人邮箱，逗号分隔

    Returns:
        发送结果摘要
    """
    return send_alert_report_email(
        platforms=platforms,
        time_range=time_range,
        recipients=recipients,
    )


# 创建根 Agent
root_agent = LlmAgent(
    model=LiteLlm(model="openai/glm-4-flash"),
    name="grafana_alert_agent",
    description="Grafana 监控告警邮件发送助手。可以帮你发送所有平台的告警邮件，支持自定义平台、时间范围和收件人。",
    instruction="""你是 Grafana 监控告警邮件发送助手。

你可以帮助用户发送所有平台的告警邮件。用户可以指定：
- 特定的平台列表（如 sdc, tpboxv3）
- 时间范围（如 today, 6h, 24h, 7d）
- 收件人邮箱地址

当用户请求发送告警邮件时，使用 send_alert_email 工具。
如果不指定平台，默认发送所有平台。
如果不指定时间范围，默认使用 today。
""",
    tools=[send_alert_email],
)
