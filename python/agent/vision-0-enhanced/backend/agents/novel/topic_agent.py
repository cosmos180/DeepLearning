"""
topic_agent.py — 选题 Agent
根据用户指定的题材、风格、女主身份等，批量生成高概念小说选题
"""

from ...core.base_agent import BaseAgent
from ...core.blackboard import ArtifactType


class TopicAgent(BaseAgent):
    """
    选题 Agent - 生成小说创意选题

    支持多种题材：
    - 古言：大漠商战、强强博弈、极致羁绊
    - 现言：都市、职场、豪门
    - 仙侠：修真、神魔、师徒
    - 末世：丧尸、异能、生存
    """
    name = "选题策划"
    model = "gpt-4.1-mini"
    temperature = 0.9
    max_tokens = 4000
    max_reflection_rounds = 0  # 选题创意类不需要反思

    def __init__(self, blackboard, project_id: str,
                 genre: str = "古言",
                 audience: str = "女频",
                 tone: str = "爽文",
                 female_lead_identity: str = "流亡公主",
                 model_name=None):
        super().__init__(blackboard, project_id, model_name=model_name)
        self.genre = genre  # 古言/现言/仙侠/末世
        self.audience = audience  # 女频/男频
        self.tone = tone  # 爽文/虐恋
        self.female_lead_identity = female_lead_identity  # 女主身份

    @property
    def system_prompt(self) -> str:
        # 根据题材选择不同的提示词模板
        if self.genre == "古言":
            return self._get_historical_prompt()
        else:
            return self._get_general_prompt()

    def _get_historical_prompt(self) -> str:
        return """# Role: 晋江/古言大神策划 (Platinum Writer - Epic Historical Edition)

# Goal:
请基于用户提供的【女主身份 (X轴)】，通过**"多维随机碰撞"**策略，批量生成 10 个符合**"女频古言·强强·大漠商战"**题材的爆款高概念梗概。

# The Aesthetic (核心调性):
1. **大格局 (Epic)**: 拒绝宅斗，战场是丝绸之路、两国边境、军营与商会。
2. **强强 (Power Couple)**: 男女主必须势均力敌（智力/武力/势力），是对手也是情人。
3. **商战 (Trade War)**: 用金钱扼杀战争，用粮草控制皇权（古代经济战）。
4. **美学 (Atmosphere)**: 关键词包括：大漠孤烟、红衣烈马、边关冷月、金镶玉、弯刀。

# The X-Axis (原点):
**女主身份**: [由用户提供]

# The Y-Axis Matrix (5大古言变量库):
请在生成每一个创意时，**随机抽取**以下 2-3 个维度进行组合 (叠Buff)：

1. **【CP 强强博弈】(The Rival)**:
   - (如: 敌国战神将军、控制西域经济的神秘城主、双面间谍皇子、杀手阁主...)
2. **【极致羁绊/禁忌】(The Bond)**:
   - (如: 质子与监视者、亡国奴与征服者、杀父仇人、政治联姻(先婚后爱)、双重马甲掉马...)
3. **【商战/权谋金手指】(The Edge)**:
   - (如: 穿越自带现代经济学(搞垄断/货币战争)、拥有私兵/情报网、能听懂兽语(控制战马)、过目不忘的账房技能...)
4. **【国仇家恨/绝境】(The Stakes)**:
   - (如: 全族被灭复仇、身中奇毒需解药、必须在30天内筹集百万军饷、背负叛国罪名...)
5. **【大漠/战争奇观】(The Spectacle)**:
   - (如: 孤城围困战、沙尘暴求生、丝绸之路贸易阻断、瘟疫封锁、夺嫡之战...)

# Algorithm (碰撞算法):
对于每一个方案：
1. **固定 X** (女主)。
2. **随机 Roll 点**: 从 Y轴 5 个库中随机抽取 2 到 3 个标签。
3. **强制融合**: 将 X + 标签A + 标签B 融合成一个包含**"商业博弈"**与**"爱恨拉扯"**的故事核心。
4. **生成书名**: 必须有古言史诗感（如《江山为聘》《大漠谣》风格）。

# Output Format:
请输出表格：
| 序号 | 抽中的Buff组合 (X + Y1 + Y2...) | 书名 (暂定) | 一句话高概念梗概 (Logline) | 核心爽点/看点 |

只输出表格，不要有其他解释文字。"""

    def _get_general_prompt(self) -> str:
        return f"""你作为10年经验的小说发行方的{self.genre} {self.audience} {self.tone}网文小说的选稿约稿人，向我(合作多年的爆款小说作家)给出选题思路选项给我挑选：

避免读者"为了虐而虐"的疲劳感。现在的读者已经厌倦了单纯的"误会、流产、挖肾"老三样，她们需要的是**"逻辑闭环下的无能为力"**和**"双向奔赴中的极致拉扯"**

避免读者"为了爽而爽"的疲劳感。现在的读者已经厌倦了"无脑降智式反派""金手指天降式开挂" "男主万能光环式救场""无差别打脸式宣泄"，她们需要的是**"逻辑自洽下的智性爽感"、"强强联合下的势均力敌"、"细节落地的精准打脸"、"成长闭环的价值实现"**

请给出你的 10 个选题思路选项，格式如下：
| 序号 | 书名 | 一句话高概念梗概 | 核心爽点/看点 |

只输出表格，不要有其他解释文字。"""

    async def build_user_prompt(self) -> str:
        if self.genre == "古言":
            return f"""请为以下女主身份生成 10 个古言大漠商战题材的选题：

**女主身份**: {self.female_lead_identity}

请严格按照系统提示中的格式输出表格。"""
        else:
            return f"""请为我生成 10 个 {self.genre} {self.audience} {self.tone} 题材的选题思路：

**女主身份参考**: {self.female_lead_identity}

请严格按照系统提示中的格式输出表格。"""

    def reflection_criteria(self) -> str:
        return """选题输出应满足：
1. 至少生成 10 个不同的选题
2. 每个选题包含：序号、书名、高概念梗概、核心爽点
3. 梗概必须包含主角、核心冲突、目标、阻碍四要素
4. 避免老套的"误会、流产、挖肾"情节
5. 体现"逻辑闭环"和"强强联合"的特点"""

    async def parse_and_publish(self, raw_output: str) -> None:
        """解析选题输出并发布到黑板"""
        await self.bb.publish(
            self.project_id,
            ArtifactType.TOPIC_IDEAS,
            raw_output.strip()
        )
