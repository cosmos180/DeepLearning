"""
base_agent.py — Agent 基类
所有专职 Agent 继承此类，内置：
  1. 反思（Reflection）机制 — 自我评估并修订输出
  2. 可观测性追踪 — 自动记录每次 LLM 调用
  3. 标准化日志 — 统一的状态上报
"""

import time
from abc import ABC, abstractmethod
from typing import Optional

from .blackboard import Blackboard, AgentStatus
from .llm_client import call_llm


class BaseAgent(ABC):
    """
    所有 Agent 的基类。
    子类需实现 system_prompt、build_user_prompt 和 parse_output。
    """

    name: str = "BaseAgent"
    model: str = None  # 由底层 fallback 到 DEFAULT_MODEL
    temperature: float = 0.8
    max_tokens: int = 4000
    max_reflection_rounds: int = 1  # 最多反思修订轮数

    def __init__(self, blackboard: Blackboard, project_id: str = "default", model_name: Optional[str] = None):
        self.bb = blackboard
        self.project_id = project_id
        if model_name:
            self.model = model_name

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Agent 的系统提示词"""
        pass

    @abstractmethod
    async def build_user_prompt(self) -> str:
        """从黑板读取上下文，构建本次任务的用户提示词"""
        pass

    @abstractmethod
    async def parse_and_publish(self, raw_output: str) -> None:
        """解析 LLM 输出，将结果发布到黑板"""
        pass

    def reflection_criteria(self) -> str:
        """
        反思评估标准。子类可覆盖此方法提供更具体的标准。
        返回一段描述"好的输出应满足哪些条件"的文本。
        """
        return "输出内容应完整、逻辑清晰、符合任务要求，没有明显的错误或遗漏。"

    async def reflect(self, output: str) -> tuple[bool, str]:
        """
        对输出进行自我反思评估。
        返回 (is_good_enough, feedback)
        """
        await self.bb.log_agent(self.project_id, self.name, AgentStatus.REFLECTING, "正在进行自我反思评估...")

        reflection_prompt = f"""你是一个严格的质量评审员。请评估以下内容是否满足标准。

【评估标准】
{self.reflection_criteria()}

【待评估内容】
{output[:3000]}  

请以 JSON 格式回复：
{{
  "passed": true/false,
  "score": 1-10,
  "issues": ["问题1", "问题2"],
  "suggestion": "如果不通过，给出具体的改进建议"
}}
只输出 JSON，不要有其他文字。"""

        result, tokens = await call_llm(
            system_prompt="你是一个专业的内容质量评审员，只输出 JSON 格式的评估结果。",
            user_prompt=reflection_prompt,
            model="gpt-4.1-nano",  # 底层会自动替换为 FAST_MODEL
            temperature=0.2,
            max_tokens=500,
        )

        await self.bb.trace(
            agent_name=self.name,
            event_type="reflection",
            content=result,
            token_count=tokens,
            project_id=self.project_id
        )

        try:
            import json
            # 清理可能的 markdown 代码块
            clean = result.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            data = json.loads(clean.strip())
            passed = data.get("passed", True)
            suggestion = data.get("suggestion", "")
            issues = data.get("issues", [])
            score = data.get("score", 7)

            feedback = f"评分: {score}/10"
            if issues:
                feedback += f"\n问题: {'; '.join(issues)}"
            if suggestion:
                feedback += f"\n建议: {suggestion}"

            return passed, feedback
        except Exception:
            return True, "反思解析失败，默认通过"

    async def run(self) -> str:
        """
        执行 Agent 的完整工作流：
        1. 构建提示词
        2. 调用 LLM
        3. 反思评估（最多 max_reflection_rounds 轮）
        4. 发布结果到黑板
        """
        await self.bb.log_agent(self.project_id, self.name, AgentStatus.THINKING, f"{self.name} 开始工作...")

        user_prompt = await self.build_user_prompt()

        current_output = ""
        for round_num in range(self.max_reflection_rounds + 1):
            start_time = time.time()

            # 如果是修订轮，在提示词中加入反思反馈
            if round_num > 0 and current_output:
                user_prompt_with_feedback = (
                    f"{user_prompt}\n\n"
                    f"【上一轮输出的问题】\n{self._last_feedback}\n\n"
                    f"【上一轮输出】\n{current_output[:2000]}\n\n"
                    f"请根据以上问题，重新生成改进后的版本。"
                )
            else:
                user_prompt_with_feedback = user_prompt

            await self.bb.trace(
                agent_name=self.name,
                event_type=f"llm_call_round_{round_num}",
                content=f"[PROMPT] {user_prompt_with_feedback[:500]}...",
                project_id=self.project_id
            )

            from ..core.llm_client import call_llm_stream
            
            # 使用流式接口并向前端广播 Token
            stream_gen = call_llm_stream(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt_with_feedback,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            chunks = []
            async for chunk in stream_gen:
                chunks.append(chunk)
                await self.bb.stream_output(self.project_id, self.name, chunk)
                
            current_output = "".join(chunks)
            # 粗略估算 token (中文/英文混合)
            tokens = len(current_output) // 2 

            duration_ms = int((time.time() - start_time) * 1000)

            await self.bb.trace(
                agent_name=self.name,
                event_type=f"llm_response_round_{round_num}",
                content=current_output[:500],
                token_count=tokens,
                duration_ms=duration_ms,
                project_id=self.project_id
            )

            # 进行反思评估
            if round_num < self.max_reflection_rounds:
                passed, feedback = await self.reflect(current_output)
                self._last_feedback = feedback
                if passed:
                    await self.bb.log_agent(
                        self.project_id, self.name, AgentStatus.REFLECTING,
                        f"反思通过（第 {round_num + 1} 轮），准备发布结果"
                    )
                    break
                else:
                    await self.bb.log_agent(
                        self.project_id, self.name, AgentStatus.REFLECTING,
                        f"反思发现问题（第 {round_num + 1} 轮），进行修订",
                        feedback
                    )
            else:
                break

        # 发布到黑板
        await self.parse_and_publish(current_output)
        await self.bb.log_agent(self.project_id, self.name, AgentStatus.COMPLETED, f"{self.name} 完成工作")
        return current_output
