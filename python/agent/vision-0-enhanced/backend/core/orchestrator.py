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
    5. 灵活启动：支持从中间步骤开始，跳过前置步骤
    """

    def __init__(self, blackboard: Blackboard):
        self.bb = blackboard
        self.project_id = "default"
        self._seed = ""
        self._target_duration = "30分钟短片"
        self._style = "科幻+温情"
        self._popular_elements = []
        self._agent_models = {}

    async def run(self, seed: str = "", target_duration: str = "30分钟短片",
                  style: str = "科幻+温情", popular_elements: list = None,
                  agent_models: dict = None,
                  start_from_step: str = None, artifacts: dict = None) -> dict:
        """
        执行影视创作工作流。
        start_from_step: 从哪个步骤开始（None 表示从头开始）
        artifacts: 手动传入的产出物（用于跳过前置步骤）
        返回最终产出物摘要。
        """
        if agent_models is None:
            agent_models = {}
        if artifacts is None:
            artifacts = {}

        self._seed = seed
        self._target_duration = target_duration
        self._style = style
        self._popular_elements = popular_elements or []
        self._agent_models = agent_models

        # 清理并设置初始状态
        await self.bb.delete_project(self.project_id)

        # 如果有预置产出物，加载到黑板
        if artifacts:
            await self._load_artifacts(artifacts)
            await self.bb.log_agent(
                self.project_id, "调度器", AgentStatus.THINKING,
                f"已加载 {len(artifacts)} 个预置产出物"
            )

        await self.bb.set_workflow_state(
            self.project_id, WorkflowStatus.RUNNING,
            current_step=STEP_INIT,
            seed=seed, target_duration=target_duration, style=style
        )

        try:
            # 根据起始步骤决定执行路径
            if start_from_step is None or start_from_step == STEP_CREATION:
                # 完整流程：从创作开始
                await self._run_creation()
                await self._run_parallel_dev()
                await self._run_review_cycle()
                await self._run_direction()
            elif start_from_step == STEP_PARALLEL_DEV:
                # 跳过创作，从并行开发开始
                await self._run_parallel_dev()
                await self._run_review_cycle()
                await self._run_direction()
            elif start_from_step == STEP_REVIEW:
                # 跳过创作和并行开发，从评审开始
                await self._run_review_cycle()
                await self._run_direction()
            elif start_from_step == STEP_DIRECTION:
                # 跳过所有前置步骤，只执行导演
                await self._run_direction()
            else:
                raise ValueError(f"Unknown start_from_step: {start_from_step}")

            # ── 完成 ──────────────────────────────────────────────────────
            # 自动保存生成的草稿到编辑器存储路径，供用户在工作台无缝查看
            await self._save_to_documents()

            await self.bb.set_workflow_state(
                self.project_id, WorkflowStatus.COMPLETED,
                current_step=STEP_COMPLETED
            )
            await self.bb.log_agent(
                self.project_id, "调度器", AgentStatus.COMPLETED,
                "🎬 所有制作阶段完成！影视项目已就绪。"
            )

            return await self._build_summary()

        except Exception as e:
            await self.bb.set_workflow_state(
                self.project_id, WorkflowStatus.FAILED,
                current_step=STEP_FAILED
            )
            await self.bb.log_agent(
                self.project_id, "调度器", AgentStatus.FAILED,
                f"工作流执行失败: {str(e)}"
            )
            raise

    async def _load_artifacts(self, artifacts: dict[str, str]):
        """加载预置产出物到黑板"""
        await self.bb.publish_many(self.project_id, artifacts)

    async def _run_creation(self):
        """步骤 1：原著作者创作故事圣经"""
        await self._update_step(STEP_CREATION)
        creator_model = self._agent_models.get("creator")
        creator = CreatorAgent(
            self.bb, self.project_id, self._seed,
            self._target_duration, self._style,
            popular_elements=self._popular_elements, model_name=creator_model
        )
        await creator.run()

    async def _run_parallel_dev(self):
        """步骤 2：编剧 + 艺术总监并行工作"""
        await self._update_step(STEP_PARALLEL_DEV)
        await self.bb.log_agent(
            self.project_id, "调度器", AgentStatus.THINKING,
            "启动并行阶段：编剧 + 艺术总监同时工作..."
        )

        screenwriter_model = self._agent_models.get("screenwriter")
        art_director_model = self._agent_models.get("art_director")
        screenwriter = ScreenwriterAgent(self.bb, self.project_id, model_name=screenwriter_model)
        art_director = ArtDirectorAgent(self.bb, self.project_id, model_name=art_director_model)

        # asyncio.gather 实现真正的并行
        await asyncio.gather(
            screenwriter.run(),
            art_director.run(),
        )

        await self.bb.log_agent(
            self.project_id, "调度器", AgentStatus.THINKING,
            "并行阶段完成，编剧和艺术总监均已提交成果"
        )

    async def _run_review_cycle(self):
        """步骤 3：剧本评审（含修订循环）"""
        revision_count = 0
        reviewer_model = self._agent_models.get("reviewer")
        screenwriter_model = self._agent_models.get("screenwriter")

        while revision_count <= MAX_REVISION_ROUNDS:
            await self._update_step(STEP_REVIEW, iteration_count=revision_count)
            reviewer = ReviewerAgent(self.bb, self.project_id, model_name=reviewer_model)
            await reviewer.run()
            verdict = reviewer.get_verdict()

            await self.bb.log_agent(
                self.project_id, "调度器", AgentStatus.THINKING,
                f"评审结论: {verdict}（第 {revision_count + 1} 轮）"
            )

            if verdict == "PASS":
                await self.bb.log_agent(
                    self.project_id, "调度器", AgentStatus.THINKING, "剧本通过评审，进入导演阶段"
                )
                break
            elif verdict == "REJECT" and revision_count >= MAX_REVISION_ROUNDS:
                await self.bb.log_agent(
                    self.project_id, "调度器", AgentStatus.THINKING,
                    f"已达最大修订轮数 ({MAX_REVISION_ROUNDS})，强制进入导演阶段"
                )
                break
            else:
                revision_count += 1
                await self._update_step(STEP_REVISION, iteration_count=revision_count)
                await self.bb.log_agent(
                    self.project_id, "调度器", AgentStatus.THINKING,
                    f"剧本需要修订（第 {revision_count} 轮），重新召唤编剧..."
                )
                # 重新运行编剧（会读取评审报告作为上下文）
                revised_screenwriter = ScreenwriterAgent(self.bb, self.project_id, model_name=screenwriter_model)
                await revised_screenwriter.run()

    async def _run_direction(self):
        """步骤 4：导演分镜"""
        await self._update_step(STEP_DIRECTION)
        director_model = self._agent_models.get("director")
        director = DirectorAgent(self.bb, self.project_id, model_name=director_model)
        await director.run()

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
            self.project_id, "调度器", AgentStatus.THINKING,
            f"进入步骤：{display}"
        )

    async def _save_to_documents(self):
        """将生成的产出物保存为当前工作台草稿，以便直接进入编辑器查阅"""
        import json
        import hashlib
        from datetime import datetime
        from pathlib import Path

        doc_path = Path(__file__).parent.parent / "data" / "docs"
        doc_path.mkdir(parents=True, exist_ok=True)
        
        artifacts = await self.bb.read_all(self.project_id)
        now_str = datetime.now().isoformat()

        # 构建 creator 文档
        creator_sections = []
        creator_mapping = {
            "script": "script_source",
            "logline": "logline",
            "character_sheets": "character_sheets",
            "beat_sheet": "beat_sheet",
        }
        for bb_key, section_id in creator_mapping.items():
            content = artifacts.get(bb_key, {}).get("content", "")
            if content:
                creator_sections.append({"id": section_id, "content": content})
                
        if creator_sections:
            doc_id = hashlib.md5(f"creator_{now_str}".encode()).hexdigest()[:8]
            doc_data = {
                "id": doc_id,
                "project_id": self.project_id,
                "mode": "creator",
                "sections": creator_sections,
                "created_at": now_str,
            }
            with open(doc_path / f"{self.project_id}_creator.json", "w", encoding="utf-8") as f:
                json.dump(doc_data, f, ensure_ascii=False, indent=2)

        # 构建 reviewer 文档
        reviewer_sections = []
        reviewer_mapping = {
            "script": "script_source",
            "review_overview": "review_overview",
            "review_structure": "review_structure",
            "review_characters": "review_characters",
            "review_dialogue": "review_dialogue",
            "review_causal_chain": "review_causal_chain",
            "review_market": "review_market",
            "review_summary": "review_summary",
        }
        
        # The Reviewer agent currently puts all review content into REVIEW_REPORT (ArtifactType.REVIEW_REPORT),
        # but the editor expects split sections. The reviewer agent doesn't split its output into the DB?
        # Let's check how many artifacts reviewer outputs. Wait, we should output whatever is mapped.
        # But script_source at least must be there.
        for bb_key, section_id in reviewer_mapping.items():
            content = artifacts.get(bb_key, {}).get("content", "")
            if content:
                reviewer_sections.append({"id": section_id, "content": content})
                
        # Fallback for Review report if split keys aren't used by the agent:
        # Currently, reviewer_agent might just output single `review_report`. Let's still save what we can.
        if "review_report" in artifacts and not any(s["id"] == "review_overview" for s in reviewer_sections):
            # Just push it as overview if it's a monolithic report
            content = artifacts.get("review_report", {}).get("content", "")
            if content:
                reviewer_sections.append({"id": "review_overview", "content": content})

        if reviewer_sections:
            doc_id = hashlib.md5(f"reviewer_{now_str}".encode()).hexdigest()[:8]
            doc_data = {
                "id": doc_id,
                "project_id": self.project_id,
                "mode": "reviewer",
                "sections": reviewer_sections,
                "created_at": now_str,
            }
            with open(doc_path / f"{self.project_id}_reviewer.json", "w", encoding="utf-8") as f:
                json.dump(doc_data, f, ensure_ascii=False, indent=2)

    async def _build_summary(self) -> dict:
        """构建最终产出物摘要"""
        artifacts = await self.bb.read_all(self.project_id)
        summary = {}
        for key, val in artifacts.items():
            content = val.get("content", "")
            summary[key] = {
                "version": val.get("version", 1),
                "preview": content[:200] + "..." if len(content) > 200 else content,
                "length": len(content),
            }
        return summary
