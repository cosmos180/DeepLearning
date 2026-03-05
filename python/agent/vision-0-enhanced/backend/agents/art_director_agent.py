"""
art_director_agent.py — 艺术总监 Agent
与导演并行工作，负责视觉风格圣经和色彩方案
"""

from ..core.base_agent import BaseAgent
from ..core.blackboard import ArtifactType


class ArtDirectorAgent(BaseAgent):
    name = "艺术总监"
    model = "gpt-4.1-mini"
    temperature = 0.8
    max_tokens = 2500
    max_reflection_rounds = 0  # 艺术总监并行工作，不需要反思

    @property
    def system_prompt(self) -> str:
        return """你是 AI 影视制片厂的**艺术总监**，视觉风格的最高裁判官。

你将根据故事圣经，制定一份完整的**视觉风格圣经（Visual Style Bible）**，为所有视觉创作提供统一的美学标准。

## 你的核心职责
1. **色彩语言**：为每个叙事阶段定义色彩情绪板（Mood Board）
2. **光影哲学**：确定整体光影风格和关键场景的光线方案
3. **参考系建立**：引用真实的电影/摄影作品作为视觉锚点
4. **禁忌清单**：明确哪些视觉元素与本片风格相悖

## 输出格式

## STYLE_GUIDE
# 视觉风格圣经

## 整体美学定位
[用3部参考电影定义视觉坐标系，格式：电影名(导演/年份) + 借鉴元素]

## 色彩方案
| 叙事阶段 | 主色调 | 辅助色 | 情绪意图 | 参考画面 |
|---------|--------|--------|---------|---------|

## 光影方案
[整体光影风格 + 关键场景光线设计]

## 视觉禁忌
[列出5-8条本片绝对不能出现的视觉元素或风格]

## 统一风格标签（用于 Video Prompt）
[给出5-8个风格标签，所有 Video Prompt 必须包含这些标签，使用中文]"""

    async def build_user_prompt(self) -> str:
        # 新增强制中文约束
        constraint = "【重要提示】请确保所有输出内容严格使用中文（包括所有标题、标签和术语）。"

        logline = await self.bb.read(ArtifactType.LOGLINE) or ""
        characters = await self.bb.read(ArtifactType.CHARACTER_SHEETS) or ""
        beat_sheet = await self.bb.read(ArtifactType.BEAT_SHEET) or ""

        return f"""请根据以下故事圣经，制定视觉风格圣经：

## Logline
{logline}

## 角色设定
{characters[:800]}

## 故事节拍（了解情绪走向）
{beat_sheet[:600]}

{constraint}
请严格按照系统提示中的格式输出 STYLE_GUIDE 部分。"""

    async def parse_and_publish(self, raw_output: str) -> None:
        # 提取 STYLE_GUIDE 部分
        if "## STYLE_GUIDE" in raw_output:
            style_guide = raw_output.split("## STYLE_GUIDE", 1)[1].strip()
        else:
            style_guide = raw_output

        await self.bb.publish(ArtifactType.STYLE_GUIDE, style_guide)
