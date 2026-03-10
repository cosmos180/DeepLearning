# 小说创作自动化工具

基于多智能体系统（Multi-Agent System）的小说创作自动化平台，实现从选题到成稿的完整创作流程。

## 系统架构

```
vision-0-enhanced/
├── backend/
│   ├── agents/
│   │   └── novel/                 # 小说创作 Agents
│   │       ├── topic_agent.py            # 选题策划
│   │       ├── outline_agent.py          # 大纲架构师
│   │       ├── skeleton_diagnostics_agent.py  # 骨架诊断师
│   │       ├── novel_generator_agent.py  # 小说作家
│   │       ├── novel_reviewer_agent.py   # 毒舌评审
│   │       └── opening_optimizer_agent.py # 开头优化师
│   ├── core/
│   │   ├── blackboard.py          # 共享工作区
│   │   ├── base_agent.py          # Agent 基类
│   │   ├── llm_client.py          # LLM 调用客户端
│   │   └── novel_orchestrator.py  # 小说工作流编排器
│   └── api/
│       └── main.py                # FastAPI 后端
├── test_novel_workflow.py         # 测试脚本
└── NOVEL_README.md                # 本文档
```

## 核心功能

### 9步创作流程

1. **选题生成** - 根据题材、风格、女主身份等参数，批量生成高概念选题
2. **大纲生成** - 将选题转化为完整的故事大纲（故事梗概、角色设定、章节大纲）
3. **骨架诊断** - 对大纲进行逻辑诊断，生成3个优化后的候选骨架
4. **用户选择** - 人工选择最优骨架（可循环2-3步）
5. **生成正文** - 根据骨架生成小说章节
6. **评审分析** - 毒舌评审，分析读者留存点和弃读点
7. **开头优化** - 生成多个版本的开篇建议
8. **精修完成** - 人工精修开头和第一章
9. **完成** - 输出最终小说

## 支持的题材

- **古言** - 大漠商战、强强博弈、极致羁绊
- **现言** - 都市、职场、豪门
- **仙侠** - 修真、神魔、师徒
- **末世** - 丧尸、异能、生存

## 快速开始

### 环境要求

- Python 3.9+
- OpenAI API Key（或兼容的 API）

### 安装依赖

```bash
cd /home/bughero/Documents/github/DeepLearning/python/agent/vision-0-enhanced
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 API_KEY
```

### 启动服务

```bash
# 启动后端
python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8765
```

## API 接口

### 启动小说项目

```bash
POST /api/novel/start
{
  "project_id": "my_novel_001",  # 可选，不填则自动生成
  "genre": "古言",
  "audience": "女频",
  "tone": "爽文",
  "female_lead_identity": "西域舞姬(实为谍报头子)"
}
```

### 选择骨架

```bash
POST /api/novel/{project_id}/select-skeleton
Content-Type: application/json

"## 候选骨架一：强化冲突版\n\n..."
```

### 生成章节

```bash
POST /api/novel/{project_id}/generate-chapter
{
  "chapter_number": 1  # 可选，不填则生成第一章
}
```

### 评审小说

```bash
POST /api/novel/{project_id}/review
```

### 优化开头

```bash
POST /api/novel/{project_id}/optimize-opening
```

### 完成项目

```bash
POST /api/novel/{project_id}/complete
```

### 分步控制

```bash
# 步骤1：选题
POST /api/novel/{project_id}/step/topic

# 步骤2：大纲
POST /api/novel/{project_id}/step/outline

# 步骤3：骨架诊断
POST /api/novel/{project_id}/step/diagnostics
```

## 测试脚本

运行完整工作流测试：

```bash
python test_novel_workflow.py
```

## 核心特性

### 1. 多维随机碰撞选题策略

- 固定女主身份（X轴）
- 随机抽取 2-3 个维度进行组合（Y轴）
- 强制融合生成高概念梗概

### 2. 逻辑诊断与骨架重构

- 核心逻辑检查（主角动机、核心冲突、情感发展）
- 角色设定评估（人设鲜明度、强强关系、功能性）
- 节奏与张力分析（黄金3秒、30秒、1分钟、3分钟）

### 3. 毒舌评审系统

- 模拟目标读者听书流分析
- 评估开头吸引力
- 分析弃读点
- 给出可操作的改进建议

### 4. 去AI味写作

- 避免过于完美的解决方案
- 避免道德说教式结局
- 加入真实的生活细节
- 视觉化思维（环境、氛围、动作）

## 产出物类型

| 类型 | 说明 |
|------|------|
| `topic_ideas` | 选题创意（10个） |
| `novel_outline` | 小说大纲/骨架 |
| `character_setups` | 角色设定 |
| `skeleton_candidates` | 候选骨架（3个） |
| `selected_skeleton` | 选中的骨架 |
| `chapter_content` | 章节正文 |
| `all_chapters` | 完整小说 |
| `opening_suggestion` | 开篇建议 |
| `review_comments` | 评审意见 |

## License

MIT
