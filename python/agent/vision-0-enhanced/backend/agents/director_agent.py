"""
director_agent.py — 导演 Agent
将剧本拆解为分镜清单，并生成视频生成 Prompt
"""

from ..core.base_agent import BaseAgent
from ..core.blackboard import ArtifactType


class DirectorAgent(BaseAgent):
    name = "导演"
    model = "gpt-4.1-mini"
    temperature = 0.7
    max_tokens = 4000
    max_reflection_rounds = 1

    @property
    def system_prompt(self) -> str:
        return """你是 AI 影视制片厂的**导演**，视觉翻译官与审美决策者。

你将把剧本文字拆解为具体可执行的**镜头语言**，并为视频生成模型（Veo/Sora）编写精准的视觉描述 Prompt。

## 景别代码
ECU(极近景) | CU(近景) | MCU(中近景) | MS(中景) | MLS(中远景) | LS(远景) | ELS(极远景)

## 角度代码
EYE(平视) | LA(仰角) | HA(俯角) | BIRD(鸟瞰) | DUTCH(倾斜)

## 运动代码
STATIC(静止) | PAN(水平摇) | TILT(垂直摇) | DOLLY IN/OUT(推拉轨) | TRACKING(跟随) | HANDHELD(手持) | CRANE(升降)

## Video Prompt 格式
[主体描述] + [动作/状态] + [环境/背景] + [镜头语言] + [光影氛围] + [风格标签]
- 全部用**中文**编写
- 第一句必须描述主体外形（从 character_sheets 调取）
- 具体胜过抽象
- 末尾加统一风格标签

## 输出格式

## SHOT_LIST
[为每个场景生成分镜表，格式：
### Scene X：场景标题
| 镜头 | 景别 | 角度 | 运动 | 内容描述 | 时长 |
|------|------|------|------|---------|------|
| S01-S01 | MS | EYE | STATIC | ... | 4s |
]

## VIDEO_PROMPTS
[为每个镜头编写中文 Prompt，格式：
### Shot S01-S01
**Prompt:** ...
**Negative Prompt:** 模糊的, 低画质, 文字, 水印
]

## DIRECTOR_NOTES
[视觉风格定调、关键场景镜头意图、节奏控制策略]"""

    async def build_user_prompt(self) -> str:
        # 新增强制中文约束
        constraint = "【重要提示】请确保所有输出内容（包括所有标题、标签、术语和 Prompt 内容本身）严格且完全使用中文。"
        script = await self.bb.read(ArtifactType.SCRIPT) or ""
        characters = await self.bb.read(ArtifactType.CHARACTER_SHEETS) or ""

        return f"""请根据以下剧本和角色设定，创作完整的分镜清单和视频生成 Prompt：

## 角色视觉特征（用于 Prompt 一致性）
{characters[:1000]}

{script[:3000]}

{constraint}
请严格按照系统提示中的格式输出三个部分：SHOT_LIST、VIDEO_PROMPTS、DIRECTOR_NOTES。"""

    def reflection_criteria(self) -> str:
        return """分镜清单应满足：
1. 每个场景至少有3个镜头
2. 每个镜头包含景别、角度、运动、内容描述
3. Video Prompt 全部用中文，包含主体描述、环境、镜头语言、风格标签
4. Director Notes 包含视觉风格定调"""

    async def parse_and_publish(self, raw_output: str) -> None:
        sections = {"SHOT_LIST": "", "VIDEO_PROMPTS": "", "DIRECTOR_NOTES": ""}
        current_section = None

        for line in raw_output.split("\n"):
            stripped = line.strip()
            if stripped == "## SHOT_LIST":
                current_section = "SHOT_LIST"
            elif stripped == "## VIDEO_PROMPTS":
                current_section = "VIDEO_PROMPTS"
            elif stripped == "## DIRECTOR_NOTES":
                current_section = "DIRECTOR_NOTES"
            elif current_section:
                sections[current_section] += line + "\n"

        if not sections["SHOT_LIST"]:
            sections["SHOT_LIST"] = raw_output

        await self.bb.publish(ArtifactType.SHOT_LIST, sections["SHOT_LIST"].strip())
        await self.bb.publish(ArtifactType.VIDEO_PROMPTS, sections["VIDEO_PROMPTS"].strip())
        await self.bb.publish(ArtifactType.DIRECTOR_NOTES, sections["DIRECTOR_NOTES"].strip())
