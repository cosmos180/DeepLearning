# Grafana ADK Agent

基于 Google Agent Development Kit 的智能监控告警 Agent。

## 概述

这个 Agent 将 Grafana 的监控查询功能转换为智能对话接口，支持：

- **Elasticsearch 查询** - 自然语言查询 ES 数据
- **告警检查** - 智能告警分析和建议
- **Dashboard 探索** - 对话式仪表板浏览

## 快速开始

### 1. 安装依赖

```bash
make agent-install
```

### 2. 设置 API Key

```bash
export ZHIPU_API_KEY="your-zhipu-api-key"
```

### 3. 运行 Agent

```bash
# 方式 1: 使用 Makefile (推荐)
make agent-run

# 方式 2: 直接使用 adk 命令
cd agent
adk run .
```

### 4. 与 Agent 对话

```
Running agent grafana_monitoring_agent, type exit to exit.

[user]: 查询 sdc 平台最近 24 小时的数据
[grafana_monitoring_agent]: [显示查询结果]

[user]: 有没有触发告警？
[grafana_monitoring_agent]: [检查告警规则并返回结果]

[user]: 列出 ipc 文件夹的仪表板
[grafana_monitoring_agent]: [列出仪表板]

[user]: exit
```

## 可用工具

### ES 查询工具

| 工具 | 说明 | 示例 |
|------|------|------|
| `search_es_by_platform` | 按平台搜索 | "查询 sdc 平台数据" |
| `search_es_by_device` | 按设备搜索 | "设备 ABC123 有什么问题？" |
| `search_es_by_metric` | 按指标搜索 | "cache 有什么异常？" |
| `search_es_custom` | 自定义 Lucene 查询 | "搜索 metrics.platform:'sdc'" |
| `get_es_summary` | 获取数据摘要 | "sdc 平台数据摘要" |

### 告警工具

| 工具 | 说明 | 示例 |
|------|------|------|
| `check_all_alerts` | 检查所有告警 | "有没有触发告警？" |
| `check_alert_by_rule` | 检查特定规则 | "检查 cache_info_json 告警" |
| `get_alert_rules` | 获取规则列表 | "显示所有告警规则" |
| `analyze_alert_trend` | 分析告警趋势 | "设备 ABC123 的告警趋势" |
| `get_alert_suggestions` | 获取优化建议 | "告警优化建议" |

### Dashboard 工具

| 工具 | 说明 | 示例 |
|------|------|------|
| `list_dashboards` | 列出仪表板 | "列出 ipc 文件夹的仪表板" |
| `get_dashboard_panels` | 获取面板列表 | "显示 dashboard 的面板" |
| `search_panels` | 搜索面板 | "搜索包含 crash 的面板" |
| `get_panel_info` | 获取面板详情 | "面板 5 的详细信息" |
| `get_dashboard_recommendations` | 获取推荐 | "sdc 平台的推荐仪表板" |

## 自然语言示例

### ES 查询
```
"查询 sdc 平台最近 12 小时的数据"
"搜索设备 ABC123 的问题"
"cache_info.json 有哪些异常？"
"最近一天 sdc 平台 disk 使用率超过 80% 的设备"
```

### 告警检查
```
"有没有触发告警？"
"检查 sdc 的 cache 告警"
"disk 告警情况如何？"
"设备 ABC123 的告警趋势"
```

### Dashboard 探索
```
"列出 ipc 文件夹的仪表板"
"显示设备监控的面板"
"搜索包含 crash 的面板"
"面板 5 的详细信息"
```

## 配置

### 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `ZHIPU_API_KEY` | 智谱 AI API Key | 是 |
| `GRAFANA_URL` | Grafana 服务器 URL | 否 |
| `GRAFANA_API_KEY` | Grafana API Key | 否 |

### Elasticsearch 配置

在 `agent/tools/es_query_tool.py` 中修改：

```python
ES_HOST = "172.26.2.88"
ES_PORT = 39202
```

## 架构

```
agent/
├── __init__.py             # Root Agent 定义 (adk run 入口)
├── grafana_agent_simple.py # 简化版 (不需要 LLM)
├── tools/
│   ├── __init__.py
│   ├── es_query_tool.py    # ES 查询工具
│   ├── alert_tool.py       # 告警检查工具
│   └── dashboard_tool.py   # Dashboard 探索工具
├── requirements.txt
└── README.md
```

## Makefile 命令

```bash
make agent-install   # 安装依赖
make agent-run       # 运行 ADK Agent (需要 ZHIPU_API_KEY)
make agent-run-simple # 运行简化版 (不需要 LLM)
make agent-tools     # 列出所有工具
```

## 模型

- **默认**: GLM-4-Flash (智谱 AI)
- **API**: OpenAI 兼容端点 (`https://open.bigmodel.cn/api/paas/v4/`)

## 故障排查

### Agent 启动失败

1. 确保设置了 `ZHIPU_API_KEY`
2. 检查网络连接到智谱 API
3. 查看日志: `tail -f /tmp/agents_log/agent.latest.log`

### 工具调用失败

1. 确保 Elasticsearch 可访问
2. 检查 Grafana API Key (Dashboard 功能需要)
3. 使用 `make agent-run-simple` 测试工具是否正常

## 许可证

MIT License
