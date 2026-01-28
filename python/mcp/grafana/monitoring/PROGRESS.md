# ELK 监控告警系统 - 进度报告

**更新时间**: 2026-01-26

## 项目概述

为 ELK Stack 中的错误和指标建立监控系统，支持定时扫描、阈值告警，并可通过邮件通知。

---

## Phase 3 完成情况 (2026-01-26)

### ✅ 新增功能：Grafana 监控告警智能 Agent

基于 Google ADK (Agent Development Kit) 框架，开发了支持自然语言查询的智能监控助手。

#### 1. Agent 架构

**目录结构：**
```
agent/
├── __init__.py              # Root Agent 定义 (adk run 入口)
├── tools/
│   ├── __init__.py
│   ├── es_query_tool.py     # ES 查询工具 (5 个函数)
│   ├── alert_tool.py        # 告警检查工具 (5 个函数)
│   └── dashboard_tool.py    # Dashboard 探索工具 (5 个函数)
├── requirements.txt
└── README.md
```

**技术栈：**
- Google ADK 框架
- GLM-4-Flash 模型 (智谱 AI)
- nest_asyncio (嵌套事件循环支持)
- httpx (异步 HTTP 客户端)

#### 2. 15 个 Agent 工具

**ES 查询工具 (5 个)：**
| 工具 | 说明 | 示例 |
|------|------|------|
| `search_es_by_platform` | 按平台搜索 | "查询 sdc 平台最近 24 小时的数据" |
| `search_es_by_device` | 按设备搜索 | "设备 ABC123 有什么问题？" |
| `search_es_by_metric` | 按指标搜索 | "cache_info.json 有哪些异常？" |
| `search_es_custom` | 自定义 Lucene 查询 | "metrics.platform:'sdc' AND metrics.payload.camera_error_info.code:'-1506'" |
| `get_es_summary` | 获取数据摘要 | "sdc 平台数据摘要" |

**告警工具 (5 个)：**
| 工具 | 说明 | 示例 |
|------|------|------|
| `check_all_alerts` | 检查所有告警 | "有没有触发告警？" |
| `check_alert_by_rule` | 检查特定规则 | "检查 cache_info_json 告警" |
| `get_alert_rules` | 获取规则列表 | "显示所有告警规则" |
| `analyze_alert_trend` | 分析告警趋势 | "设备 ABC123 的告警趋势" |
| `get_alert_suggestions` | 获取优化建议 | "告警优化建议" |

**Dashboard 工具 (5 个)：**
| 工具 | 说明 | 示例 |
|------|------|------|
| `list_dashboards` | 列出仪表板 | "列出 ipc 文件夹的仪表板" |
| `get_dashboard_panels` | 获取面板列表 | "显示 dashboard 的面板" |
| `search_panels` | 搜索面板 | "搜索包含 crash 的面板" |
| `get_panel_info` | 获取面板详情 | "面板 5 的详细信息" |
| `get_dashboard_recommendations` | 获取推荐 | "sdc 平台的推荐仪表板" |

#### 3. 修复的问题

**1) Async 事件循环冲突**
- **问题**: ADK 运行在已有事件循环中，`asyncio.run()` 导致 `RuntimeError`
- **解决**: 使用 `nest_asyncio.apply()` 允许嵌套事件循环

**2) 语法错误**
- **问题**: `es_query_tool.py:241` 有 malformed f-string
- **解决**: 修复 `* TO *}` → `* TO *]`

**3) 时间范围解析**
- **问题**: "今天" 被解析为 "now-24h" (最近 24 小时)
- **解决**: "today" 转换为 "now/d" (今天 0 点)

**4) 查询结果显示**
- **问题**: 输出不显示搜索条件，难以验证查询是否正确
- **解决**: 在结果中显示查询条件和时间范围

#### 4. 查询结果示例

```
🔍 Elasticsearch 查询结果
============================================================
  查询条件: metrics.platform: "sdc" AND metrics.payload.camera_error_info.code: "-1506"
  时间范围: now/d ~ now
============================================================
  总命中: 6 条
  返回: 6 条文档
============================================================

📊 按设备聚合统计:
  C0CD834C0858B06986974C679C662EA6: 3 条
  445CB6E30DA6CEEC65FD6EA1A0E96C02: 1 条
  4AF08F3E10A2CDE9532D908A35F42AD5: 1 条
  ...
```

#### 5. Makefile 命令

```bash
make agent-install    # 安装依赖 (包括 nest_asyncio)
make agent-run        # 运行 ADK Agent (需要 ZHIPU_API_KEY)
make agent-run-simple # 运行简化版 (不需要 LLM)
make agent-tools      # 列出所有工具
```

