# Grafana MCP Server - 功能文档

**版本**: v1.0.0
**更新时间**: 2026-01-26
**项目**: Grafana MCP Server & ELK 监控告警系统

---

## 目录

1. [概述](#概述)
2. [MCP 服务器工具](#mcp-服务器工具)
3. [监控告警系统](#监控告警系统)
4. [命令行工具](#命令行工具)
5. [配置说明](#配置说明)

---

## 概述

本项目提供两个主要功能模块：

| 模块 | 说明 |
|------|------|
| **Grafana MCP Server** | 通过 MCP 协议访问 Grafana Dashboard、Panel 数据 |
| **ELK 监控告警系统** | 基于 Elasticsearch 的轻量级监控告警系统，支持 YAML 规则配置 |

---

## MCP 服务器工具

### 1. Dashboard 管理工具

#### list_dashboards
列出 Grafana 中的所有仪表板

```python
# 工具调用参数
{
    "grafana_url": "https://g.dev.tuputech.com",
    "api_key": "optional_api_key",
    "folder": "Production",     # 按文件夹过滤
    "tag": "API",               # 按标签过滤
    "query": "error",           # 搜索查询
    "limit": 100                # 最大结果数
}
```

**过滤选项**:
- `folder`: 按文件夹名称过滤
- `tag`: 按标签过滤
- `query`: 全文搜索查询

---

#### get_dashboard_panels
获取指定仪表板的所有面板信息

```python
{
    "grafana_url": "https://g.dev.tuputech.com",
    "dashboard_uid": "urJcwIvHz"
}
```

**返回信息**:
- 面板 ID
- 面板标题
- 面板类型 (timeseries, table, stat, logs 等)
- 数据源类型

---

#### get_panel_info
获取单个面板的详细信息

```python
{
    "grafana_url": "https://g.dev.tuputech.com",
    "dashboard_uid": "urJcwIvHz",
    "panel_id": 5
}
```

**返回信息**:
- 面板配置 (targets, datasource, queries)
- 字段映射
- 聚合方式

---

#### query_panel_data
查询面板数据

```python
{
    "grafana_url": "https://g.dev.tuputech.com",
    "dashboard_uid": "urJcwIvHz",
    "panel_id": 5,
    "time_from": "now-24h",
    "time_to": "now"
}
```

**时间范围格式**:
- `now-1h`, `now-6h`, `now-24h` - 相对时间
- `now-1d`, `now-7d` - 按天计算
- `2024-01-01 00:00:00` - 绝对时间

---

### 2. 告警管理工具

#### get_firing_alerts
获取当前正在触发的告警

```python
{
    "grafana_url": "https://g.dev.tuputech.com"
}
```

**返回信息**:
- 告警名称
- 触发状态
- 所属文件夹
- 告警 URL

---

#### get_alert_states
获取告警状态，支持过滤

```python
{
    "grafana_url": "https://g.dev.tuputech.com",
    "folder": "Production",     # 按文件夹过滤
    "state": "firing"           # firing | pending | normal | no_data
}
```

**告警状态**:
| 状态 | 说明 |
|------|------|
| `firing` | 告警正在触发 |
| `pending` | 告警等待确认 |
| `normal` | 正常状态 |
| `no_data` | 无数据 |

---

#### get_alert_rules
列出所有配置的告警规则

```python
{
    "grafana_url": "https://g.dev.tuputech.com"
}
```

---

#### get_notification_history
获取通知历史记录

```python
{
    "grafana_url": "https://g.dev.tuputech.com",
    "limit": 100
}
```

---

### 3. 数据源工具

#### list_datasources
列出所有配置的数据源

```python
{
    "grafana_url": "https://g.dev.tuputech.com"
}
```

**返回信息**:
- 数据源名称
- 数据源类型 (elasticsearch, prometheus, etc.)
- 数据源 UID
- 数据源 URL

---

#### query_datasource
直接查询数据源

```python
{
    "grafana_url": "https://g.dev.tuputech.com",
    "datasource_uid": "wsnKPH4Nk",
    "query": {...},              # 数据源特定的查询
    "time_from": "now-1h",
    "time_to": "now"
}
```

---

#### query_elasticsearch
使用 Lucene 语法直接查询 Elasticsearch

```python
{
    "grafana_url": "https://g.dev.tuputech.com",
    "datasource_uid": "wsnKPH4Nk",
    "query": 'metrics.platform: "sdc" AND metrics.msg: "局域网"',
    "time_from": "now-24h",
    "time_to": "now",
    "size": 100
}
```

**支持的 Lucene 查询语法**:
- 字段匹配: `metrics.platform: "sdc"`
- 布尔运算: `AND`, `OR`, `NOT`
- 通配符: `device*`
- 范围查询: `count:[10 TO 100]`

---

## 监控告警系统

### 架构说明

监控告警系统是一个**脱离 Grafana 的轻量级告警系统**，直接查询 Elasticsearch 并根据 YAML 规则触发告警。

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Alert Rules    │──────│  Alert Checker  │──────│  Email Notifier │
│   (YAML)        │      │   (Python)      │      │   (SMTP)        │
└─────────────────┘      └────────┬────────┘      └─────────────────┘
                                   │
                                   ▼
                            ┌─────────────────┐
                            │ Elasticsearch   │
                            │  (172.26.2.88)  │
                            └─────────────────┘
```

---

### 告警规则 YAML 格式

```yaml
name: "SDC Cache Info JSON Alert"
description: "Alert when cache_info.json exceeds threshold"

# 索引配置
index: "tupu-metrics-production-tp_ipc-*"
query: 'metrics.platform: "sdc"'

# 告警条件
alert:
  field: "metrics.cache_info.json"       # 监控字段
  threshold_type: "greater_than"         # greater_than | less_than | equal
  threshold: 10                           # 阈值
  aggregation: "terms"                    # terms | sum | avg
  aggregation_field: "deviceId"           # 聚合字段

# 时间窗口
time_window:
  range: "now-5m"                         # 查询时间范围
  schedule: "*/5 * * * *"                 # Cron 调度表达式

# 告警级别
severity: "warning"                       # critical | warning | info

# 通知配置
notification:
  type: "email"
  template: "{name}: {device_id} = {value} (threshold: {threshold})"
```

---

### 支持的告警类型

| 类型 | alert_field | 说明 |
|------|-------------|------|
| **数值阈值** | `metrics.field.name` | 监控字段的最大值是否超过阈值 |
| **文档计数** | `_count` | 监控文档数量是否超过阈值 |
| **磁盘使用率** | `metrics.disk.used_ratio` | 监控磁盘使用率 |

---

### 阈值类型

| threshold_type | 触发条件 |
|----------------|----------|
| `greater_than` | value > threshold |
| `less_than` | value < threshold |
| `greater_equal` | value >= threshold |
| `less_equal` | value <= threshold |
| `equal` | value == threshold |

---

### 告警流程

```
1. 加载 YAML 规则
       │
       ▼
2. 构建 Elasticsearch 聚合查询
       │
       ▼
3. 执行查询，按设备聚合
       │
       ▼
4. 检查每个设备的值是否超过阈值
       │
       ▼
5. 触发告警 (控制台 + 邮件)
```

---

## 命令行工具

### Grafana MCP 客户端

```bash
# 列出所有可用工具
python simple_client.py list-tools

# 列出仪表板
python simple_client.py list-dashboards
python simple_client.py list-dashboards folder=ipc limit=50

# 获取面板信息
python simple_client.py get-panel 5

# 查询面板数据
python simple_client.py query-data 5

# 获取告警
python simple_client.py get-alerts

# 列出数据源
python simple_client.py list-ds

# 直接查询 Elasticsearch
python simple_client.py query-es wsnKPH4Nk query='metrics.platform: "sdc"'
```

---

### 交互式探索器

```bash
# 启动交互式探索器
python simple_client.py explore

# 带过滤条件的探索
python simple_client.py explore folder=ipc limit=100
```

**探索流程**:
1. 选择仪表板
2. 选择面板
3. 选择时间范围
4. 查看数据

---

### ES 直接查询工具

```bash
# 查询 SDC 平台数据（带聚合）
make es-query

# 查询最近 24 小时数据
make es-query-sdc

# 显示查询 DSL
make es-query-explain

# 输出原始 JSON
make es-query-json
```

---

### 告警检查工具

```bash
# 检查所有告警规则
make alert-check

# 检查单个规则
make alert-check-rule

# 显示规则详情
make alert-show-rule

# 检查磁盘告警
make alert-check-disk
```

---

### 邮件通知

```bash
# 测试邮件配置
make alert-email-test

# 检查告警并发送邮件
make alert-check-email

# 检查所有规则并发送邮件
make alert-check-all-email
```

---

## 配置说明

### Grafana 连接配置

在 `simple_client.py` 中配置：

```python
DEFAULT_CONFIG = {
    "grafana_url": "https://g.dev.tuputech.com",
    "api_key": os.getenv("GRAFANA_API_KEY", ""),  # 从环境变量读取
    "dashboard_uid": "urJcwIvHz",
}
```

**设置 API Key**:
```bash
export GRAFANA_API_KEY="your_api_key_here"
```

---

### Elasticsearch 配置

在 `monitoring/scripts/es_query.py` 中：

```python
ES_HOST = "172.26.2.88"
ES_PORT = 39202
ES_URL = f"http://{ES_HOST}:{ES_PORT}"
```

---

### 邮件配置

创建 `monitoring/config/email.yaml`:

```yaml
smtp:
  host: "smtp.gmail.com"
  port: 587
  use_tls: true

sender:
  email: "your@gmail.com"
  password: "your-app-password"  # Gmail 应用专用密码

recipients:
  to:
    - "ops@example.com"
    - "devops@example.com"
  cc:
    - "manager@example.com"
```

**或使用环境变量**:
```bash
export SMTP_HOST='smtp.gmail.com'
export SMTP_PORT='587'
export SENDER_EMAIL='your@gmail.com'
export SENDER_PASSWORD='your-app-password'
```

---

## 数据格式

### Grafana Frame 数据格式

```json
{
  "results": {
    "A": {
      "frames": [
        {
          "schema": {
            "name": "Device Metrics",
            "fields": [
              {"name": "Time", "type": "time"},
              {"name": "Value", "type": "number", "config": {"displayNameFromDS": "Device Count"}}
            ]
          },
          "data": {
            "values": [
              [1706227200000, 1706227260000, ...],  // 时间戳
              [10, 15, 20, ...]                        // 数值
            ]
          }
        }
      ]
    }
  }
}
```

---

### Elasticsearch 聚合结果格式

```json
{
  "aggregations": {
    "by_device": {
      "buckets": [
        {
          "key": "device123",
          "doc_count": 150,
          "max_value": {"value": 95.5},
          "latest_time": {"value": 1706227200000}
        }
      ]
    }
  }
}
```

---

## 常用 Makefile 命令

```bash
# 查看所有可用命令
make help

# 安装依赖
make install
make venv

# 运行 MCP 服务器
make run

# 运行测试客户端
make simple-client

# ES 查询
make es-query
make es-query-sdc
make es-query-explain

# 告警检查
make alert-check
make alert-check-rule
make alert-show-rule

# 邮件通知
make alert-email-test
make alert-check-email

# 交互式探索
make explore
make explore-ipc
make explore-all
```

---

## 环境要求

- Python 3.12+
- Elasticsearch 7.x/8.x
- Grafana 8.x+
- SMTP 服务器 (用于邮件通知)

---

## 项目结构

```
python/mcp/grafana/
├── server.py                      # MCP 服务器
├── simple_client.py               # 简单客户端 + 数据格式化
├── monitoring/
│   ├── PROGRESS.md                # 进度记录
│   ├── alert_rules/               # YAML 告警规则
│   │   └── sdc/
│   │       ├── cache_info_json.yaml
│   │       └── disk_used_ratio.yaml
│   ├── config/
│   │   └── email.yaml.example     # 邮件配置示例
│   └── scripts/
│       ├── es_query.py            # ES 直接查询工具
│       ├── alert_checker.py       # 告警检查器
│       └── email_notifier.py      # 邮件通知模块
├── Makefile                       # 命令快捷方式
└── requirements.txt               # Python 依赖
```

---

## 许可证

MIT License
