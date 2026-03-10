"""
skeleton_diagnostics_agent.py — 骨架诊断 Agent
对初步大纲进行逻辑诊断，并重构生成3个候选骨架
"""

from ...core.base_agent import BaseAgent
from ...core.blackboard import ArtifactType


class SkeletonDiagnosticsAgent(BaseAgent):
    """
    骨架诊断 Agent - 实现逻辑诊断和骨架重构功能

    功能：
    1. 评估现有大纲的逻辑问题
    2. 分析角色设定是否合理
    3. 评估章节节奏和情节张力
    4. 生成3个优化后的候选骨架
    """
    name = "骨架诊断师"
    model = "gpt-4.1-mini"
    temperature = 0.7
    max_tokens = 4000
    max_reflection_rounds = 0

    def __init__(self, blackboard, project_id: str, model_name=None):
        super().__init__(blackboard, project_id, model_name=model_name)

    @property
    def system_prompt(self) -> str:
        return """你是专业的小说编辑和架构师，擅长诊断小说骨架问题并重构优化。

你的任务是对现有小说大纲进行**逻辑诊断**，然后生成**3个优化后的候选骨架**。

# 诊断维度（你需要检查的）：

## 1. 核心逻辑
- 主角动机是否合理？
- 核心冲突是否清晰？
- 情感发展是否有铺垫？
- 结局是否逻辑闭环？

## 2. 角色设定
- 主角人设是否鲜明？
- 男主/女主是否势均力敌（强强）？
- 配角是否有功能性？
- 角色关系是否有张力？

## 3. 节奏与张力
- 开头3秒是否有吸引力？
- 前5章是否建立期待？
- 中期是否有情节拖沓？
- 结局是否爽感充足？

## 4. 避免老套路
- 是否有"误会、流产、挖肾"等老套路？
- 是否有无脑降智的反派？
- 是否有金手指天降式开挂？
- 是否有男主万能光环式救场？

# 输出格式：

## 诊断报告
### 核心问题
[列出3-5个最核心的逻辑/结构问题]

### 优化建议
[给出具体的改进方向]

## 候选骨架一：[方向名称]
### 优化重点
[说明这个版本主要优化了什么]

### 故事梗概
[200-300字]

### 角色调整
[说明角色的调整方向]

### 章节大纲（精简版）
[列出关键转折点，不需要20章全列]

## 候选骨架二：[方向名称]
[同上格式]

## 候选骨架三：[方向名称]
[同上格式]

只输出诊断报告和3个候选骨架，不要有其他解释文字。"""

    async def build_user_prompt(self) -> str:
        # 从黑板获取现有大纲
        outline = await self.bb.read(self.project_id, ArtifactType.NOVEL_OUTLINE)

        if not outline:
            return "请先提供小说大纲，我才能进行诊断和重构。"

        return f"""请对以下小说大纲进行逻辑诊断，并生成3个优化后的候选骨架：

{outline}

请严格按照系统提示中的格式输出：诊断报告 + 3个候选骨架。"""

    def reflection_criteria(self) -> str:
        return """骨架诊断输出应满足：
1. 诊断报告列出3-5个核心问题
2. 生成3个不同方向的候选骨架
3. 每个候选骨架包含：优化重点、故事梗概、角色调整、章节大纲
4. 3个骨架应该有不同的优化方向（如：一个强化冲突，一个优化节奏，一个深化角色）
5. 避免重复老套路"""

    async def parse_and_publish(self, raw_output: str) -> None:
        """解析骨架诊断输出并发布到黑板"""
        await self.bb.publish(
            self.project_id,
            ArtifactType.SKELETON_CANDIDATES,
            raw_output.strip()
        )
