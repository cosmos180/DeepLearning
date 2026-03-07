"""
screenwriter_agent.py — 编剧 Agent
将故事圣经转化为标准 Fountain 格式剧本，并生成场景实体状态追踪表
"""

from ..core.base_agent import BaseAgent
from ..core.blackboard import ArtifactType


class ScreenwriterAgent(BaseAgent):
    name = "编剧"
    model = "gpt-4.1-mini"
    temperature = 0.75
    max_tokens = 4000
    max_reflection_rounds = 1

    @property
    def system_prompt(self) -> str:
        return """你是 AI 影视制片厂的**编剧**，文字蓝图的绘制者。

你将把「故事圣经」转化为一份可直接用于拍摄的**标准格式剧本**（Fountain 格式）。

## Fountain 格式规范
- Scene Heading（场景标题）：全大写，格式为 `INT./EXT. 地点 - 时间`
- Action（动作描述）：普通段落，避免主观内心描写，使用现在时
- Character（角色名）：全大写，居中
- Dialogue（对话）：角色名下方
- Transition（转场）：`> CUT TO: <` 等

## 对话要求
1. **去 AI 味**：充满停顿、打断、未说完的话
2. **少说多做**：能用动作表达的，不用对话
3. **潜台词**：角色说的不一定是真正想说的

## 时空一致性（强制要求）
- 时间标记前后一致（DAY/NIGHT/CONTINUOUS/LATER）
- 角色位移合理，不能"瞬移"
- 关键道具状态前后一致

## 输出格式
请输出两个部分：

## SCRIPT
[完整的 Fountain 格式剧本，包含5-10个场景]

## SCRIPT_NOTES
[包含：总场景数、预估时长、每幕场景分布、场景实体状态追踪表]"""

    async def build_user_prompt(self) -> str:
        logline = await self.bb.read(self.project_id, ArtifactType.LOGLINE) or "（未找到 Logline）"
        characters = await self.bb.read(self.project_id, ArtifactType.CHARACTER_SHEETS) or "（未找到角色设定）"
        beat_sheet = await self.bb.read(self.project_id, ArtifactType.BEAT_SHEET) or "（未找到节拍表）"

        return f"""请根据以下故事圣经，创作完整的标准格式剧本：

## Logline
{logline}

## 角色设定
{characters[:1500]}

## 故事节拍表
{beat_sheet[:2000]}

请严格按照系统提示中的格式输出两个部分：SCRIPT 和 SCRIPT_NOTES。
剧本应包含 5-10 个场景，每个场景都要推进情节或揭示角色。"""

    def reflection_criteria(self) -> str:
        return """剧本应满足：
1. 包含至少5个场景，每个场景有完整的 Scene Heading、Action 和 Dialogue
2. 时间标记（DAY/NIGHT等）前后一致，无矛盾
3. 对话去除"AI味"，有停顿、打断、潜台词
4. Script Notes 包含场景实体状态追踪表
5. 角色名使用全大写"""

    async def parse_and_publish(self, raw_output: str) -> None:
        sections = {"SCRIPT": "", "SCRIPT_NOTES": ""}
        current_section = None

        for line in raw_output.split("\n"):
            stripped = line.strip()
            if stripped == "## SCRIPT":
                current_section = "SCRIPT"
            elif stripped == "## SCRIPT_NOTES":
                current_section = "SCRIPT_NOTES"
            elif current_section:
                sections[current_section] += line + "\n"

        if not sections["SCRIPT"]:
            sections["SCRIPT"] = raw_output

        await self.bb.publish(self.project_id, ArtifactType.SCRIPT, sections["SCRIPT"].strip())
        await self.bb.publish(self.project_id, ArtifactType.SCRIPT_NOTES, sections["SCRIPT_NOTES"].strip())
