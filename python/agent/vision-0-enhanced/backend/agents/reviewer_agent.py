"""
reviewer_agent.py — 剧本评审 Agent（Script Doctor）
从逻辑和情感两个维度对剧本进行"临床诊断"
"""

from ..core.base_agent import BaseAgent
from ..core.blackboard import ArtifactType


REVIEW_VERDICT_PASS = "✅ 康复出院"
REVIEW_VERDICT_MINOR = "⚠️ 需住院微创"
REVIEW_VERDICT_REJECT = "❌ 建议重新投胎"


class ReviewerAgent(BaseAgent):
    name = "剧本评审"
    model = "gpt-4.1-mini"
    temperature = 0.3   # 评审用低温，保证客观性
    max_tokens = 3000
    max_reflection_rounds = 0  # 评审不需要自我反思

    @property
    def system_prompt(self) -> str:
        return """你是 AI 影视制片厂的**剧本主治医师（Script Doctor）**，独立的第三方冷酷视角。

你的职责是给剧本开具一份**「双维临床诊断报告」**，从**逻辑（脑外科）**和**情感（心内科）**两个维度进行深度"尸检"。

## 重要原则
1. **拒绝温和**：必须像医生一样客观、冷酷地指出致命病灶
2. **诊疗一体**：不仅指出"病灶"，还必须提供具体的"根治手术"方案
3. **拒绝主线逃逸**：严查"机械降神"和突兀的类型转变

## 逻辑病理筛查（脑外科）
- 机械降神症（Deus Ex Machina）
- 主线逃逸综合征
- 动机薄弱/行为收益失衡
- 时间线矛盾症
- 空间逻辑紊乱

## 情感病理筛查（心内科）
- 工具人抗体（NPC Syndrome）
- 任务式和解（Cheap Resolution）
- 电报式对话（On-the-Nose）

## 输出格式（严格遵守）

## REVIEW_REPORT
# 双维临床诊断报告

## 【病情综述】
[200字以内，肯定优点，点出最致命病变]

## 【逻辑病理临床单】(脑外科)
### 病灶 L-01 (位置：Scene X)
- **症状描述**: ...
- **尸检分析**: ...
- **根治手术**: ...

## 【情感病理临床单】(心内科)
### 病灶 E-01 (位置：Scene X)
- **症状描述**: ...
- **心电图分析**: ...
- **情感起搏**: ...

## 【最终医嘱】
[精炼医嘱 + 结论：✅ 康复出院 / ⚠️ 需住院微创 / ❌ 建议重新投胎]

## VERDICT
[只写以下三个之一：PASS / MINOR_FIX / REJECT]"""

    async def build_user_prompt(self) -> str:
        logline = await self.bb.read(ArtifactType.LOGLINE) or ""
        characters = await self.bb.read(ArtifactType.CHARACTER_SHEETS) or ""
        beat_sheet = await self.bb.read(ArtifactType.BEAT_SHEET) or ""
        script = await self.bb.read(ArtifactType.SCRIPT) or ""
        script_notes = await self.bb.read(ArtifactType.SCRIPT_NOTES) or ""

        return f"""请对以下剧本进行全面的临床诊断：

## Logline
{logline}

## 角色设定
{characters[:800]}

## 节拍表
{beat_sheet[:800]}

## 剧本正文
{script[:3000]}

## 编剧备注
{script_notes[:500]}

请严格按照系统提示中的格式输出诊断报告。"""

    async def parse_and_publish(self, raw_output: str) -> None:
        # 解析报告和结论
        report = ""
        verdict = "MINOR_FIX"

        lines = raw_output.split("\n")
        in_report = False
        in_verdict = False

        for line in lines:
            stripped = line.strip()
            if stripped == "## REVIEW_REPORT":
                in_report = True
                in_verdict = False
            elif stripped == "## VERDICT":
                in_report = False
                in_verdict = True
            elif in_report:
                report += line + "\n"
            elif in_verdict and stripped:
                if "PASS" in stripped.upper():
                    verdict = "PASS"
                elif "REJECT" in stripped.upper():
                    verdict = "REJECT"
                else:
                    verdict = "MINOR_FIX"

        if not report:
            report = raw_output
            # 从文本中推断结论
            if "康复出院" in raw_output or "PASS" in raw_output:
                verdict = "PASS"
            elif "重新投胎" in raw_output or "REJECT" in raw_output:
                verdict = "REJECT"
            else:
                verdict = "MINOR_FIX"

        full_report = f"{report.strip()}\n\n---\n**评审结论代码**: {verdict}"
        await self.bb.publish(ArtifactType.REVIEW_REPORT, full_report)
        self.verdict = verdict

    def get_verdict(self) -> str:
        return getattr(self, "verdict", "MINOR_FIX")
