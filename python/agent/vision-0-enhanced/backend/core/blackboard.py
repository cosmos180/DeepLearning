"""
blackboard.py — 共享工作区（黑板系统）
实现所有 Agent 共享的中心化状态存储，支持发布/订阅模式
"""

import json
import asyncio
import aiosqlite
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, AsyncGenerator

DB_PATH = Path(__file__).parent.parent / "data" / "blackboard.db"


class ArtifactType(str, Enum):
    # 小说创作相关
    TOPIC_IDEAS = "topic_ideas"           # 选题创意
    NOVEL_OUTLINE = "novel_outline"        # 小说大纲/骨架
    TITLE_CANDIDATES = "title_candidates"  # 候选书名（20个）
    SELECTED_TITLE = "selected_title"      # 选中的书名
    CHARACTER_SETUPS = "character_setups"  # 角色设定
    SKELETON_CANDIDATES = "skeleton_candidates"  # 候选骨架（3个）
    SELECTED_SKELETON = "selected_skeleton"  # 选中的骨架
    CHAPTER_CONTENT = "chapter_content"    # 章节正文
    ALL_CHAPTERS = "all_chapters"          # 完整小说
    OPENING_SUGGESTION = "opening_suggestion"  # 开篇建议
    REVIEW_COMMENTS = "review_comments"    # 评审意见

    # 影视制作相关（保留用于兼容）
    LOGLINE = "logline"
    CHARACTER_SHEETS = "character_sheets"
    BEAT_SHEET = "beat_sheet"
    SCRIPT = "script"
    SCRIPT_NOTES = "script_notes"
    REVIEW_REPORT = "review_report"
    SHOT_LIST = "shot_list"
    VIDEO_PROMPTS = "video_prompts"
    DIRECTOR_NOTES = "director_notes"
    STYLE_GUIDE = "style_guide"


class WorkflowStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING_HUMAN = "waiting_human"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    FAILED = "failed"


