import os
import litellm
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import LlmAgent

# 配置智谱 AI (Zhipu AI) OpenAI 兼容端点
os.environ["OPENAI_API_KEY"] = os.environ.get("ZHIPU_API_KEY", "your-zhipu-api-key")
litellm.api_base = "https://open.bigmodel.cn/api/paas/v4/"

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = LlmAgent(
    model=LiteLlm(model="openai/glm-4-flash"),
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    tools=[get_current_time],
)
