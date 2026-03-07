import asyncio
from backend.core.blackboard import blackboard, WorkflowStatus
from backend.core.base_agent import AgentStatus

async def main():
    project_id = 'test-fail-123'
    # 模拟失败的项目
    await blackboard.set_workflow_state(
        project_id, WorkflowStatus.FAILED,
        current_step='编剧',
        seed='这是一个注定失败的测试项目',
        target_duration='5分钟',
        style='悬疑'
    )
    # 写入一条失败日志
    await blackboard.log_agent(
        "调度器", AgentStatus.FAILED,
        "工作流执行失败: 无法连接到 LLM 模型 (Timeout)",
        detail="Traceback..."
    )
    # Update project_id to point to the created workflow state
    await blackboard._db.execute(
        "UPDATE agent_logs SET project_id = ? WHERE project_id IS NULL OR project_id = 'default'", (project_id,)
    )
    await blackboard._db.commit()
    print("Failed project created.")

asyncio.run(main())
