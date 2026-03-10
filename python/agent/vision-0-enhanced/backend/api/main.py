"""
main.py — FastAPI 后端入口
提供 REST API 和 SSE 实时事件推送
"""

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime
from hashlib import md5
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

import sys
import os

# 加载 .env 文件
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.core.blackboard import blackboard, WorkflowStatus, AgentStatus
from backend.core.orchestrator import Orchestrator
from backend.core.novel_orchestrator import NovelOrchestrator, NovelStep
from backend.core.llm_client import call_llm, FAST_MODEL, DEFAULT_MODEL, get_cherry_models


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

# 静态文件目录
FRONTEND_PATH = Path(__file__).parent.parent.parent / "frontend"

import uuid

# 全局任务追踪
_running_tasks: dict[str, asyncio.Task] = {}


class ProjectRequest(BaseModel):
    project_id: Optional[str] = None
    seed: str = ""
    target_duration: str = "30分钟短片"
    style: str = "科幻+温情"
    popular_elements: list[str] = []        # 用户选择的流行创作元素
    agent_models: dict[str, str] = {}
    start_from_step: Optional[str] = None  # 从哪个步骤开始
    artifacts: dict[str, str] = {}          # 预置产出物（用于跳过前置步骤）


# ─── 工作流控制 ───────────────────────────────────────────────────────────────

@app.post("/api/project/start")
async def start_project(req: ProjectRequest):
    """启动新的影视项目工作流"""
    global _running_tasks

    project_id = req.project_id or str(uuid.uuid4())

    # 检查当前项目是否在运行
    state = await blackboard.get_workflow_state(project_id)
    if state and state.get("status") == WorkflowStatus.RUNNING.value and project_id in _running_tasks and not _running_tasks[project_id].done():
        raise HTTPException(status_code=409, detail=f"项目 {project_id} 正在运行，请等待完成或重置")

    # 验证：如果是从头开始，必须有 seed
    if req.start_from_step is None and not req.seed:
        raise HTTPException(status_code=400, detail="从创作步骤开始时，必须提供创意种子")

    async def run_workflow():
        orch = Orchestrator(blackboard)
        orch.project_id = project_id
        try:
            await orch.run(
                seed=req.seed,
                target_duration=req.target_duration,
                style=req.style,
                popular_elements=req.popular_elements,
                agent_models=req.agent_models,
                start_from_step=req.start_from_step,
                artifacts=req.artifacts
            )
        except Exception as e:
            print(f"工作流异常 [{project_id}]: {e}")

    _running_tasks[project_id] = asyncio.create_task(run_workflow())

    step_info = f"，从步骤 [{req.start_from_step}] 开始" if req.start_from_step else ""
    return {"status": "started", "project_id": project_id, "message": f"项目 {project_id} 已启动{step_info}"}


@app.post("/api/project/{project_id}/reset")
async def reset_project(project_id: str):
    """重置项目，清空所有数据"""
    global _running_tasks
    task = _running_tasks.get(project_id)
    if task and not task.done():
        task.cancel()
    await blackboard.delete_project(project_id)
    return {"status": "reset", "message": f"项目 {project_id} 已重置"}


@app.post("/api/project/{project_id}/reset-status")
async def reset_project_status(project_id: str):
    """重置项目状态（解除卡住的running状态）"""
    global _running_tasks

    # 取消正在运行的任务
    task = _running_tasks.get(project_id)
    if task and not task.done():
        task.cancel()
        _running_tasks.pop(project_id, None)

    # 获取当前状态
    current_state = await blackboard.get_workflow_state(project_id)
    current_step = current_state.get("current_step") if current_state else None

    # 将状态从running改为idle，但保持当前步骤
    await blackboard.set_workflow_state(
        project_id,
        WorkflowStatus.IDLE,
        current_step=current_step  # 保持当前步骤不变
    )

    return {"status": "ok", "message": "项目状态已重置"}


# ─── 模型查询 ─────────────────────────────────────────────────────────────────

@app.get("/api/cherry/models")
async def get_cherry_models_api():
    """获取 Cherry Studio 可用模型列表"""
    models = await get_cherry_models()
    return {"models": models}


