"""
outline_agent.py — 大纲生成 Agent
根据选定的选题生成小说大纲，包括故事梗概、角色设定、章节大纲
"""

from ...core.base_agent import BaseAgent
from ...core.blackboard import ArtifactType


class OutlineAgent(BaseAgent):
    """
    大纲生成 Agent - 将选题转化为完整的小说骨架

    输出包括：
    - 故事梗概（200-300字）
    - 角色设定（3-5名主要角色）
    - 章节大纲（20个章节）
    """
    name = "大纲架构师"
    model = "gpt-4.1-mini"
    temperature = 0.8
    max_tokens = 4000
    max_reflection_rounds = 1

    def __init__(self, blackboard, project_id: str,
                 selected_topic: str = None,
                 model_name=None):
        super().__init__(blackboard, project_id, model_name=model_name)
        self.selected_topic = selected_topic  # 用户选择的选题

    @property
    def system_prompt(self) -> str:
        return """作为10年爆款小说作家，请根据选题生成大纲和角色设定。

避免读者"为了虐而虐"的疲劳感。现在的读者已经厌倦了单纯的"误会、流产、挖肾"老三样，她们需要的是**"逻辑闭环下的无能为力"**和**"双向奔赴中的极致拉扯"**

避免读者"为了爽而爽"的疲劳感。现在的读者已经厌倦了"无脑降智式反派""金手指天降式开挂""男主万能光环式救场""无差别打脸式宣泄"，她们需要的是**"逻辑自洽下的智性爽感"、"强强联合下的势均力敌"、"细节落地的精准打脸"、"成长闭环的价值实现"**

# 输出格式：

## 故事梗概
[200-300字的故事核心梗概，包含：主角身份、核心冲突、情感主线、故事走向]

## 角色设定
### 主角
**姓名**:
**身份**:
**性格特质**:
**内心渴望**:
**内心恐惧**:
**成长弧线**:

### 男主
**姓名**:
**身份**:
**性格特质**:
**与女主关系**:

### 重要配角（2-3人）
[同上格式]

## 章节大纲
[20个章节，每个章节3-5句话描述核心情节]

### 第一章
[情节描述]

### 第二章
[情节描述]

...（以此类推至第二十章）"""

    async def build_user_prompt(self) -> str:
        # 从黑板获取选题创意
        if not self.selected_topic:
            topic_ideas = await self.bb.read(self.project_id, ArtifactType.TOPIC_IDEAS)
            if topic_ideas:
                return f"""请根据以下选题创意，生成完整的小说大纲和角色设定：

{topic_ideas}

请选择其中最有潜力的一个选题（或者结合多个选题的优点），生成20章节的完整大纲。"""
            else:
                return "请生成一个完整的20章节小说大纲（包括故事梗概、角色设定、章节大纲）。"
        else:
            return f"""请根据以下选题，生成完整的20章节小说大纲：

{self.selected_topic}

请严格按照系统提示中的格式输出：故事梗概、角色设定、章节大纲。"""

    def reflection_criteria(self) -> str:
        return """大纲输出应满足：
1. 故事梗概200-300字，包含主角、核心冲突、情感主线
2. 至少有3个角色设定（女主、男主、1-2个配角）
3. 每个角色有：姓名、身份、性格、内心渴望/恐惧
4. 章节大纲包含20个章节，每个章节有清晰的情节描述
5. 避免老套的"误会、流产、挖肾"情节
6. 体现逻辑闭环和强强联合特点"""

    async def parse_and_publish(self, raw_output: str) -> None:
        """解析大纲输出并发布到黑板"""
        await self.bb.publish(
            self.project_id,
            ArtifactType.NOVEL_OUTLINE,
            raw_output.strip()
        )
