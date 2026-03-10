"""
reviewer_agent.py — 评审 Agent
毒舌评价，评估读者留存率，分析弃读点
"""

from ...core.base_agent import BaseAgent
from ...core.blackboard import ArtifactType


class NovelReviewerAgent(BaseAgent):
    """
    评审 Agent - 毒舌辣评，评估读者留存

    功能：
    1. 分析开头黄金3秒
    2. 评估30秒内角色关系和背景设定
    3. 分析1分钟、3分钟内的弃读点
    4. 给出具体的改进建议
    """
    name = "毒舌评审"
    model = "gpt-4.1-mini"
    temperature = 0.6
    max_tokens = 3000
    max_reflection_rounds = 0

    def __init__(self, blackboard, project_id: str, model_name=None):
        super().__init__(blackboard, project_id, model_name=model_name)

    @property
    def system_prompt(self) -> str:
        return """你作为10年经验的毒舌辣评的小说发行方选稿人，评估有声小说稿件是否能签约。

你的工作流程：
1. 首先评估小说的标签和目标受众
2. 然后模拟目标读者的听书流分析
3. 给出毒舌挑刺

# 听书流分析维度：

## 黄金3秒（物理抓手）
- 开头第一句话是否有冲击力？
- 是否立即建立场景/冲突/悬念？
- 读者会在前3秒划走吗？

## 30秒分析（受众筛选）
- 30秒内能让目标听众知道角色关系吗？
- 30秒内能让目标听众了解背景前提吗？
- 30秒内有没有在目标听众心中种下期望或悬念？
- 读者会继续看下去吗？

## 1分钟分析（留存测试）
- 1分钟内，用户会弃读吗？
- 如果会，为什么？
- 如果不会，什么在吸引ta？

## 3分钟分析（长线留存）
- 3分钟内，用户有哪些弃读点？
- 哪些地方节奏拖沓？
- 哪些地方逻辑出戏？

# 输出格式：

## 标签与受众
**题材标签**: [如：古言/强强/商战]
**目标受众**: [如：25-35岁女性，喜欢大女主搞钱]
**核心爽点**: [一句话概括]

## 听书流诊断

### 黄金3秒
[评分/10] [具体分析] [如果不及格，给出修改建议]

### 30秒分析
[评分/10] [角色关系分析] [背景前提分析] [期望/悬念分析]

### 1分钟分析
[评分/10] [是否弃读] [为什么]

### 3分钟分析
[评分/10] [弃读点列表]

## 毒舌挑刺
[列出3-5个最刺痛的问题，用毒舌的语气]

## 改进建议
[给出具体的、可操作的修改建议]

请严格遵循以上格式输出，不要有其他解释文字。"""

    async def build_user_prompt(self) -> str:
        # 从黑板获取需要评审的内容
        content = await self.bb.read(self.project_id, ArtifactType.CHAPTER_CONTENT)
        if not content:
            content = await self.bb.read(self.project_id, ArtifactType.ALL_CHAPTERS)

        if not content:
            return "请先提供小说正文（第一章或全部章节），我才能进行评审。"

        return f"""请对以下小说正文进行毒舌评审：

{content[:5000]}

请严格按照系统提示中的格式输出评审报告。"""

    def reflection_criteria(self) -> str:
        return """评审报告应满足：
1. 给出明确的题材标签和目标受众
2. 对黄金3秒、30秒、1分钟、3分钟都有评分和分析
3. 毒舌挑刺部分要尖锐、具体、有针对性
4. 改进建议要可操作
5. 全文使用中文"""

    async def parse_and_publish(self, raw_output: str) -> None:
        """解析评审报告并发布到黑板"""
        await self.bb.publish(
            self.project_id,
            ArtifactType.REVIEW_COMMENTS,
            raw_output.strip()
        )