# ─── 状态查询 ─────────────────────────────────────────────────────────────────

@app.get("/api/projects")
async def get_projects():
    """获取所有项目列表"""
    try:
        from backend.core.blackboard import blackboard
        projects = await blackboard.get_all_projects()
        return {"projects": projects}
    except Exception as e:
        return {"projects": [], "error": str(e)}

@app.delete("/api/project/{project_id}")
async def delete_project(project_id: str):
    """删除指定项目的所有数据"""
    try:
        from backend.core.blackboard import blackboard
        await blackboard.delete_project(project_id)
        return {"status": "success", "message": f"Project {project_id} deleted."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/project/{project_id}/state")
async def get_state(project_id: str):
    """获取指定工作流状态"""
    state = await blackboard.get_workflow_state(project_id)
    logs = await blackboard.get_agent_logs(project_id, limit=30)
    artifacts = await blackboard.read_all(project_id)

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


@app.get("/api/project/{project_id}/artifact/{artifact_type}")
async def get_artifact(project_id: str, artifact_type: str):
    """获取指定类型的完整产出物"""
    from backend.core.blackboard import ArtifactType
    try:
        at = ArtifactType(artifact_type)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"未知产出物类型: {artifact_type}")

    content = await blackboard.read(project_id, at)
    if content is None:
        raise HTTPException(status_code=404, detail=f"产出物 {artifact_type} 尚未生成")
    return {"type": artifact_type, "content": content}


class ArtifactUploadRequest(BaseModel):
    project_id: str
    artifacts: dict[str, str]


@app.post("/api/artifact/upload")
async def upload_artifacts(req: ArtifactUploadRequest):
    """
    手动上传产出物（用于跳过前置步骤）。
    接收产出物字典，批量写入黑板。
    """
    if not req.artifacts:
        raise HTTPException(status_code=400, detail="没有提供产出物")

    await blackboard.publish_many(req.project_id, req.artifacts)
    return {
        "status": "ok",
        "message": f"已上传 {len(req.artifacts)} 个产出物",
        "types": list(req.artifacts.keys())
    }


@app.get("/api/project/{project_id}/traces")
async def get_traces(project_id: str):
    """获取追踪事件（可观测性）"""
    traces = await blackboard.get_traces(project_id=project_id, limit=100)
    return {"traces": traces}


# ─── SSE 实时事件流 ───────────────────────────────────────────────────────────

@app.get("/api/events")
async def event_stream(project_id: Optional[str] = None):
    """SSE 实时事件流，前端订阅此接口获取实时更新
    如果不提供 project_id，可能返回所有项目通知（按需扩展）。目前为了兼容，允许传空或传特定id。
    """
    queue = blackboard.subscribe_sse()

    async def generator():
        try:
            target_pid = project_id or "default"
            # 立即发送当前状态
            state = await blackboard.get_workflow_state(target_pid)
            logs = await blackboard.get_agent_logs(target_pid, limit=10)
            artifacts = await blackboard.read_all(target_pid)
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
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    yield {"event": "heartbeat", "data": "ping"}
                    continue

                if isinstance(msg, dict) and msg.get("type") == "stream":
                    # Filter by project_id
                    if msg.get("project_id") == target_pid or target_pid == "default":
                        yield {
                            "event": "stream",
                            "data": json.dumps({
                                "agent": msg.get("agent"),
                                "chunk": msg.get("chunk")
                            }, ensure_ascii=False)
                        }
                    continue

                # 发送最新状态 (state_update)
                state = await blackboard.get_workflow_state(target_pid)
                logs = await blackboard.get_agent_logs(target_pid, limit=20)
                artifacts = await blackboard.read_all(target_pid)
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


# ─── 前端页面路由 ───────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """返回首页"""
    index_file = FRONTEND_PATH / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"error": "index.html not found"}


@app.get("/editor.html")
async def editor_page():
    """返回编辑器页面"""
    editor_file = FRONTEND_PATH / "editor.html"
    if editor_file.exists():
        return FileResponse(editor_file)
    return {"error": "editor.html not found"}


