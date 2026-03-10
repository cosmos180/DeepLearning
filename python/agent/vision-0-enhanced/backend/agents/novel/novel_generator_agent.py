"""
novel_generator_agent.py — 小说生成 Agent
根据优化后的骨架生成小说正文内容
"""

from ...core.base_agent import BaseAgent
from ...core.blackboard import ArtifactType


class NovelGeneratorAgent(BaseAgent):
    """
    小说生成 Agent - 根据骨架生成小说正文

    功能：
    1. 根据大纲生成指定章节的正文
    2. 支持单章生成或全文生成
    3. 保持角色一致性和情节连贯性
    """
    name = "小说作家"
    model = "gpt-4.1-mini"
    temperature = 0.85
    max_tokens = 3000
    max_reflection_rounds = 1

    def __init__(self, blackboard, project_id: str,
                 chapter_number: int = None,
                 generate_all: bool = False,
                 model_name=None):
        super().__init__(blackboard, project_id, model_name=model_name)
        self.chapter_number = chapter_number  # 指定章节号
        self.generate_all = generate_all  # 是否生成全部章节

    @property
    def system_prompt(self) -> str:
        return """你是专业的小说作家，擅长创作引人入胜的网文。

# 写作原则：

## 去AI味
- 避免过于完美的解决方案
- 避免道德说教式结局
- 避免角色情绪过于单一
- 加入真实的生活细节和感官描写

## 冲突要真实
- 内心冲突比外部冲突更重要
- 确保主角有真实的弱点和成长弧线
- 情感发展要有铺垫，不能突兀

## 视觉化思维
- 每个场景脑中要能浮现出具体画面
- 注重环境、氛围、动作描写
- 多用"展示"而非"讲述"

## 节奏把控
- 开头3秒必须有吸引力
- 每章结尾留钩子
- 对话推动情节，不要流水账

# 避免老套路：
- "误会、流产、挖肾"老三样
- 无脑降智式反派
- 金手指天降式开挂
- 男主万能光环式救场

# 输出格式：
直接输出小说正文，不要有任何标题、说明或解释文字。
正文应该以场景切入，让读者立即进入故事。"""

    async def build_user_prompt(self) -> str:
        # 从黑板获取骨架
        skeleton = await self.bb.read(self.project_id, ArtifactType.SELECTED_SKELETON)
        if not skeleton:
            # 如果没有选中的骨架，使用原始大纲
            skeleton = await self.bb.read(self.project_id, ArtifactType.NOVEL_OUTLINE)

        if not skeleton:
            return "请先提供小说骨架或大纲，我才能生成正文。"

        if self.generate_all:
            return f"""请根据以下骨架，生成完整的20章节小说正文：

{skeleton}

请按照章节顺序，逐一输出每章正文。每章应该在1500-2500字之间。"""
        elif self.chapter_number is not None:
            return f"""请根据以下骨架，生成第{self.chapter_number}章的正文：

{skeleton}

本章应该在1500-2500字之间，请直接输出正文内容，不要有章节标题。"""
        else:
            return f"""请根据以下骨架，生成第一章的正文：

{skeleton}

本章应该在1500-2500字之间，请直接输出正文内容，不要有章节标题。"""

    def reflection_criteria(self) -> str:
        return """小说正文应满足：
1. 以场景切入，开头3秒有吸引力
2. 字数在1500-2500字之间
3. 对话推动情节，不要流水账
4. 有真实的生活细节和感官描写
5. 角色性格一致，行为有逻辑
6. 避免老套路（误会、流产、挖肾）
7. 章节结尾留钩子，吸引继续阅读
8. 全文使用中文输出"""

    async def parse_and_publish(self, raw_output: str) -> None:
        """解析小说正文并发布到黑板"""
        if self.generate_all:
            # 生成全部章节 - 自动添加markdown标题格式
            import re
            content = raw_output.strip()
            lines = content.split('\n')
            formatted_lines = []

            for line in lines:
                stripped = line.strip()
                # 如果行包含"第X章"但不是markdown格式，添加#前缀
                if stripped and not stripped.startswith('#'):
                    if re.match(r'^第[一二三四五六七八九十百千0-9]+章', stripped):
                        formatted_lines.append(f"# {stripped}")
                    else:
                        formatted_lines.append(line)
                else:
                    formatted_lines.append(line)

            await self.bb.publish(
                self.project_id,
                ArtifactType.ALL_CHAPTERS,
                '\n'.join(formatted_lines)
            )
        elif self.chapter_number is not None:
            # 单独章节 - 添加markdown标题
            await self.bb.publish(
                self.project_id,
                ArtifactType.CHAPTER_CONTENT,  # 也发布到通用章节内容
                f"# 第{self.chapter_number}章\n\n{raw_output.strip()}"
            )
        else:
            # 默认第一章
            await self.bb.publish(
                self.project_id,
                ArtifactType.CHAPTER_CONTENT,
                f"# 第一章\n\n{raw_output.strip()}"
            )
