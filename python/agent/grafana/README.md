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
| `search_es_aggregation` | **聚合统计**（获取所有唯一值） | "有哪些错误类型？" |
| `get_es_summary` | 获取数据摘要 | "sdc 平台数据摘要" |

**聚合统计工具说明：**

当需要统计字段的所有唯一值时，使用 `search_es_aggregation`：
- 返回字段的所有唯一值（不受 size 限制）
- 自动统计每个值的数量和占比
- 固定格式的表格输出

示例：
```
"查询今天 metrics.msg: 'uploadTrack' 的告警中，有哪些错误类型？"
→ search_es_aggregation(lucene_query='metrics.msg: "uploadTrack" AND metrics.msg: "reason"',
                         agg_field='metrics.payload.code',
                         time_range='today',
                         agg_size=200)
```

### 告警工具

| 工具 | 说明 | 示例 |
|------|------|------|
| `check_all_alerts` | 检查所有告警 | "有没有触发告警？" |
| `check_alert_by_rule` | 检查特定规则 | "检查 cache_info_json 告警" |
| `get_alert_rules` | 获取规则列表 | "显示所有告警规则" |
| `analyze_alert_trend` | 分析告警趋势 | "设备 ABC123 的告警趋势" |
| `get_alert_suggestions` | 获取优化建议 | "告警优化建议" |
| `get_camera_config` | 获取摄像头配置 (Tupu BI) | "获取设备 a8:3f:a1:30:16:fb 的配置" |

### Dashboard 工具

| 工具 | 说明 | 示例 |
|------|------|------|
| `list_dashboards` | 列出仪表板 | "列出 ipc 文件夹的仪表板" |
| `get_dashboard_panels` | 获取面板列表 | "显示 dashboard 的面板" |
| `search_panels` | 搜索面板 | "搜索包含 crash 的面板" |
| `get_panel_info` | 获取面板详情 | "面板 5 的详细信息" |
| `get_panel_query_results` | **执行 panel 查询**（返回实际数据） | "查询 panel 2 的数据" |
| `get_panel_render_url` | **获取访问链接**（无需 render 插件） | "获取 panel 13 的链接" |
| `download_panel_render` | **下载截图/链接**（自动回退） | "下载 panel 2 的截图" |
| `send_panel_to_email` | **发送邮件**（自动回退到链接） | "把 panel 2 发到我邮箱" |
| `get_dashboard_recommendations` | 获取推荐 | "sdc 平台的推荐仪表板" |

---

## Panel 访问功能

### 🎯 智能回退机制

**好消息**：`download_panel_render` 和 `send_panel_to_email` 已内置智能回退功能！

| 工具 | render 可用时 | render 不可用时 |
|------|--------------|----------------|
| `download_panel_render` | 下载 PNG 图片到本地 | 返回直接访问链接 |
| `send_panel_to_email` | 发送带图片的 HTML 邮件 | 发送带链接的 HTML 邮件 |

### 使用方式

```python
# 这些工具会自动处理 render 插件是否可用的情况
download_panel_render(dashboard_uid='urJcwIvHz', panel_id=13, time_range='today')
send_panel_to_email(dashboard_uid='urJcwIvHz', panel_id=13, recipients='user@example.com')
```

**输出示例（render 不可用时）**：

```
🔗 Panel 直接访问链接
============================================================
  Dashboard UID: urJcwIvHz
  Panel ID: 13
  时间范围: today
============================================================

  📎 点击访问:
  https://g.dev.tuputech.com/d/urJcwIvHz/ye-wu-yi-chang-jian-kong?orgId=1&viewPanel=13&from=now%2Fd&to=now

  💡 提示: 此链接会直接打开 Grafana 并显示指定的 Panel

⚠️ 注意: Grafana Image Renderer 插件不可用，已提供直接访问链接作为备用方案。
```

### 邮件效果对比

| render 可用 | render 不可用 |
|------------|--------------|
| 📸 邮件中内嵌图片 | 🔗 邮件中带按钮链接 |
| ![Panel截图](image) | [🔗 打开 Panel] |
| 可直接查看 | 点击跳转到 Grafana |

### 环境变量配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `GRAFANA_URL` | Grafana 服务器 URL | `https://g.dev.tuputech.com` |
| `GRAFANA_API_KEY` | Grafana API Key（用于获取 panel 信息） | - |

邮件配置参考 `monitoring/config/email.yaml`。

## 自然语言示例

### ES 查询
```
"查询 sdc 平台最近 12 小时的数据"
"搜索设备 ABC123 的问题"
"cache_info.json 有哪些异常？"
"最近一天 sdc 平台 disk 使用率超过 80% 的设备"
"查询今天 uploadTrack 告警中有哪些错误类型？"  # 使用聚合统计
"统计 metrics.payload.code 的所有值及其数量"    # 使用聚合统计
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
"查询 dashboard xxx 的 panel 2 的数据"  # 执行实际查询
"下载 panel 2 的截图"                   # 保存到本地
"把 panel 2 的截图发到 user@example.com" # 发送邮件
```

## Tupu BI 集成

Agent 集成了 Tupu BI MCP 服务，可以获取告警设备的摄像头配置信息。

### 功能

- **自动补充设备信息**：在检查告警时自动获取摄像头配置
- **独立查询工具**：直接查询指定设备的配置信息
- **多种设备标识符**：支持 MAC 地址和序列号

### 使用方式

#### 方式 1: 自动补充（推荐）

在查询告警时设置 `enrich_with_camera_config=True`：

```
"检查 sdc 平台的告警，并显示设备配置信息"
```

#### 方式 2: 独立查询

直接查询指定设备的配置：

```
"获取设备 a8:3f:a1:30:16:fb 的摄像头配置"
"查询序列号 6AB2F0C3E97DD45610FE4C45EA1E71B1 的配置"
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TUPI_BI_API_BASE` | Tupu BI API 地址 | `https://api.bi.tuputech.com` |

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