@app.get("/index.html")
async def index_page():
    """返回首页（兼容 index.html 路径）"""
    index_file = FRONTEND_PATH / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"error": "index.html not found"}


@app.get("/novel.html")
async def novel_page():
    """返回小说创作页面"""
    novel_file = FRONTEND_PATH / "novel.html"
    if novel_file.exists():
        return FileResponse(novel_file)
    return {"error": "novel.html not found"}


# 挂载静态资源
app.mount("/static", StaticFiles(directory=str(FRONTEND_PATH)), name="static")


# ─── 编辑器 AI 接口 ───────────────────────────────────────────────────────────

import hashlib
from datetime import datetime
from pathlib import Path

# 文档存储路径
DOC_PATH = Path(__file__).parent.parent / "data" / "documents"
DOC_PATH.mkdir(parents=True, exist_ok=True)


class AiOptimizeRequest(BaseModel):
    text: str
    context: str = "影视创作"
    style: str = "专业"


class AiChatRequest(BaseModel):
    message: str
    mode: str = "creator"
    model: Optional[str] = None
    api_source: Optional[str] = "openrouter"  # openrouter 或 cherry
    current_section: Optional[str] = None
    context: dict = {}


class AiSuggestRequest(BaseModel):
    content: str
    section_type: str
    mode: str = "creator"


class AiStyleRequest(BaseModel):
    content: str
    style: str  # concise, vivid, formal, casual


class DocumentSaveRequest(BaseModel):
    project_id: str
    mode: str
    sections: list


@app.post("/api/ai/optimize")
async def ai_optimize(req: AiOptimizeRequest):
    """AI 优化文本"""
    system_prompt = f"""你是一位专业的{req.context}文案优化专家。
请优化用户提供的文本，要求：
1. 保留原文核心含义，提升表达质量
2. 风格要求：{req.style}
3. 去除冗余表达，增强画面感和情感张力
4. 直接输出优化后的文本，不要添加任何解释或前缀"""
    try:
        optimized, _ = await call_llm(
            system_prompt=system_prompt,
            user_prompt=f"请优化以下文本：\n\n{req.text}",
            model=FAST_MODEL,
            temperature=0.7,
            max_tokens=2000,
        )
        return {"optimized": optimized.strip()}
    except Exception as e:
        return {"optimized": f"优化失败：{str(e)}"}


@app.post("/api/ai/chat")
async def ai_chat(req: AiChatRequest):
    """AI 对话"""
    mode_desc = "原著创作" if req.mode == "creator" else "剧本评审"
    context_text = ""
    if req.context:
        # 当前活跃章节传入完整内容，其他章节传入摘要
        other_parts = []
        current_part = ""
        for k, v in req.context.items():
            if req.current_section and k == req.current_section:
                current_part = f"\n\n### 当前章节【{k}】完整内容：\n{v}"
            else:
                summary = v[:500] + "..." if len(v) > 500 else v
                other_parts.append(f"- {k}: {summary}")

        if other_parts:
            context_text = "\n\n其他章节摘要：\n" + "\n".join(other_parts)
        if current_part:
            context_text += current_part
    section_hint = f"\n用户当前正在编辑的章节：{req.current_section}" if req.current_section else ""

    system_prompt = f"""你是 AI 影视制片厂的{mode_desc}助手。
你正在协助用户进行影视剧本的{mode_desc}工作。{section_hint}
你可以看到用户提供的所有章节内容。请用专业但友好的语气回答用户的问题或执行用户的指令。
回复要简洁实用，避免空洞的套话。{context_text}"""
    try:
        # 使用传入的模型，如果没有则使用默认模型
        model = req.model if req.model else FAST_MODEL
        api_source = req.api_source if req.api_source else "openrouter"
        response, _ = await call_llm(
            system_prompt=system_prompt,
            user_prompt=req.message,
            model=model,
            temperature=0.7,
            max_tokens=4000,
            api_source=api_source,
        )
        return {"response": response.strip()}
    except Exception as e:
        return {"response": f"抱歉，请求失败：{str(e)}"}


