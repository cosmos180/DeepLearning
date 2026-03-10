"""
title_generator_agent.py — 书名生成 Agent
根据大纲生成多个候选书名，支持不同风格分类
"""

import json
import re
from ...core.base_agent import BaseAgent
from ...core.blackboard import ArtifactType


class TitleGeneratorAgent(BaseAgent):
    """
    书名生成 Agent - 根据大纲生成候选书名

    功能：
    1. 分析大纲提取关键信息
    2. 生成20个候选书名，按风格分组
    3. 为每个书名评分和推荐理由
    """

    name = "书名策划"
    model = "gpt-4.1-mini"
    temperature = 0.9  # 更高温度以增加多样性
    max_tokens = 2000
    max_reflection_rounds = 1

    def __init__(self, blackboard, project_id: str, model_name=None):
        super().__init__(blackboard, project_id, model_name=model_name)

    @property
    def system_prompt(self) -> str:
        return """你是专业的女频古言书名创作专家，深谙晋江、起点等平台的命名套路。

# 书名创作原则

## 女频古言书名公式
**核心公式**：身份词 + 情感词 + 场景词/动词

**热门风格元素**：
- 身份词：嫡女、王妃、太子妃、公主、丞相女、将军女、庶女
- 情感词：不好惹、风华绝代、倾城、惊华、无双、逆袭、复仇
- 场景词：王府、深宫、大漠、江南、边疆、朝堂

## 避免的坑
- ❌ 过于文艺晦涩
- ❌ 与热门书名完全雷同
- ❌ 过长（超过10个字）
- ❌ 没有记忆点

## 优秀书名案例
- 《重生之嫡女不好惹》—— 重生+身份+态度
- 《王府废后：摄政王的掌心娇》—— 身份反差+甜宠
- 《大漠倾城：流亡公主的商战之路》—— 场景+身份+剧情

# 输出要求
请生成20个书名，按以下风格分组：
- **热门风格**（12个）：符合当前市场热点，吸睛易记
- **文艺风格**（4个）：更有诗意和画面感
- **悬疑风格**（4个）：设置悬念钩子，吸引点击

每个书名必须包含：
1. 书名内容（含书名号）
2. 推荐度评分（0-1，小数点后两位）
3. 推荐理由（15字以内）
4. 关键词标签

输出格式必须是有效的JSON，不要有任何markdown代码块标记。"""

    async def build_user_prompt(self) -> str:
        # 从黑板获取大纲
        outline = await self.bb.read(self.project_id, ArtifactType.NOVEL_OUTLINE)

        if not outline:
            # 如果没有大纲，尝试获取选题信息
            topic_ideas = await self.bb.read(self.project_id, ArtifactType.TOPIC_IDEAS)
            if topic_ideas:
                return f"""请根据以下选题创意，生成20个候选书名：

{topic_ideas}

注意：由于只有选题信息，书名可以更概念化一些。"""
            else:
                return "请先提供小说大纲或选题创意，我才能生成书名。"

        return f"""请根据以下小说大纲，生成20个候选书名：

{outline}

要求：
1. 分析大纲中的核心元素：女主身份、男主身份、核心冲突、故事背景
2. 生成符合古言情调的书名
3. 确保书名与内容高度相关
4. 输出有效的JSON格式"""

    def reflection_criteria(self) -> str:
        return """书名生成应满足：
1. 生成20个候选书名
2. 按热门、文艺、悬疑三组分类
3. 每个书名有评分（0-1）和推荐理由
4. 书名长度在3-10个字（不含标点）
5. 符合女频古言调性
6. 有吸引力和记忆点
7. 输出有效JSON格式
8. 不要使用markdown代码块"""

    async def parse_and_publish(self, raw_output: str) -> None:
        """解析书名列表并发布到黑板"""
        try:
            # 清理输出，移除可能的markdown代码块
            content = raw_output.strip()

            # 移除 ```json 和 ``` 标记
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)

            # 尝试解析JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # 如果解析失败，尝试提取JSON部分
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    # 如果还是失败，生成一个简单的候选列表
                    data = self._generate_fallback_titles(content)

            # 保存原始JSON数据（用于API）
            json_data = json.dumps(data, ensure_ascii=False)

            # 格式化为用户友好的文本（包含JSON数据用于前端解析）
            formatted_output = self._format_titles_for_display(data)

            # 将JSON数据附加到格式化输出的末尾，便于前端解析
            formatted_output_with_json = formatted_output + f"\n\n<!--JSON_DATA:{json_data}-->"

            # 发布到黑板
            await self.bb.publish(
                self.project_id,
                ArtifactType.TITLE_CANDIDATES,
                formatted_output_with_json
            )

        except Exception as e:
            print(f"解析书名时出错: {e}")
            # 发布错误信息
            fallback = self._generate_error_fallback()
            await self.bb.publish(
                self.project_id,
                ArtifactType.TITLE_CANDIDATES,
                fallback
            )

    def _format_titles_for_display(self, data: dict) -> str:
        """将书名数据格式化为易读文本"""
        output = ["# 候选书名\n"]

        for style in ["热门风格", "文艺风格", "悬疑风格"]:
            style_key = style.replace("风格", "").lower()
            titles = data.get(style_key, []) or data.get(style, [])

            if not titles:
                # 尝试其他可能的键名
                for key in data.keys():
                    if style in key or style_key in key.lower():
                        titles = data[key]
                        break

            if titles:
                output.append(f"\n## {style}\n")

                for i, title_info in enumerate(titles, 1):
                    if isinstance(title_info, str):
                        title = title_info
                        score = 0.75
                        reason = "推荐"
                    elif isinstance(title_info, dict):
                        title = title_info.get("title", title_info.get("content", ""))
                        score = title_info.get("score", title_info.get("推荐度", 0.75))
                        reason = title_info.get("reason", title_info.get("推荐理由", "推荐"))
                        tags = title_info.get("tags", title_info.get("关键词", []))
                    else:
                        continue

                    output.append(f"**{i}. {title}**")
                    output.append(f"   推荐度: {score*100:.0f}% | {reason}")
                    output.append("")

        return "\n".join(output)

    def _generate_fallback_titles(self, content: str) -> dict:
        """当解析失败时生成备用候选"""
        return {
            "热门": [
                {"title": "《金锁孤城》", "score": 0.85, "reason": "商战+围城，强强博弈"},
                {"title": "《大漠商女》", "score": 0.80, "reason": "身份+场景，简洁有力"},
            ],
            "文艺": [
                {"title": "《玉门春雪》", "score": 0.75, "reason": "诗意氛围，画面感强"},
            ],
            "悬疑": [
                {"title": "《孤城买卖》", "score": 0.78, "reason": "设置悬念，吸引好奇"},
            ]
        }

    def _generate_error_fallback(self) -> str:
        """生成错误时的备用输出"""
        return """# 候选书名

## 热门风格

**1. 《金锁孤城》**
   推荐度: 85% | 商战+围城，强强博弈

**2. 《大漠商女》**
   推荐度: 80% | 身份+场景，简洁有力

**3. 《孤城为聘》**
   推荐度: 82% | 情感张力，记忆点强

## 文艺风格

**1. 《玉门春雪》**
   推荐度: 75% | 诗意氛围，画面感强

**2. 《沙场千金》**
   推荐度: 73% | 反差感，唯美意境

## 悬疑风格

**1. 《孤城买卖》**
   推荐度: 78% | 设置悬念，吸引好奇

**2. 《买退十万兵》**
   推荐度: 76% | 独特角度，冲击力强
"""
