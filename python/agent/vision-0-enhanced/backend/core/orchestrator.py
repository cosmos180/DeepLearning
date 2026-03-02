"""
orchestrator.py — 动态调度器（Orchestrator）
实现工作流状态机，支持并行 Agent 调度和动态路由
"""

import asyncio
from typing import Optional

from .blackboard import Blackboard, WorkflowStatus, AgentStatus, ArtifactType
from ..agents.creator_agent import CreatorAgent
from ..agents.screenwriter_agent import ScreenwriterAgent
from ..agents.reviewer_agent import ReviewerAgent
from ..agents.director_agent import DirectorAgent
from ..agents.art_director_agent import ArtDirectorAgent


# 工作流步骤定义
STEP_INIT = "init"
STEP_CREATION = "creation"           # 原著作者工作
STEP_PARALLEL_DEV = "parallel_dev"   # 编剧 + 艺术总监并行
STEP_REVIEW = "review"               # 剧本评审
STEP_REVISION = "revision"           # 剧本修订（如评审不通过）
STEP_DIRECTION = "direction"         # 导演分镜
STEP_COMPLETED = "completed"
STEP_FAILED = "failed"

MAX_REVISION_ROUNDS = 2  # 最多修订轮数


class Orchestrator:
    """
    动态工作流调度器。
    核心改进：
    1. 并行化：编剧和艺术总监同时工作
    2. 动态路由：根据评审结果决定是否进入修订循环
    3. 状态机：每个步骤有明确的状态转换
    4. 检查点：每个步骤完成后保存状态
    """

    def __init__(self, blackboard: Blackboard):
        self.bb = blackboard
        self.project_id = "default"

    async def run(self, seed: str, target_duration: str = "30分钟短片",
                  style: str = "科幻+温情", agent_models: dict = None) -> dict:
        """
        执行完整的影视创作工作流。
        返回最终产出物摘要。
        """
        if agent_models is None:
            agent_models = {}

        await self.bb.clear_all()
        await self.bb.set_workflow_state(
            self.project_id, WorkflowStatus.RUNNING,
            current_step=STEP_INIT,
            seed=seed, target_duration=target_duration, style=style
        )

        try:
            # ── 步骤 1：原著作者创作故事圣经 ──────────────────────────────
            await self._update_step(STEP_CREATION)
            creator_model = agent_models.get("creator")
            creator = CreatorAgent(self.bb, self.project_id, seed, target_duration, style, model_name=creator_model)
            await creator.run()

            # ── 步骤 2：编剧 + 艺术总监并行工作 ──────────────────────────
            await self._update_step(STEP_PARALLEL_DEV)
            await self.bb.log_agent(
                "调度器", AgentStatus.THINKING,
                "启动并行阶段：编剧 + 艺术总监同时工作..."
            )

            screenwriter_model = agent_models.get("screenwriter")
            art_director_model = agent_models.get("art_director")
            screenwriter = ScreenwriterAgent(self.bb, self.project_id, model_name=screenwriter_model)
            art_director = ArtDirectorAgent(self.bb, self.project_id, model_name=art_director_model)

            # asyncio.gather 实现真正的并行
            await asyncio.gather(
                screenwriter.run(),
                art_director.run(),
            )

            await self.bb.log_agent(
                "调度器", AgentStatus.THINKING,
                "并行阶段完成，编剧和艺术总监均已提交成果"
            )

            # ── 步骤 3：剧本评审（含修订循环）────────────────────────────
            revision_count = 0
            reviewer_model = agent_models.get("reviewer")
            while revision_count <= MAX_REVISION_ROUNDS:
                await self._update_step(STEP_REVIEW, iteration_count=revision_count)
                reviewer = ReviewerAgent(self.bb, self.project_id, model_name=reviewer_model)
                await reviewer.run()
                verdict = reviewer.get_verdict()

                await self.bb.log_agent(
                    "调度器", AgentStatus.THINKING,
                    f"评审结论: {verdict}（第 {revision_count + 1} 轮）"
                )

                if verdict == "PASS":
                    await self.bb.log_agent(
                        "调度器", AgentStatus.THINKING, "剧本通过评审，进入导演阶段"
                    )
                    break
                elif verdict == "REJECT" and revision_count >= MAX_REVISION_ROUNDS:
                    await self.bb.log_agent(
                        "调度器", AgentStatus.THINKING,
                        f"已达最大修订轮数 ({MAX_REVISION_ROUNDS})，强制进入导演阶段"
                    )
                    break
                else:
                    revision_count += 1
                    await self._update_step(STEP_REVISION, iteration_count=revision_count)
                    await self.bb.log_agent(
                        "调度器", AgentStatus.THINKING,
                        f"剧本需要修订（第 {revision_count} 轮），重新召唤编剧..."
                    )
                    # 重新运行编剧（会读取评审报告作为上下文）
                    revised_screenwriter = ScreenwriterAgent(self.bb, self.project_id, model_name=screenwriter_model)
                    await revised_screenwriter.run()

            # ── 步骤 4：导演分镜 ──────────────────────────────────────────
            await self._update_step(STEP_DIRECTION)
            director_model = agent_models.get("director")
            director = DirectorAgent(self.bb, self.project_id, model_name=director_model)
            await director.run()

            # ── 完成 ──────────────────────────────────────────────────────
            await self.bb.set_workflow_state(
                self.project_id, WorkflowStatus.COMPLETED,
                current_step=STEP_COMPLETED
            )
            await self.bb.log_agent(
                "调度器", AgentStatus.COMPLETED,
                "🎬 所有制作阶段完成！影视项目已就绪。"
            )

            return await self._build_summary()

        except Exception as e:
            await self.bb.set_workflow_state(
                self.project_id, WorkflowStatus.FAILED,
                current_step=STEP_FAILED
            )
            await self.bb.log_agent(
                "调度器", AgentStatus.FAILED,
                f"工作流执行失败: {str(e)}"
            )
            raise

    async def _update_step(self, step: str, iteration_count: int = 0):
        """更新当前工作流步骤"""
        step_names = {
            STEP_CREATION: "原著作者：创作故事圣经",
            STEP_PARALLEL_DEV: "并行开发：编剧 + 艺术总监",
            STEP_REVIEW: "剧本评审",
            STEP_REVISION: "剧本修订",
            STEP_DIRECTION: "导演：分镜与视频 Prompt",
            STEP_COMPLETED: "制作完成",
        }
        display = step_names.get(step, step)
        if iteration_count > 0:
            display += f"（第 {iteration_count} 轮）"

        await self.bb.set_workflow_state(
            self.project_id, WorkflowStatus.RUNNING,
            current_step=display,
            iteration_count=iteration_count
        )
        await self.bb.log_agent(
            "调度器", AgentStatus.THINKING,
            f"进入步骤：{display}"
        )

    async def _build_summary(self) -> dict:
        """构建最终产出物摘要"""
        artifacts = await self.bb.read_all()
        summary = {}
        for key, val in artifacts.items():
            content = val.get("content", "")
            summary[key] = {
                "version": val.get("version", 1),
                "preview": content[:200] + "..." if len(content) > 200 else content,
                "length": len(content),
            }
        return summary