@app.post("/api/ai/suggest")
async def ai_suggest(req: AiSuggestRequest):
    """AI 建议"""
    mode_desc = "原著创作" if req.mode == "creator" else "剧本评审"
    system_prompt = f"""你是资深的影视{mode_desc}顾问。
请分析用户提供的「{req.section_type}」内容，给出 3-5 条具体的改进建议。
要求：
1. 每条建议要具体、可操作，不要泛泛而谈
2. 指出具体的问题位置或段落
3. 给出修改方向或示例
4. 用编号列表格式输出"""
    try:
        suggestion, _ = await call_llm(
            system_prompt=system_prompt,
            user_prompt=f"请分析以下内容并给出改进建议：\n\n{req.content}",
            model=FAST_MODEL,
            temperature=0.4,
            max_tokens=2000,
        )
        return {"suggestion": suggestion.strip()}
    except Exception as e:
        return {"suggestion": f"分析失败：{str(e)}"}


@app.post("/api/ai/adjust-style")
async def ai_adjust_style(req: AiStyleRequest):
    """AI 风格调整"""
    style_instructions = {
        "concise": "请将文本改写为更简洁的版本。删除冗余修饰，精简句式，保留核心信息。每句话力求精炼有力。",
        "vivid": "请将文本改写为更生动的版本。增加感官描写、比喻和画面感，让读者仿佛身临其境。",
        "formal": "请将文本改写为更正式的版本。使用规范的书面语，语句严谨，适合专业场合。",
        "casual": "请将文本改写为更口语化的版本。语气轻松自然，像在跟朋友聊天。",
    }
    instruction = style_instructions.get(req.style, "请按要求调整文本风格。")
    system_prompt = f"""你是专业的文本风格调整专家。
{instruction}
要求：
1. 保留原文的核心含义和信息
2. 直接输出调整后的完整文本
3. 不要添加任何解释、标注或前缀"""
    try:
        adjusted, _ = await call_llm(
            system_prompt=system_prompt,
            user_prompt=f"请调整以下文本的风格：\n\n{req.content}",
            model=FAST_MODEL,
            temperature=0.7,
            max_tokens=4000,
        )
        return {"adjusted": adjusted.strip()}
    except Exception as e:
        return {"adjusted": f"风格调整失败：{str(e)}"}


