"""
creator_agent.py — 原著作者 Agent
将创意种子转化为完整的故事圣经（Logline + Character Sheets + Beat Sheet）
"""

from ..core.base_agent import BaseAgent
from ..core.blackboard import ArtifactType


class CreatorAgent(BaseAgent):
    name = "原著作者"
    model = "gpt-4.1-mini"
    temperature = 0.85
    max_tokens = 3000
    max_reflection_rounds = 1

    def __init__(self, blackboard, project_id, seed: str,
                 target_duration: str = "30分钟短片", style: str = "科幻+温情", model_name=None):
        super().__init__(blackboard, project_id, model_name=model_name)
        self.seed = seed
        self.target_duration = target_duration
        self.style = style

    @property
    def system_prompt(self) -> str:
        return """你是 AI 影视制片厂的**原著作者**，创意源头与世界观架构师。
你的使命是将一颗模糊的创意种子，打磨成一份完整、专业的「故事圣经（Story Bible）」。

核心要求：
1. **去 AI 味**：避免过于完美的解决方案、道德说教式结局、角色情绪过于单一
2. **冲突要真实**：内心冲突比外部冲突更重要，确保主角有真实的弱点和成长弧线
3. **视觉化思维**：每个设定脑中要能浮现出具体画面
4. **角色视觉特征**用英文描述（便于后续图像生成），其余用中文

输出格式严格按照以下三部分：

## LOGLINE
[一句话梗概，包含：主角 + 处境 + 目标 + 核心冲突 + 最大阻碍]

## CHARACTER_SHEETS
[为3-5名主要角色各建立档案，包含：姓名/代号、视觉特征(英文)、性格特质、背景故事、内心渴望、内心恐惧]

## BEAT_SHEET
[按三幕式结构列出15个关键节拍，每个节拍包含：发生了什么(1-2句) + 主角情绪状态 + 涉及的关键道具/位移]"""

    async def build_user_prompt(self) -> str:
        return f"""请根据以下创意种子，创作完整的故事圣经：

**创意种子：** {self.seed}
**目标时长：** {self.target_duration}
**风格基调：** {self.style}

请严格按照系统提示中的格式输出三个部分：LOGLINE、CHARACTER_SHEETS、BEAT_SHEET。"""

    def reflection_criteria(self) -> str:
        return """故事圣经应满足：
1. Logline 必须包含主角、核心冲突、目标、阻碍四要素
2. 至少有3个角色，每个角色有清晰的内心渴望和恐惧
3. Beat Sheet 覆盖三幕结构的所有关键节点（至少12个）
4. 角色视觉特征使用英文描述
5. 没有明显的"AI 味"（避免过于完美的解决方案或说教式结局）"""

    async def parse_and_publish(self, raw_output: str) -> None:
        # 解析并分别发布三个产出物
        sections = {"LOGLINE": "", "CHARACTER_SHEETS": "", "BEAT_SHEET": ""}
        current_section = None

        for line in raw_output.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## LOGLINE"):
                current_section = "LOGLINE"
            elif stripped.startswith("## CHARACTER_SHEETS"):
                current_section = "CHARACTER_SHEETS"
            elif stripped.startswith("## BEAT_SHEET"):
                current_section = "BEAT_SHEET"
            elif current_section:
                sections[current_section] += line + "\n"

        # 如果解析失败，将整个输出存入 logline
        if not any(sections.values()):
            sections["LOGLINE"] = raw_output

        await self.bb.publish(ArtifactType.LOGLINE, sections["LOGLINE"].strip())
        await self.bb.publish(ArtifactType.CHARACTER_SHEETS, sections["CHARACTER_SHEETS"].strip())
        await self.bb.publish(ArtifactType.BEAT_SHEET, sections["BEAT_SHEET"].strip())
