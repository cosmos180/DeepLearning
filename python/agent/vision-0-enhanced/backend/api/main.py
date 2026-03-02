"""
main.py — FastAPI 后端入口
提供 REST API 和 SSE 实时事件推送
"""

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.core.blackboard import blackboard, WorkflowStatus
from backend.core.orchestrator import Orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    await blackboard.init()
    yield
    await blackboard.close()


app = FastAPI(title="Vision-0 Enhanced API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局任务追踪
_running_task: Optional[asyncio.Task] = None


class ProjectRequest(BaseModel):
    seed: str
    target_duration: str = "30分钟短片"
    style: str = "科幻+温情"
    agent_models: dict[str, str] = {}


# ─── 工作流控制 ───────────────────────────────────────────────────────────────

@app.post("/api/project/start")
async def start_project(req: ProjectRequest):
    """启动新的影视项目工作流"""
    global _running_task

    # 检查是否已有任务在运行
    state = await blackboard.get_workflow_state("default")
    if state and state.get("status") == WorkflowStatus.RUNNING.value:
        raise HTTPException(status_code=409, detail="已有项目正在运行，请等待完成或重置")

    async def run_workflow():
        orch = Orchestrator(blackboard)
        try:
            await orch.run(req.seed, req.target_duration, req.style, req.agent_models)
        except Exception as e:
            print(f"工作流异常: {e}")

    _running_task = asyncio.create_task(run_workflow())
    return {"status": "started", "message": f"项目已启动，创意种子：{req.seed}"}


@app.post("/api/project/reset")
async def reset_project():
    """重置项目，清空所有数据"""
    global _running_task
    if _running_task and not _running_task.done():
        _running_task.cancel()
    await blackboard.clear_all()
    return {"status": "reset", "message": "项目已重置"}


# ─── 状态查询 ─────────────────────────────────────────────────────────────────

@app.get("/api/state")
async def get_state():
    """获取当前工作流状态"""
    state = await blackboard.get_workflow_state("default")
    logs = await blackboard.get_agent_logs(limit=30)
    artifacts = await blackboard.read_all()

    # 构建产出物摘要（不返回完整内容）
    artifact_summary = {}
    for k, v in artifacts.items():
        content = v.get("content", "")
        artifact_summary[k] = {
            "version": v.get("version", 1),
            "length": len(content),
            "preview": content[:150] + "..." if len(content) > 150 else content,
            "updated_at": v.get("updated_at", ""),
        }

    return {
        "workflow": state,
        "logs": logs,
        "artifacts": artifact_summary,
    }


@app.get("/api/artifact/{artifact_type}")
async def get_artifact(artifact_type: str):
    """获取指定类型的完整产出物"""
    from backend.core.blackboard import ArtifactType
    try:
        at = ArtifactType(artifact_type)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"未知产出物类型: {artifact_type}")

    content = await blackboard.read(at)
    if content is None:
        raise HTTPException(status_code=404, detail=f"产出物 {artifact_type} 尚未生成")
    return {"type": artifact_type, "content": content}


@app.get("/api/traces")
async def get_traces():
    """获取追踪事件（可观测性）"""
    traces = await blackboard.get_traces(project_id="default", limit=100)
    return {"traces": traces}


# ─── SSE 实时事件流 ───────────────────────────────────────────────────────────

@app.get("/api/events")
async def event_stream():
    """SSE 实时事件流，前端订阅此接口获取实时更新"""
    queue = blackboard.subscribe_sse()

    async def generator():
        try:
            # 立即发送当前状态
            state = await blackboard.get_workflow_state("default")
            logs = await blackboard.get_agent_logs(limit=10)
            artifacts = await blackboard.read_all()
            artifact_summary = {
                k: {"version": v.get("version", 1), "length": len(v.get("content", ""))}
                for k, v in artifacts.items()
            }
            yield {
                "event": "init",
                "data": json.dumps({
                    "workflow": state,
                    "logs": logs,
                    "artifacts": artifact_summary
                }, ensure_ascii=False)
            }

            while True:
                try:
                    # 等待更新通知（超时后发送心跳）
                    await asyncio.wait_for(queue.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    yield {"event": "heartbeat", "data": "ping"}
                    continue

                # 发送最新状态
                state = await blackboard.get_workflow_state("default")
                logs = await blackboard.get_agent_logs(limit=20)
                artifacts = await blackboard.read_all()
                artifact_summary = {
                    k: {
                        "version": v.get("version", 1),
                        "length": len(v.get("content", "")),
                        "preview": v.get("content", "")[:100],
                    }
                    for k, v in artifacts.items()
                }

                yield {
                    "event": "update",
                    "data": json.dumps({
                        "workflow": state,
                        "logs": logs[-5:],  # 只发最新5条
                        "artifacts": artifact_summary,
                    }, ensure_ascii=False)
                }

        except asyncio.CancelledError:
            pass
        finally:
            blackboard.unsubscribe_sse(queue)

    return EventSourceResponse(generator())


# ─── 健康检查 ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Vision-0 Enhanced"}