@app.post("/api/document/save")
async def save_document(req: DocumentSaveRequest):
    """保存文档"""
    doc_id = hashlib.md5(f"{req.project_id}_{req.mode}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
    doc_data = {
        "id": doc_id,
        "project_id": req.project_id,
        "mode": req.mode,
        "sections": req.sections,
        "created_at": datetime.now().isoformat(),
    }

    # 保存当前文档
    doc_file = DOC_PATH / f"{req.project_id}_{req.mode}.json"
    with open(doc_file, "w", encoding="utf-8") as f:
        json.dump(doc_data, f, ensure_ascii=False, indent=2)

    # 保存版本快照
    version_file = DOC_PATH / f"v_{req.project_id}_{req.mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(doc_data, f, ensure_ascii=False, indent=2)

    return {"status": "ok", "id": doc_id}


@app.get("/api/document/load")
async def load_document(project_id: str, mode: str):
    """加载文档"""
    doc_file = DOC_PATH / f"{project_id}_{mode}.json"
    if doc_file.exists():
        with open(doc_file, "r", encoding="utf-8") as f:
            return json.load(f)
            
    # 兼容没有独立项目ID的旧版数据存档
    legacy_file = DOC_PATH / f"{mode}_current.json"
    if project_id == "default" and legacy_file.exists():
        with open(legacy_file, "r", encoding="utf-8") as f:
            return json.load(f)
            
    return {"project_id": project_id, "mode": mode, "sections": []}


@app.get("/api/document/versions")
async def get_document_versions(project_id: str, mode: str):
    """获取文档版本历史"""
    versions = []
    for f in sorted(DOC_PATH.glob(f"v_{project_id}_{mode}_*.json"), reverse=True)[:20]:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                versions.append({
                    "id": f.stem,
                    "title": f"版本 {f.stem.split('_v')[-1]}",
                    "created_at": data.get("created_at", ""),
                })
        except:
            pass
    return {"versions": versions}


@app.get("/api/document/version/{version_id}")
async def get_document_version(version_id: str):
    """加载特定版本的文档"""
    version_file = DOC_PATH / f"{version_id}.json"
    if not version_file.exists():
        raise HTTPException(status_code=404, detail=f"版本 {version_id} 不存在")
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取版本失败：{str(e)}")


@app.post("/api/ai/generate-section")
async def generate_section(req: dict):
    """生成章节内容"""
    section_type = req.get("section_type", "")
    mode = req.get("mode", "creator")
    context = req.get("context", {})

    # 构建上下文摘要
    context_text = ""
    if context:
        # 单独提取流行元素
        popular_elements = context.pop("popular_elements", None)
        if popular_elements and isinstance(popular_elements, list):
            context_text += "\n\n**用户选择的流行创作元素：** " + "、".join(popular_elements)
            context_text += "\n请在创作中自然融入以上元素，使其服务于故事本身，不要生硬堆砌。"
        if context:
            context_text += "\n\n以下是已有的内容供参考：\n" + "\n".join(
                f"### {k}\n{v[:500]}" for k, v in context.items()
            )

    # 各章节类型对应的生成提示
    section_prompts = {
        "logline": {
            "system": """你是专业的影视编剧。请根据上下文创作一段精彩的 Logline（一句话梗概）。
要求：包含主角、处境、目标、核心冲突和最大阻碍。控制在 2-4 句话。
直接输出 Logline 内容，不要加标题或前缀。""",
            "user": "请为这个影视项目创作 Logline。",
            "temperature": 0.85,
        },
        "character_sheets": {
            "system": """你是专业的影视编剧。请创作详细的角色设定档案。
要求：
1. 创建 3-5 个主要角色
2. 每个角色包含：姓名/代号、基本信息、外观描述、性格特征、背景故事、内心渴望、内心恐惧
3. 角色之间要有清晰的关系网络和冲突
4. 使用 Markdown 格式，每个角色用 ## 标题
直接输出角色设定内容。""",
            "user": "请创作完整的角色设定档案。",
            "temperature": 0.85,
        },
        "beat_sheet": {
            "system": """你是专业的影视编剧。请创作详细的故事节拍表（Beat Sheet）。
要求：
1. 按三幕结构组织（开端、发展、高潮/结局）
2. 每个节拍包含：节拍名称、时间点、具体事件（1-2句）、主角情绪状态
3. 至少 12-15 个关键节拍
4. 节奏紧凑，情感递进合理
5. 使用 Markdown 格式
直接输出节拍表内容。""",
            "user": "请创作完整的故事节拍表。",
            "temperature": 0.8,
        },
        "review_overview": {
            "system": """你是资深的剧本评审专家。请对提供的剧本材料进行综合评审。
重要：你需要从头到尾通读全文，特别注意前后场景之间的逻辑连贯性。
要求：
1. 给出综合评分（百分制）和等级
2. 从故事结构、角色塑造、对白质量、情感深度、创新性、逻辑连贯性六个维度分别评分
3. 列出 3 个核心优势和 3 个主要问题
4. 特别指出任何前后矛盾或逻辑断裂
5. 使用表格展示评分
6. 使用 Markdown 格式
直接输出评审内容。""",
            "user": "请对以下剧本材料进行综合评审。",
            "temperature": 0.4,
        },
        "review_structure": {
            "system": """你是资深的剧本结构分析专家。请分析剧本的叙事结构。
要求：
1. 按幕分析，每幕指出优势和问题
2. 给出具体的修改建议，包含原版和建议版的对比
3. 分析节奏是否合理
4. 使用 ✅ ⚠️ ❌ 标记各部分状态
5. 使用 Markdown 格式
直接输出结构分析内容。""",
            "user": "请分析以下剧本的叙事结构。",
            "temperature": 0.4,
        },
        "review_characters": {
            "system": """你是资深的角色分析专家。请分析剧本中的角色塑造。
要求：
1. 分析每个主要角色的立体度，给出评分
2. 评估角色弧线是否完整
3. 指出角色塑造的优势和问题
4. 给出具体的修改建议
5. 如有需要，建议新增角色
6. 使用 Markdown 格式
直接输出角色分析内容。""",
            "user": "请分析以下剧本中的角色塑造。",
            "temperature": 0.4,
        },
        "review_dialogue": {
            "system": """你是资深的对白写作专家。请分析剧本中的对白质量。
要求：
1. 给出对白的整体评价和评分
2. 找出有问题的对白（过于直白、缺乏潜台词、信息过载），给出原版和修改建议对比
3. 标出优秀的对白作为正面示例
4. 按修改优先级排序
5. 使用 Markdown 格式和代码块展示对白对比
直接输出对白分析内容。""",
            "user": "请分析以下剧本中的对白质量。",
            "temperature": 0.4,
        },
        "review_summary": {
            "system": """你是资深的剧本评审专家。请汇总所有分析，生成修改建议清单。
特别注意：如果有因果链分析结果，请将其中的断裂点也纳入修改建议。
要求：
1. 分三级：🔴 必须修改、🟡 建议修改、🟢 可选优化
2. 每条建议包含：序号、问题描述、涉及场景、修改建议、预计工时
3. 使用表格展示
4. 最后给出推荐的修改顺序和总耗时估算
5. 使用 Markdown 格式
直接输出修改建议清单。""",
            "user": "请汇总分析结果，生成修改建议清单。",
            "temperature": 0.4,
        },
        "review_causal_chain": {
            "system": """你是资深的剧本逻辑分析专家，擅长发现剧本中的因果链条和前后依赖关系。

请对剧本进行**逐场景渐进式分析**，像观众初次观看一样，从第一个场景开始逐场阅读，边读边追踪：

## 分析维度

### 1. 伏笔追踪表
逐场记录所有伏笔（道具、台词暗示、角色行为、环境线索）的状态：
- 🟡 **埋入** — 新出现的伏笔元素
- ⏳ **悬置** — 已埋入但尚未回收
- 🟢 **回收** — 伏笔得到呼应/解答
- 🔴 **遗忘** — 全文结束仍未回收的伏笔（契诃夫之枪违规）

用表格展示，格式：
| 伏笔元素 | 埋入场景 | 当前状态 | 回收场景 | 说明 |

### 2. 角色状态连续性
追踪每个主要角色跨场景的：
- 知识状态（是否知道某个秘密/信息）
- 情感状态（情绪是否连贯递进）
- 物理状态（受伤/持有物品等）

发现状态矛盾时，标记 ⚠️ 并指出具体场景和行。

### 3. 因果链完整性
绘制关键事件的因果链：
```
事件A (场景X) → 导致 → 事件B (场景Y) → 导致 → 事件C (场景Z)
```
检查是否存在：
- 无因之果：某个重要事件没有足够的前因铺垫
- 无果之因：某个重要设定埋下后没有产生后续影响
- 因果跳跃：事件之间缺少必要的过渡

### 4. 断裂点汇总
将所有发现的问题按严重程度排序：
- 🔴 **硬伤** — 逻辑矛盾，观众一定会注意到
- 🟡 **软伤** — 不够严谨，仔细看会发现
- 🟢 **建议** — 可以做得更好的伏笔/呼应机会

请使用 Markdown 格式输出，每个维度用 ## 标题分隔。
直接输出分析内容。""",
            "user": "请对以下剧本进行逐场景因果链分析。",
            "temperature": 0.3,
        },
        "review_market": {
            "system": """你是同时具备创意嗅觉和商业判断力的资深制片人。
请从**商业可行性**角度分析剧本，评估其市场潜力。

## 分析维度（每个维度 0-100 分）

### 1. 高概念可传播性
- 能否一句话说清核心卖点？请写出你认为最佳的一句话卖点
- 这句话是否包含：冲突 + 反转 + 情感钩子？

### 2. 角色共情力
- 观众能否在 10 分钟内代入主角？
- 主角是否有普世的内心渴望和致命缺陷？

### 3. 前 10 分钟钩子
- 开场是否建立了悬念或冲突？观众是否有追下去的理由？

### 4. 情感曲线设计
- 是否张弛有度？高潮前是否有情绪酝酿？结尾是否有情感释放？
- 绘制简易情感曲线（用文字描述各段落情感走向）

### 5. 名场面密度
- 列出可以剪入预告片的名场面
- 是否有可截图传播的金句？是否有出乎意料的反转？

### 6. 市场契合度
- 最接近的已上映成功影片？目标受众画像？
- 潜在市场风险？是否有跨文化传播潜力？

### 7. 深度与娱乐性平衡
- 主题是否有社会共鸣？深刻内容是否用故事而非说教传达？
- 观众看完是否有讨论欲望（社交货币）？

### 8. IP/续集潜力
- 世界观是否可扩展？角色是否值得再看？是否留有系列化空间？

## 输出格式
1. 先给出**综合市场评分**和一句话定性（如"具备黑马潜质"/"安全但缺乏爆点"）
2. 用表格展示 8 个维度的评分
3. 每个维度给出 2-3 句分析
4. 最后给出**制片建议**：是否值得投拍、建议调整方向、目标发行策略

使用 Markdown 格式，直接输出分析内容。""",
            "user": "请从制片人视角分析以下剧本的商业潜力。",
            "temperature": 0.5,
        },
    }

    # 循环为每个 prompt 补充强制中文约束
    chinese_constraint = "\n\n【重要提示】请确保所有输出内容严格且完全使用中文（包括所有标题、标签和术语），切勿混用英文单词。"
    for key in section_prompts:
        section_prompts[key]["system"] += chinese_constraint

    prompt_config = section_prompts.get(section_type)
    if not prompt_config:
        return {"content": f"未知的章节类型：{section_type}"}

    user_prompt = prompt_config["user"] + context_text

    try:
        content, _ = await call_llm(
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            model=DEFAULT_MODEL,
            temperature=prompt_config.get("temperature", 0.7),
            max_tokens=4000,
        )
        return {"content": content.strip()}
    except Exception as e:
        return {"content": f"生成失败：{str(e)}"}


# ─── 小说创作 API ─────────────────────────────────────────────────────────────

class NovelProjectRequest(BaseModel):
    project_id: Optional[str] = None
    genre: str = "古言"           # 古言/现言/仙侠/末世
    audience: str = "女频"        # 女频/男频
    tone: str = "爽文"            # 爽文/虐恋
    female_lead_identity: str = "流亡公主"  # 女主身份
    model_name: Optional[str] = None


@app.post("/api/novel/start")
async def start_novel_project(req: NovelProjectRequest):
    """启动新的小说创作项目（步骤1-3）"""
    global _running_tasks

    project_id = req.project_id or str(uuid.uuid4())

    # 检查当前项目是否在运行
    state = await blackboard.get_workflow_state(project_id)
    if state and state.get("status") == WorkflowStatus.RUNNING.value and project_id in _running_tasks and not _running_tasks[project_id].done():
        raise HTTPException(status_code=409, detail=f"项目 {project_id} 正在运行，请等待完成或重置")

    async def run_workflow():
        orch = NovelOrchestrator(blackboard)
        try:
            await orch.run_full_workflow(
                project_id=project_id,
                genre=req.genre,
                audience=req.audience,
                tone=req.tone,
                female_lead_identity=req.female_lead_identity,
                model_name=req.model_name,
                progress_callback=lambda msg: blackboard.log_agent(
                    project_id, "系统", AgentStatus.THINKING, msg
                )
            )
        except Exception as e:
            print(f"小说工作流异常 [{project_id}]: {e}")
            import traceback
            traceback.print_exc()

    _running_tasks[project_id] = asyncio.create_task(run_workflow())

    return {
        "status": "started",
        "project_id": project_id,
        "message": f"小说项目 {project_id} 已启动（选题→大纲→骨架诊断）"
    }


@app.post("/api/novel/{project_id}/select-skeleton")
async def select_skeleton(project_id: str, skeleton: str = Body(..., embed=True)):
    """选择骨架（步骤3完成后，用户选择后继续）"""
    orch = NovelOrchestrator(blackboard)
    orch.project_id = project_id
    await orch.select_skeleton(skeleton)

    return {
        "status": "ok",
        "message": "骨架已选择，可以继续生成正文"
    }


@app.post("/api/novel/{project_id}/generate-chapter")
async def generate_chapter(
    project_id: str,
    chapter_number: Optional[int] = None,
    model_name: Optional[str] = None
):
    """生成指定章节（步骤5）"""
    orch = NovelOrchestrator(blackboard)
    orch.project_id = project_id
    await orch.run_step_5_generate_chapter(
        chapter_number=chapter_number,
        model_name=model_name
    )

    return {
        "status": "ok",
        "message": f"{'第' + str(chapter_number) + '章' if chapter_number else '第一章'}正文已生成"
    }


@app.post("/api/novel/{project_id}/review")
async def review_novel(project_id: str, model_name: Optional[str] = None):
    """评审小说（步骤6）"""
    orch = NovelOrchestrator(blackboard)
    orch.project_id = project_id
    await orch.run_step_6_review(model_name=model_name)

    return {
        "status": "ok",
        "message": "评审完成"
    }


@app.post("/api/novel/{project_id}/optimize-opening")
async def optimize_opening(project_id: str, model_name: Optional[str] = None):
    """优化开头（步骤7）"""
    orch = NovelOrchestrator(blackboard)
    orch.project_id = project_id
    await orch.run_step_7_opening(model_name=model_name)

    return {
        "status": "ok",
        "message": "开头建议已生成"
    }


@app.post("/api/novel/{project_id}/complete")
async def complete_novel(project_id: str):
    """完成小说项目（步骤8-9）"""
    orch = NovelOrchestrator(blackboard)
    orch.project_id = project_id
    await orch.complete_workflow()

    return {
        "status": "completed",
        "message": "小说创作已完成"
    }


# ─── 小说创作步骤控制 ─────────────────────────────────────────────────────────

@app.post("/api/novel/{project_id}/step/topic")
async def novel_step_topic(project_id: str, model_name: Optional[str] = None):
    """步骤1：选题"""
    orch = NovelOrchestrator(blackboard)
    orch.project_id = project_id
    await orch.run_step_1_topic(model_name=model_name)
    return {"status": "ok", "message": "选题已生成"}


@app.post("/api/novel/{project_id}/step/outline")
async def novel_step_outline(project_id: str, model_name: Optional[str] = None):
    """步骤2：大纲"""
    orch = NovelOrchestrator(blackboard)
    orch.project_id = project_id
    await orch.run_step_2_outline(model_name=model_name)
    return {"status": "ok", "message": "大纲已生成"}


@app.post("/api/novel/{project_id}/step/title")
async def novel_step_title(project_id: str, model_name: Optional[str] = None):
    """步骤2.5：书名生成"""
    orch = NovelOrchestrator(blackboard)
    orch.project_id = project_id
    await orch.run_step_2_5_title(model_name=model_name)
    return {"status": "ok", "message": "书名已生成，请选择"}


@app.post("/api/novel/{project_id}/select-title")
async def novel_select_title(project_id: str, title: str = Body(..., embed=True)):
    """选择书名"""
    orch = NovelOrchestrator(blackboard)
    orch.project_id = project_id
    await orch.select_title(title)
    return {
        "status": "ok",
        "message": "书名已选择",
        "selected_title": title
    }


@app.post("/api/novel/{project_id}/step/diagnostics")
async def novel_step_diagnostics(project_id: str, model_name: Optional[str] = None):
    """步骤3：骨架诊断"""
    orch = NovelOrchestrator(blackboard)
    orch.project_id = project_id
    await orch.run_step_3_diagnostics(model_name=model_name)
    return {"status": "ok", "message": "骨架诊断完成，请选择候选骨架"}
