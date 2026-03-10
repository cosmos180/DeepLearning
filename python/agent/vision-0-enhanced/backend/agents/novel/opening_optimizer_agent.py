"""
opening_optimizer_agent.py — 开头优化 Agent
生成建议的开篇几句话，帮助优化开头和第一章
"""

from ...core.base_agent import BaseAgent
from ...core.blackboard import ArtifactType


class OpeningOptimizerAgent(BaseAgent):
    """
    开头优化 Agent - 生成吸引人的开篇

    功能：
    1. 分析现有开头的优缺点
    2. 生成多个版本的开篇建议
    3. 提供具体的优化方向
    """
    name = "开头优化师"
    model = "gpt-4.1-mini"
    temperature = 0.8
    max_tokens = 2000
    max_reflection_rounds = 0

    def __init__(self, blackboard, project_id: str, model_name=None):
        super().__init__(blackboard, project_id, model_name=model_name)

    @property
    def system_prompt(self) -> str:
        return """你是专业的网文编辑，擅长打造"黄金开头"。

你的任务是分析现有开头的优缺点，并生成多个优化版本的开篇建议。

# 好开头的标准：

## 黄金3秒（第一句话）
- 必须有强烈的视觉/听觉/情绪冲击
- 立即建立场景、冲突或悬念
- 让读者无法划走

## 受众筛选（前30秒）
- 快速建立角色关系
- 快速交代背景前提
- 埋下期待或悬念

## 期待Buff（前1分钟）
- 让读者想知道"接下来会怎样"
- 建立情感连接或好奇

# 风格类型：
根据小说题材，开头风格可能包括：
- **冷感克制**：强强文，智性博弈
- **激烈冲突**：狗血文，撕逼爽感
- **暧昧拉扯**：甜宠文，氛围感

# 输出格式：

## 现有开头分析
[分析当前开头的优缺点]

## 开篇建议（3个版本）

### 版本一：[风格定位]
[3-5句话的开篇，符合黄金3秒标准]

### 版本二：[风格定位]
[3-5句话的开篇，不同切入点]

### 版本三：[风格定位]
[3-5句话的开篇，不同切入点]

## 优化建议
[具体的、可操作的改进方向]

请严格遵循以上格式输出，不要有其他解释文字。"""

    async def build_user_prompt(self) -> str:
        # 获取大纲和第一章内容
        outline = await self.bb.read(self.project_id, ArtifactType.NOVEL_OUTLINE)
        skeleton = await self.bb.read(self.project_id, ArtifactType.SELECTED_SKELETON)
        chapter = await self.bb.read(self.project_id, ArtifactType.CHAPTER_CONTENT)

        skeleton_or_outline = skeleton or outline or ""

        if not chapter:
            return """请先提供小说骨架/大纲和第一章内容，我才能生成开篇建议。

当前没有找到第一章内容。"""

        # 获取评审意见作为参考
        review = await self.bb.read(self.project_id, ArtifactType.REVIEW_COMMENTS)
        review_hint = ""
        if review:
            review_hint = f"\n\n【参考评审意见】\n{review[:1000]}"

        return f"""请根据以下骨架和第一章内容，生成开篇优化建议：

【小说骨架/大纲】
{skeleton_or_outline}

【第一章内容】
{chapter[:3000]}{review_hint}

请严格按照系统提示中的格式输出：现有开头分析 + 3个开篇建议版本 + 优化建议。"""

    def reflection_criteria(self) -> str:
        return """开篇优化输出应满足：
1. 分析现有开头的优缺点
2. 提供3个不同版本的开篇建议
3. 每个版本3-5句话，符合黄金3秒标准
4. 体现不同的风格定位
5. 给出可操作的优化建议"""

    async def parse_and_publish(self, raw_output: str) -> None:
        """解析开篇建议并发布到黑板"""
        await self.bb.publish(
            self.project_id,
            ArtifactType.OPENING_SUGGESTION,
            raw_output.strip()
        )
