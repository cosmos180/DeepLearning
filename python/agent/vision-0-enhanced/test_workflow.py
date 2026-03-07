import asyncio
from backend.core.blackboard import blackboard
from backend.core.orchestrator import Orchestrator

async def main():
    await blackboard.init()
    orch = Orchestrator(blackboard)
    try:
        await orch.run(
            seed="测试LLM连接错误",
            target_duration="1分钟短片",
            style="测试风格"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
