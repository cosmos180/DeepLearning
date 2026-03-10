"""
novel_orchestrator.py — 小说创作工作流编排器
实现9步小说创作流程的自动化编排
"""

import asyncio
from typing import Optional, Callable
from enum import Enum

from .blackboard import Blackboard, ArtifactType, WorkflowStatus, AgentStatus


class NovelStep(str, Enum):
    """小说创作流程步骤"""
    IDLE = "idle"
    STEP_1_TOPIC = "step_1_topic"           # 1. 选题
    STEP_2_OUTLINE = "step_2_outline"       # 2. 初步大纲
    STEP_2_5_TITLE = "step_2_5_title"       # 2.5. 书名生成
    STEP_3_SELECT = "step_3_select"         # 3. 选择候选骨架
    STEP_4_VALIDATE = "step_4_validate"     # 4. 验证骨架
    STEP_5_GENERATE = "step_5_generate"     # 5. 生成正文
    STEP_6_REVIEW = "step_6_review"         # 6. 评审
    STEP_7_OPENING = "step_7_opening"       # 7. 开头建议
    STEP_8_REFINE = "step_8_refine"         # 8. 精修
    COMPLETED = "completed"


class NovelOrchestrator:
    """
    小说创作工作流编排器

    实现9步创作流程：
    1. 选题 → 2. 初步大纲 → 3. 选择候选骨架 → 4. 验证骨架
    → 5. 生成正文 → 6. 评审 → 7. 开头建议 → 8. 精修 → 9. 完成
    """

    def __init__(self, blackboard: Blackboard):
        self.bb = blackboard
        self.project_id = "default"

    async def start_novel_project(
        self,
        project_id: str,
        genre: str = "古言",
        audience: str = "女频",
        tone: str = "爽文",
        female_lead_identity: str = "流亡公主",
        model_name: Optional[str] = None
    ) -> str:
        """
        启动新的小说创作项目
        返回项目ID
        """
        self.project_id = project_id

        # 初始化工作流状态
        await self.bb.set_workflow_state(
            project_id,
            WorkflowStatus.RUNNING,
            current_step=NovelStep.STEP_1_TOPIC,
            seed=f"{genre}_{audience}_{tone}",
            target_duration="20章节",
            style=female_lead_identity
        )

        return project_id

    async def run_step_1_topic(self, model_name: Optional[str] = None):
        """步骤1：选题"""
        from ..agents.novel.topic_agent import TopicAgent

        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.RUNNING,
            current_step=NovelStep.STEP_1_TOPIC
        )

        # 这里需要获取项目配置（genre, audience等）
        # 简化处理，使用默认值
        state = await self.bb.get_workflow_state(self.project_id)
        style = state.get("style", "流亡公主") if state else "流亡公主"
        seed = state.get("seed", "古言_女频_爽文") if state else "古言_女频_爽文"

        parts = seed.split("_")
        genre = parts[0] if len(parts) > 0 else "古言"
        audience = parts[1] if len(parts) > 1 else "女频"
        tone = parts[2] if len(parts) > 2 else "爽文"

        agent = TopicAgent(
            self.bb,
            self.project_id,
            genre=genre,
            audience=audience,
            tone=tone,
            female_lead_identity=style,
            model_name=model_name
        )

        await agent.run()

    async def run_step_2_outline(self, model_name: Optional[str] = None):
        """步骤2：初步大纲"""
        from ..agents.novel.outline_agent import OutlineAgent

        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.RUNNING,
            current_step=NovelStep.STEP_2_OUTLINE
        )

        agent = OutlineAgent(
            self.bb,
            self.project_id,
            model_name=model_name
        )

        await agent.run()

    async def run_step_2_5_title(self, model_name: Optional[str] = None):
        """步骤2.5：书名生成"""
        from ..agents.novel.title_generator_agent import TitleGeneratorAgent

        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.RUNNING,
            current_step=NovelStep.STEP_2_5_TITLE
        )

        agent = TitleGeneratorAgent(
            self.bb,
            self.project_id,
            model_name=model_name
        )

        await agent.run()

        # 书名生成完成后进入等待状态
        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.WAITING_HUMAN,
            current_step=NovelStep.STEP_2_5_TITLE
        )

    async def select_title(self, selected_title: str):
        """用户选择书名后，保存选择"""
        await self.bb.publish(
            self.project_id,
            ArtifactType.SELECTED_TITLE,
            selected_title
        )

        # 继续下一步（骨架诊断）
        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.RUNNING,
            current_step=NovelStep.STEP_3_SELECT
        )

    async def run_step_3_diagnostics(self, model_name: Optional[str] = None):
        """步骤3：骨架诊断（生成候选骨架）"""
        from ..agents.novel.skeleton_diagnostics_agent import SkeletonDiagnosticsAgent

        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.RUNNING,
            current_step=NovelStep.STEP_3_SELECT
        )

        agent = SkeletonDiagnosticsAgent(
            self.bb,
            self.project_id,
            model_name=model_name
        )

        await agent.run()

        # 诊断完成后进入等待状态，让用户选择
        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.WAITING_HUMAN,
            current_step=NovelStep.STEP_3_SELECT
        )

    async def select_skeleton(self, selected_skeleton: str):
        """用户选择骨架后，保存选择"""
        await self.bb.publish(
            self.project_id,
            ArtifactType.SELECTED_SKELETON,
            selected_skeleton
        )

        # 继续下一步
        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.RUNNING,
            current_step=NovelStep.STEP_4_VALIDATE
        )

    async def run_step_5_generate_chapter(
        self,
        chapter_number: Optional[int] = None,
        model_name: Optional[str] = None
    ):
        """步骤5：生成正文"""
        from ..agents.novel.novel_generator_agent import NovelGeneratorAgent

        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.RUNNING,
            current_step=NovelStep.STEP_5_GENERATE
        )

        agent = NovelGeneratorAgent(
            self.bb,
            self.project_id,
            chapter_number=chapter_number,
            generate_all=False,
            model_name=model_name
        )

        await agent.run()

    async def run_step_6_review(self, model_name: Optional[str] = None):
        """步骤6：评审"""
        from ..agents.novel.novel_reviewer_agent import NovelReviewerAgent

        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.RUNNING,
            current_step=NovelStep.STEP_6_REVIEW
        )

        agent = NovelReviewerAgent(
            self.bb,
            self.project_id,
            model_name=model_name
        )

        await agent.run()

    async def run_step_7_opening(self, model_name: Optional[str] = None):
        """步骤7：开头优化"""
        from ..agents.novel.opening_optimizer_agent import OpeningOptimizerAgent

        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.RUNNING,
            current_step=NovelStep.STEP_7_OPENING
        )

        agent = OpeningOptimizerAgent(
            self.bb,
            self.project_id,
            model_name=model_name
        )

        await agent.run()

    async def complete_workflow(self):
        """步骤8-9：完成工作流"""
        await self.bb.set_workflow_state(
            self.project_id,
            WorkflowStatus.COMPLETED,
            current_step=NovelStep.COMPLETED
        )

    async def run_full_workflow(
        self,
        project_id: str,
        genre: str = "古言",
        audience: str = "女频",
        tone: str = "爽文",
        female_lead_identity: str = "流亡公主",
        model_name: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ):
        """
        运行完整工作流（步骤1-7）

        注意：步骤3（骨架选择）需要人工介入，会暂停等待用户选择
        """
        await self.start_novel_project(
            project_id,
            genre=genre,
            audience=audience,
            tone=tone,
            female_lead_identity=female_lead_identity,
            model_name=model_name
        )

        # 步骤1：选题
        if progress_callback:
            await progress_callback("正在生成选题...")
        await self.run_step_1_topic(model_name)

        # 步骤2：大纲
        if progress_callback:
            await progress_callback("正在生成大纲...")
        await self.run_step_2_outline(model_name)

        # 步骤3：骨架诊断
        if progress_callback:
            await progress_callback("正在诊断骨架...")
        await self.run_step_3_diagnostics(model_name)

        # 步骤3需要用户选择，工作流在此暂停
        # 用户调用 select_skeleton() 后可继续


# 全局单例
novel_orchestrator = NovelOrchestrator(blackboard=None)  # 会在使用时注入
