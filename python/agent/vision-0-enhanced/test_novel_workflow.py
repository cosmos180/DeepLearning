#!/usr/bin/env python3
"""
test_novel_workflow.py — 小说创作工作流测试脚本

测试小说创作的各个步骤：
1. 选题生成
2. 大纲生成
3. 骨架诊断
4. 章节生成
5. 评审
6. 开头优化
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.core.blackboard import blackboard, ArtifactType
from backend.core.novel_orchestrator import NovelOrchestrator


async def test_topic_agent():
    """测试选题 Agent"""
    print("\n=== 测试选题 Agent ===")
    from backend.agents.novel.topic_agent import TopicAgent

    agent = TopicAgent(
        blackboard,
        "test_novel_001",
        genre="古言",
        audience="女频",
        tone="爽文",
        female_lead_identity="西域舞姬(实为谍报头子)"
    )

    result = await agent.run()
    print(f"选题生成完成，结果长度: {len(result)} 字符")

    # 检查结果
    topic_ideas = await blackboard.read("test_novel_001", ArtifactType.TOPIC_IDEAS)
    print(f"黑板中的选题创意长度: {len(topic_ideas) if topic_ideas else 0} 字符")

    return result


async def test_outline_agent():
    """测试大纲生成 Agent"""
    print("\n=== 测试大纲生成 Agent ===")
    from backend.agents.novel.outline_agent import OutlineAgent

    agent = OutlineAgent(
        blackboard,
        "test_novel_001"
    )

    result = await agent.run()
    print(f"大纲生成完成，结果长度: {len(result)} 字符")

    # 检查结果
    outline = await blackboard.read("test_novel_001", ArtifactType.NOVEL_OUTLINE)
    print(f"黑板中的大纲长度: {len(outline) if outline else 0} 字符")

    return result


async def test_diagnostics_agent():
    """测试骨架诊断 Agent"""
    print("\n=== 测试骨架诊断 Agent ===")
    from backend.agents.novel.skeleton_diagnostics_agent import SkeletonDiagnosticsAgent

    agent = SkeletonDiagnosticsAgent(
        blackboard,
        "test_novel_001"
    )

    result = await agent.run()
    print(f"骨架诊断完成，结果长度: {len(result)} 字符")

    # 检查结果
    candidates = await blackboard.read("test_novel_001", ArtifactType.SKELETON_CANDIDATES)
    print(f"黑板中的候选骨架长度: {len(candidates) if candidates else 0} 字符")

    return result


async def test_novel_generator_agent():
    """测试小说生成 Agent"""
    print("\n=== 测试小说生成 Agent ===")
    from backend.agents.novel.novel_generator_agent import NovelGeneratorAgent

    # 先模拟选择一个骨架
    await blackboard.publish(
        "test_novel_001",
        ArtifactType.SELECTED_SKELETON,
        "## 候选骨架一：强化冲突版\n\n这是一个关于西域谍战与商战的故事..."
    )

    agent = NovelGeneratorAgent(
        blackboard,
        "test_novel_001",
        chapter_number=1
    )

    result = await agent.run()
    print(f"第一章生成完成，结果长度: {len(result)} 字符")

    return result


async def test_reviewer_agent():
    """测试评审 Agent"""
    print("\n=== 测试评审 Agent ===")
    from backend.agents.novel.novel_reviewer_agent import NovelReviewerAgent

    agent = NovelReviewerAgent(
        blackboard,
        "test_novel_001"
    )

    result = await agent.run()
    print(f"评审完成，结果长度: {len(result)} 字符")

    # 检查结果
    review = await blackboard.read("test_novel_001", ArtifactType.REVIEW_COMMENTS)
    print(f"黑板中的评审意见长度: {len(review) if review else 0} 字符")

    return result


async def test_opening_optimizer_agent():
    """测试开头优化 Agent"""
    print("\n=== 测试开头优化 Agent ===")
    from backend.agents.novel.opening_optimizer_agent import OpeningOptimizerAgent

    agent = OpeningOptimizerAgent(
        blackboard,
        "test_novel_001"
    )

    result = await agent.run()
    print(f"开头优化完成，结果长度: {len(result)} 字符")

    # 检查结果
    opening = await blackboard.read("test_novel_001", ArtifactType.OPENING_SUGGESTION)
    print(f"黑板中的开头建议长度: {len(opening) if opening else 0} 字符")

    return result


async def test_full_workflow():
    """测试完整工作流"""
    print("\n" + "="*50)
    print("测试完整小说创作工作流")
    print("="*50)

    await blackboard.init()

    try:
        # 步骤1：选题
        await test_topic_agent()

        # 步骤2：大纲
        await test_outline_agent()

        # 步骤3：骨架诊断
        await test_diagnostics_agent()

        # 步骤5：生成第一章（跳过步骤4的用户选择）
        await test_novel_generator_agent()

        # 步骤6：评审
        await test_reviewer_agent()

        # 步骤7：开头优化
        await test_opening_optimizer_agent()

        print("\n" + "="*50)
        print("所有测试完成！")
        print("="*50)

    finally:
        await blackboard.close()


if __name__ == "__main__":
    print("小说创作工作流测试")
    print("="*50)

    # 检查环境变量
    if not os.getenv("OPENROUTER_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("警告: 未检测到 API Key，请设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY 环境变量")
        print("测试将可能失败...")
        print()

    asyncio.run(test_full_workflow())