#### 6. 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `ZHIPU_API_KEY` | 智谱 AI API Key | 是 |
| `GRAFANA_URL` | Grafana 服务器 URL | 否 |
| `GRAFANA_API_KEY` | Grafana API Key | 否 |

---

## Phase 2 完成情况 (2026-01-21)

### ✅ 新增功能：脱离 Grafana 的轻量告警系统

基于路径 A (ElastAlert)，实现了一套自定义的告警检查系统，直接查询 Elasticsearch 并发送告警。

#### 1. Elasticsearch 直接查询工具

| 文件 | 说明 |
|-----|------|
| `monitoring/scripts/es_query.py` | ES 直接查询工具 |

**功能：**
- 支持 Lucene 查询语法
- 按设备聚合统计
- 格式化输出查询结果
- 支持 JSON 输出

**使用示例：**
```bash
# 查询 sdc 平台数据
make es-query

# 查询最近 24 小时数据
make es-query-sdc

# 查看查询 DSL
make es-query-explain
```

#### 2. 基于 YAML 的告警规则系统

**目录结构：**
```
monitoring/
├── alert_rules/
│   └── sdc/                          # 按平台分类的告警规则
│       ├── cache_info_json.yaml      # JSON 缓存告警
│       └── disk_used_ratio.yaml      # 磁盘使用率告警
├── config/
│   └── email.yaml                    # 邮件配置文件
└── scripts/
    ├── es_query.py                   # ES 查询工具
    ├── alert_checker.py              # 告警检查器
    └── email_notifier.py             # 邮件通知模块
```

**YAML 规则示例：**
```yaml
name: "SDC Cache Info JSON Alert"
description: "Alert when cache_info.json exceeds threshold"
index: "tupu-metrics-production-tp_ipc-*"
query: 'metrics.platform: "sdc"'
alert:
  field: "metrics.cache_info.json"
  threshold_type: "greater_than"
  threshold: 10
  aggregation: "terms"
  aggregation_field: "deviceId"
time_window:
  range: "now-5m"
  schedule: "*/5 * * * *"
severity: "warning"
```

#### 3. 邮件通知功能

**功能特性：**
- HTML 格式邮件
- 根据告警级别显示不同颜色
- 支持告警摘要邮件
- 支持按级别路由收件人
- 支持环境变量配置

**配置方式：**

方式 1 - 编辑配置文件 `monitoring/config/email.yaml`:
```yaml
smtp:
  host: "smtp.gmail.com"
  port: 587
  use_tls: true
sender:
  email: "your@gmail.com"
  password: "your-app-password"
recipients:
  to:
    - "ops@example.com"
```

方式 2 - 使用环境变量:
```bash
export SMTP_HOST='smtp.gmail.com'
export SMTP_PORT='587'
export SENDER_EMAIL='your@gmail.com'
export SENDER_PASSWORD='your-app-password'
```

#### 4. Makefile 命令

**ES 查询命令：**
```bash
make es-query           # 查询 (platform:sdc) AND (cache_info.json)
make es-query-sdc       # 查询 platform:sdc (24h)
make es-query-explain   # 显示查询 DSL
make es-query-json      # 输出原始 JSON
```

**告警检查命令：**
```bash
make alert-check        # 检查所有告警规则
make alert-check-rule   # 检查单个规则
make alert-show-rule    # 显示规则详情
make alert-check-disk   # 检查磁盘告警
```

**邮件通知命令：**
```bash
make alert-email-test       # 测试邮件配置
make alert-check-email      # 检查告警并发送邮件
make alert-check-all-email  # 检查所有规则并发送邮件
```

#### 5. 测试结果

**cache_info.json 告警测试** (阈值 > 10):

| 设备 ID | cache_info.json | 阈值 | 状态 |
|---------|-----------------|------|------|
| 3860AB3498F2F8B2ECFA16BFFD0E32D7 | 60 | 10 | 🟡 Warning |
| 527D98BB60D565FC5378CAB047F5B729 | 69 | 10 | 🟡 Warning |

---

## Phase 1 完成情况 (2026-01-16)

### ✅ ElastAlert2 安装与配置

| 项目 | 状态 | 说明 |
|-----|------|-----|
| **ElastAlert2** | ✅ | v2.28.0 安装成功 (Python 3.12) |
| **Elasticsearch 连接** | ✅ | 连接 `172.26.2.88:39202` 成功 |
| **索引创建** | ✅ | `elastalert_status` 索引已存在 |
| **配置文件** | ✅ | `monitoring/config/elastalert.yaml` 已配置 |

