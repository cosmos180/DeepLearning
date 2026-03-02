# Vision-0 Enhanced — AI 影视制片厂

> 基于多智能体系统（Multi-Agent System）的影视内容自动化创作平台

## 系统架构

```
vision-0-enhanced/
├── backend/
│   ├── agents/                 # 专职 Agent 实现
│   │   ├── creator_agent.py    # 原著作者：故事圣经
│   │   ├── screenwriter_agent.py  # 编剧：Fountain 格式剧本
│   │   ├── reviewer_agent.py   # 剧本评审：双维临床诊断
│   │   ├── director_agent.py   # 导演：分镜 + 视频 Prompt
│   │   └── art_director_agent.py  # 艺术总监：视觉风格圣经
│   ├── core/
│   │   ├── blackboard.py       # 共享工作区（黑板系统）
│   │   ├── base_agent.py       # Agent 基类（含反思机制）
│   │   ├── llm_client.py       # LLM 调用客户端
│   │   └── orchestrator.py     # 动态调度器（状态机）
│   └── api/
│       └── main.py             # FastAPI 后端
├── frontend/
│   └── index.html              # 可视化 Web 界面
├── .env.example                # 环境变量模板
├── start.sh                    # 一键启动脚本
└── README.md
```

## 核心优化特性

相比原始 Vision-0，本系统实现了以下四大优化：

### 1. 共享工作区（黑板系统）
所有 Agent 通过 SQLite 数据库共享产出物，支持发布/订阅机制。产出物自动版本管理，可追溯每次修订历史。

### 2. Agent 反思机制
每个 Agent 完成任务后，会自动调用一个轻量模型（gpt-4.1-nano）对自己的输出进行质量评估。若评分不足，自动进行修订，最多进行 1 轮反思-修订循环。

### 3. 并行化工作流
编剧和艺术总监同时工作（`asyncio.gather`），将原本串行的流程改为并行，大幅缩短创作周期。

### 4. 动态路由与修订循环
调度器根据评审结论（PASS / MINOR_FIX / REJECT）动态决定工作流走向。评审不通过时自动触发修订循环（最多 2 轮），无需人工干预。

### 5. 可观测性追踪
所有 LLM 调用、反思过程、Token 消耗均记录到数据库，可通过界面实时查看。

## 快速开始

### 环境要求
- Python 3.9+
- OpenAI API Key（支持 gpt-4.1-mini 和 gpt-4.1-nano）

### 安装依赖

```bash
pip install openai fastapi uvicorn python-dotenv aiosqlite sse-starlette
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY
```

### 启动服务

**方式一：使用启动脚本**
```bash
chmod +x start.sh
./start.sh
```

**方式二：手动启动**
```bash
# 终端 1：启动后端
OPENAI_API_KEY=your_key python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8765

# 终端 2：启动前端（可选，也可直接用浏览器打开 frontend/index.html）
cd frontend && python3 -m http.server 8766
```

### 访问界面

- **前端界面**：`http://localhost:8766` 或直接用浏览器打开 `frontend/index.html`
- **后端 API**：`http://localhost:8765`
- **API 文档**：`http://localhost:8765/docs`

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/project/start` | 启动新项目 |
| POST | `/api/project/reset` | 重置项目 |
| GET | `/api/state` | 获取当前状态 |
| GET | `/api/artifact/{type}` | 获取指定产出物 |
| GET | `/api/traces` | 获取追踪事件 |
| GET | `/api/events` | SSE 实时事件流 |

### 产出物类型

| 类型 | 说明 |
|------|------|
| `logline` | 故事一句话梗概 |
| `character_sheets` | 角色设定档案 |
| `beat_sheet` | 故事节拍表 |
| `script` | Fountain 格式剧本 |
| `script_notes` | 编剧备注 + 实体状态追踪表 |
| `review_report` | 双维临床诊断报告 |
| `shot_list` | 分镜清单 |
| `video_prompts` | 视频生成 Prompt（英文） |
| `director_notes` | 导演备注 |
| `style_guide` | 视觉风格圣经 |

## 工作流示意

```
用户输入创意种子
      ↓
  原著作者 Agent
  (故事圣经)
      ↓
  ┌───┴───┐  ← 并行执行
编剧 Agent  艺术总监 Agent
(剧本)    (视觉风格圣经)
  └───┬───┘
      ↓
 评审 Agent
 (双维诊断)
      ↓
  PASS? ──否──→ 编剧修订（最多2轮）
    ↓
 导演 Agent
 (分镜 + 视频Prompt)
      ↓
    完成 🎬
```