class Blackboard:
    """
    中心化共享工作区，所有 Agent 通过此类读写数据。
    实现了发布/订阅机制，支持 Agent 的异步通知。
    """

    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._subscribers: dict[str, list[asyncio.Queue]] = {}
        self._db: Optional[aiosqlite.Connection] = None

    async def init(self):
        """初始化数据库，创建所需表结构"""
        self._db = await aiosqlite.connect(DB_PATH)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL DEFAULT 'default',
                artifact_type TEXT NOT NULL,
                content TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS workflow_state (
                id INTEGER PRIMARY KEY,
                project_id TEXT NOT NULL,
                status TEXT NOT NULL,
                current_step TEXT,
                seed TEXT,
                target_duration TEXT,
                style TEXT,
                iteration_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL DEFAULT 'default',
                agent_name TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                detail TEXT,
                created_at TEXT NOT NULL
            )
        """)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS trace_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL DEFAULT 'default',
                agent_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                content TEXT,
                token_count INTEGER DEFAULT 0,
                duration_ms INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        await self._db.commit()

    async def close(self):
        if self._db:
            await self._db.close()

    # ─── Artifact 管理 ────────────────────────────────────────────────────────

    async def publish(self, project_id: str, artifact_type: ArtifactType, content: str) -> None:
        """发布一个新的产出物到黑板，并通知所有订阅者"""
        now = datetime.now().isoformat()
        # 检查是否已存在
        async with self._db.execute(
            "SELECT id, version FROM artifacts WHERE project_id = ? AND artifact_type = ?",
            (project_id, artifact_type.value)
        ) as cursor:
            row = await cursor.fetchone()

        if row:
            new_version = row[1] + 1
            await self._db.execute(
                "UPDATE artifacts SET content=?, version=?, updated_at=? WHERE project_id=? AND artifact_type=?",
                (content, new_version, now, project_id, artifact_type.value)
            )
        else:
            await self._db.execute(
                "INSERT INTO artifacts (project_id, artifact_type, content, version, created_at, updated_at) VALUES (?,?,?,1,?,?)",
                (project_id, artifact_type.value, content, now, now)
            )
        await self._db.commit()

        # 通知订阅者
        if artifact_type.value in self._subscribers:
            for queue in self._subscribers[artifact_type.value]:
                await queue.put({"type": artifact_type.value, "content": content})

    async def read(self, project_id: str, artifact_type: ArtifactType) -> Optional[str]:
        """读取指定类型的最新产出物"""
        async with self._db.execute(
            "SELECT content FROM artifacts WHERE project_id = ? AND artifact_type = ?",
            (project_id, artifact_type.value)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    async def read_all(self, project_id: str) -> dict[str, Any]:
        """读取所有产出物"""
        result = {}
        async with self._db.execute(
            "SELECT artifact_type, content, version, updated_at FROM artifacts WHERE project_id = ?",
            (project_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                result[row[0]] = {
                    "content": row[1],
                    "version": row[2],
                    "updated_at": row[3]
                }
        return result

    async def delete_project(self, project_id: str):
        """删除特定项目的所有数据（清空）"""
        await self._db.execute("DELETE FROM artifacts WHERE project_id = ?", (project_id,))
        await self._db.execute("DELETE FROM workflow_state WHERE project_id = ?", (project_id,))
        await self._db.execute("DELETE FROM agent_logs WHERE project_id = ?", (project_id,))
        await self._db.execute("DELETE FROM trace_events WHERE project_id = ?", (project_id,))
        await self._db.commit()

    async def clear_all(self):
        """清空所有数据（用于新项目开始）"""
        await self._db.execute("DELETE FROM artifacts")
        await self._db.execute("DELETE FROM workflow_state")
        await self._db.execute("DELETE FROM agent_logs")
        await self._db.execute("DELETE FROM trace_events")
        await self._db.commit()

    async def publish_many(self, project_id: str, artifacts: dict[str, str]) -> None:
        """
        批量发布产出物到黑板。
        artifacts: {artifact_type_value: content, ...}
        用于从中间步骤启动时预置前置产出物。
        """
        for artifact_type_str, content in artifacts.items():
            # 验证是否为有效的 ArtifactType
            try:
                artifact_type = ArtifactType(artifact_type_str)
                await self.publish(project_id, artifact_type, content)
            except ValueError:
                # 忽略无效的类型
                print(f"Warning: Unknown artifact type '{artifact_type_str}' ignored")

    # ─── 工作流状态管理 ───────────────────────────────────────────────────────

    async def set_workflow_state(self, project_id: str, status: WorkflowStatus,
                                  current_step: Optional[str] = None,
                                  seed: Optional[str] = None,
                                  target_duration: Optional[str] = None,
                                  style: Optional[str] = None,
                                  iteration_count: Optional[int] = None):
        now = datetime.now().isoformat()
        async with self._db.execute(
            "SELECT id, iteration_count FROM workflow_state WHERE project_id = ?", (project_id,)
        ) as cursor:
            row = await cursor.fetchone()

        if row:
            updates = ["status=?", "updated_at=?"]
            params = [status.value, now]
            if current_step is not None:
                updates.append("current_step=?"); params.append(current_step)
            if iteration_count is not None:
                updates.append("iteration_count=?"); params.append(iteration_count)
            params.append(project_id)
            await self._db.execute(
                f"UPDATE workflow_state SET {', '.join(updates)} WHERE project_id=?", params
            )
        else:
            await self._db.execute(
                "INSERT INTO workflow_state (project_id, status, current_step, seed, target_duration, style, iteration_count, created_at, updated_at) VALUES (?,?,?,?,?,?,0,?,?)",
                (project_id, status.value, current_step, seed, target_duration, style, now, now)
            )
        await self._db.commit()
        await self._notify_state_change()

    async def get_workflow_state(self, project_id: str) -> Optional[dict]:
        async with self._db.execute(
            "SELECT * FROM workflow_state WHERE project_id = ?", (project_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                cols = [d[0] for d in cursor.description]
                return dict(zip(cols, row))
        return None

    # ─── Agent 日志 ───────────────────────────────────────────────────────────

    async def log_agent(self, project_id: str, agent_name: str, status: AgentStatus,
                         message: str, detail: Optional[str] = None):
        now = datetime.now().isoformat()
        await self._db.execute(
            "INSERT INTO agent_logs (project_id, agent_name, status, message, detail, created_at) VALUES (?,?,?,?,?,?)",
            (project_id, agent_name, status.value, message, detail, now)
        )
        await self._db.commit()
        await self._notify_state_change()

    async def get_agent_logs(self, project_id: str, limit: int = 50) -> list[dict]:
        async with self._db.execute(
            "SELECT agent_name, status, message, detail, created_at FROM agent_logs WHERE project_id = ? ORDER BY id DESC LIMIT ?",
            (project_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {"agent": r[0], "status": r[1], "message": r[2], "detail": r[3], "time": r[4]}
                for r in reversed(rows)
            ]

    async def get_all_projects(self) -> list[dict]:
        """获取所有项目概览"""
        projects = []
        async with self._db.execute("""
            SELECT w.project_id, w.status, w.current_step, w.seed, w.target_duration, w.style, w.updated_at,
                   (SELECT message FROM agent_logs a WHERE a.project_id = w.project_id AND a.status = 'FAILED' ORDER BY created_at DESC LIMIT 1) as error_msg
            FROM workflow_state w
            ORDER BY w.updated_at DESC
        """) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                project_id = row[0]
                
                # 提取标题和简介 (从 logline 或者 取 seed 前20字)
                title = row[3] if row[3] else "未命名项目"
                summary = "暂无简介..."
                
                async with self._db.execute(
                    "SELECT content FROM artifacts WHERE project_id = ? AND artifact_type = 'logline'",
                    (project_id,)
                ) as art_cursor:
                    art_row = await art_cursor.fetchone()
                    if art_row and art_row[0]:
                        try:
                            import json
                            logline_data = json.loads(art_row[0])
                            
                            title = logline_data.get("title", title)
                            summary = logline_data.get("one_sentence_summary", summary)
                        except:
                            # 降级处理
                            lines = art_row[0].split('\n')
                            for line in lines:
                                if line.strip() and not line.startswith('#'):
                                    summary = line.strip()
                                    break
                            
                projects.append({
                    "project_id": project_id,
                    "status": row[1],
                    "current_step": row[2],
                    "seed": row[3],
                    "target_duration": row[4],
                    "style": row[5],
                    "updated_at": row[6],
                    "error_msg": row[7],
                    "title": title,
                    "summary": summary
                })
        return projects

    # ─── 追踪事件 (Observability) ─────────────────────────────────────────────

    async def trace(self, agent_name: str, event_type: str,
                    content: str = "", token_count: int = 0,
                    duration_ms: int = 0, project_id: str = "default"):
        now = datetime.now().isoformat()
        await self._db.execute(
            "INSERT INTO trace_events (project_id, agent_name, event_type, content, token_count, duration_ms, created_at) VALUES (?,?,?,?,?,?,?)",
            (project_id, agent_name, event_type, content, token_count, duration_ms, now)
        )
        await self._db.commit()

    async def get_traces(self, project_id: str = "default", limit: int = 100) -> list[dict]:
        async with self._db.execute(
            "SELECT agent_name, event_type, content, token_count, duration_ms, created_at FROM trace_events WHERE project_id=? ORDER BY id DESC LIMIT ?",
            (project_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {"agent": r[0], "event": r[1], "content": r[2],
                 "tokens": r[3], "duration_ms": r[4], "time": r[5]}
                for r in reversed(rows)
            ]

    # ─── 发布/订阅 ────────────────────────────────────────────────────────────

    def subscribe(self, artifact_type: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if artifact_type not in self._subscribers:
            self._subscribers[artifact_type] = []
        self._subscribers[artifact_type].append(queue)
        return queue

    def unsubscribe(self, artifact_type: str, queue: asyncio.Queue):
        if artifact_type in self._subscribers:
            self._subscribers[artifact_type].remove(queue)

    # ─── SSE 事件流 ───────────────────────────────────────────────────────────

    _sse_queues: list[asyncio.Queue] = []

    async def _notify_state_change(self):
        for q in self._sse_queues:
            try:
                q.put_nowait({"type": "state_update"})
            except asyncio.QueueFull:
                pass

    def subscribe_sse(self) -> asyncio.Queue:
        q = asyncio.Queue(maxsize=5000)
        self._sse_queues.append(q)
        return q

    def unsubscribe_sse(self, q: asyncio.Queue):
        if q in self._sse_queues:
            self._sse_queues.remove(q)
            
    async def stream_output(self, project_id: str, agent_name: str, chunk: str):
        """流式广播产生的 token"""
        # print(f"DEBUG STREAM OUTPUT: {repr(chunk)}", flush=True)
        for q in self._sse_queues:
            try:
                q.put_nowait({"type": "stream", "project_id": project_id, "agent": agent_name, "chunk": chunk})
            except asyncio.QueueFull:
                pass


# 全局单例
blackboard = Blackboard()