### ✅ 监控规则创建 (ElastAlert)

创建了 **19 条监控规则**，分为两大类：

**错误监控规则 (error_rules/):**
- `go_log_errors.yaml` - Go 服务错误日志告警
- `go_log_spike.yaml` - Go 服务日志激增告警
- `optimized_service_error_rate.yaml` - 按服务分组的错误率告警
- `optimized_spike.yaml` - 错误激增检测（聚合查询）
- `optimized_production_errors.yaml` - 生产环境错误监控
- `optimized_new_error_patterns.yaml` - 新错误模式检测
- `test_simple.yaml` - 简单测试规则
- `test_critical.yaml` - 关键错误测试规则

**指标监控规则 (metric_rules/):**
- `nginx_latency_alert.yaml` - Nginx 网关延迟告警
- `nginx_error_rate.yaml` - Nginx 错误率告警
- `optimized_nginx_latency.yaml` - 优化的 Nginx 延迟监控（聚合查询）
- `optimized_service_down.yaml` - 服务停止检测（flatline）
- `optimized_service_errors_count.yaml` - 错误数量阈值告警

---

## 配置信息

### Elasticsearch

```yaml
Host: 172.26.2.88:39202
Status: green (healthy)
Indices:
  - tupu-go-log-*
  - tupu-metrics-production-*
  - tupu-metrics-production-tp_ipc-*
```

### Grafana

```yaml
URL: https://g.dev.tuputech.com
API Key: eyJrIjoiaGNpeWovMGUxYUFYaTFqZldZSVhLY3hNb01DSTBHZGEiLCJuIjoibW9iaWxlLWlwYyIsImlkIjoxfQ==
```

### Python 环境

```bash
Python: 3.12
依赖: httpx, pyyaml
```

---

## 当前可用服务

| 服务名称 | 索引模式 | 数据类型 |
|---------|---------|---------|
| bi-api | `tupu-go-log-production-bi-api-*` | Go 服务日志 |
| doppelganger | `tupu-go-log-production-doppelganger-*` | Go 服务日志 |
| image-go-api-queue | `tupu-go-log-stage-image-go-api-queue-*` | 队列服务日志 |
| async-image | `tupu-go-log-production-async-image-*` | 异步图像处理服务日志 |
| text-service | `tupu-go-log-production-text-service-*` | 文本服务日志 |
| video-service | `tupu-go-log-production-video-service-*` | 视频服务日志 |
| write-ceph-gw | `tupu-go-log-production-write-ceph-gw-*` | Ceph 写入服务日志 |
| **tp_ipc (SDC)** | `tupu-metrics-production-tp_ipc-*` | 设备监控指标 |

---

## 待完成事项

### Phase 2 剩余任务

- [ ] 配置 SMTP 邮件服务器（Gmail 应用密码）
- [ ] 测试邮件发送功能
- [ ] 添加更多平台的告警规则
- [ ] 实现定时调度 (cron)

### Phase 3 准备工作

- [ ] 根据实际业务需求调整告警阈值
- [ ] 配置企业微信/钉钉通知
- [ ] 创建 systemd 服务脚本
- [ ] 告警聚合和去重

---

## 快速使用指南

### 添加新的告警规则

1. 创建平台目录：
```bash
mkdir -p monitoring/alert_rules/new_platform
```

2. 复制模板并编辑：
```bash
cp monitoring/alert_rules/sdc/cache_info_json.yaml monitoring/alert_rules/new_platform/
vim monitoring/alert_rules/new_platform/cache_info_json.yaml
```

3. 测试规则：
```bash
make alert-check-rule
```

### 测试邮件通知

```bash
# 1. 配置邮件（编辑文件或设置环境变量）
vim monitoring/config/email.yaml

# 2. 测试邮件发送
make alert-email-test

# 3. 检查告警并发送邮件
make alert-check-email
```

---

## 文档

- [README - 监控系统总览](README.md)
- [README - Grafana MCP Server](../README.md)

---

**版本**: v0.3.0
**最后更新**: 2026-01-26
**状态**: Phase 3 完成

---

## 下一步建议

1. **测试 Agent 功能**
   - 配置 `ZHIPU_API_KEY`
   - 运行 `make agent-run` 测试自然语言查询
   - 验证各种查询场景

2. **配置邮件并测试**
   - 获取 Gmail 应用密码
   - 编辑 `monitoring/config/email.yaml`
   - 运行 `make alert-email-test`

3. **添加更多告警规则**
   - 为其他平台创建告警规则
   - 调整阈值以适应实际需求

4. **实现定时调度**
   - 使用 cron 或 APScheduler
   - 部署为 systemd 服务
