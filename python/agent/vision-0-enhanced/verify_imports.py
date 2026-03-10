#!/usr/bin/env python3
"""
verify_imports.py — 验证小说创作工具的导入
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_imports():
    """测试所有小说创作相关的导入"""
    print("验证小说创作工具导入...")
    print("="*50)

    try:
        # 测试核心模块
        print("1. 测试核心模块...")
        from backend.core.blackboard import blackboard, ArtifactType, WorkflowStatus, AgentStatus
        from backend.core.base_agent import BaseAgent
        from backend.core.llm_client import call_llm, call_llm_stream
        from backend.core.novel_orchestrator import NovelOrchestrator, NovelStep
        print("   ✓ 核心模块导入成功")

        # 测试小说 Agents
        print("2. 测试小说 Agents...")
        from backend.agents.novel.topic_agent import TopicAgent
        from backend.agents.novel.outline_agent import OutlineAgent
        from backend.agents.novel.skeleton_diagnostics_agent import SkeletonDiagnosticsAgent
        from backend.agents.novel.novel_generator_agent import NovelGeneratorAgent
        from backend.agents.novel.novel_reviewer_agent import NovelReviewerAgent
        from backend.agents.novel.opening_optimizer_agent import OpeningOptimizerAgent
        print("   ✓ 所有小说 Agents 导入成功")

        # 测试 ArtifactType 扩展
        print("3. 测试 ArtifactType 扩展...")
        assert hasattr(ArtifactType, 'TOPIC_IDEAS'), "缺少 TOPIC_IDEAS"
        assert hasattr(ArtifactType, 'NOVEL_OUTLINE'), "缺少 NOVEL_OUTLINE"
        assert hasattr(ArtifactType, 'SKELETON_CANDIDATES'), "缺少 SKELETON_CANDIDATES"
        assert hasattr(ArtifactType, 'CHAPTER_CONTENT'), "缺少 CHAPTER_CONTENT"
        assert hasattr(ArtifactType, 'REVIEW_COMMENTS'), "缺少 REVIEW_COMMENTS"
        assert hasattr(ArtifactType, 'OPENING_SUGGESTION'), "缺少 OPENING_SUGGESTION"
        print("   ✓ ArtifactType 扩展正确")

        # 测试 NovelStep 枚举
        print("4. 测试 NovelStep 枚举...")
        assert hasattr(NovelStep, 'STEP_1_TOPIC'), "缺少 STEP_1_TOPIC"
        assert hasattr(NovelStep, 'STEP_2_OUTLINE'), "缺少 STEP_2_OUTLINE"
        assert hasattr(NovelStep, 'STEP_3_SELECT'), "缺少 STEP_3_SELECT"
        assert hasattr(NovelStep, 'STEP_5_GENERATE'), "缺少 STEP_5_GENERATE"
        assert hasattr(NovelStep, 'STEP_6_REVIEW'), "缺少 STEP_6_REVIEW"
        assert hasattr(NovelStep, 'STEP_7_OPENING'), "缺少 STEP_7_OPENING"
        print("   ✓ NovelStep 枚举正确")

        print("\n" + "="*50)
        print("所有导入验证通过！✓")
        print("="*50)
        return True

    except Exception as e:
        print(f"\n✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
