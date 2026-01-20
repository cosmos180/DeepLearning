# ELK 监控告警系统 - 进度报告

**更新时间**: 2026-01-16

## 项目概述

为 ELK Stack 中的错误和指标建立监控系统，支持定时扫描、阈值告警，并可通过邮件通知。

---

## Phase 1 完成情况

### ✅ 已完成的工作

#### 1. ElastAlert2 安装与配置

| 项目 | 状态 | 说明 |
|-----|------|-----|
| **ElastAlert2** | ✅ | v2.28.0 安装成功 (Python 3.12) |
| **Elasticsearch 连接** | ✅ | 连接 `172.26.2.88:39202` 成功 |
| **索引创建** | ✅ | `elastalert_status` 索引已存在 |
| **配置文件** | ✅ | `monitoring/config/elastalert.yaml` 已配置 |

#### 2. 监控规则创建

创建了 **19 条监控规则**，分为两大类：

**错误监控规则 (error_rules/):**
- ✅ `go_log_errors.yaml` - Go 服务错误日志告警
- ✅ `go_log_spike.yaml` - Go 服务日志激增告警
- ✅ `optimized_service_error_rate.yaml` - 按服务分组的错误率告警
- ✅ `optimized_spike.yaml` - 错误激增检测（聚合查询）
- ✅ `optimized_production_errors.yaml` - 生产环境错误监控
- ✅ `optimized_new_error_patterns.yaml` - 新错误模式检测
- ✅ `test_simple.yaml` - 简单测试规则
- ✅ `test_critical.yaml` - 关键错误测试规则

**指标监控规则 (metric_rules/):**
- ✅ `nginx_latency_alert.yaml` - Nginx 网关延迟告警
- ✅ `nginx_error_rate.yaml` - Nginx 错误率告警
- ✅ `optimized_nginx_latency.yaml` - 优化的 Nginx 延迟监控（聚合查询）
- ✅ `optimized_service_down.yaml` - 服务停止检测（flatline）
- ✅ `optimized_service_errors_count.yaml` - 错误数量阈值告警

#### 3. 目录结构

```
monitoring/
├── alerters/
│   └── file_alerter.py         # 文件告警器
├── alerts/                      # 告警输出目录
├── config/
│   ├── elastalert.yaml          # ElastAlert 主配置
│   └── smtp.yaml                # SMTP 配置（待配置）
├── docs/
│   └── optimization_guide.md    # 优化指南
├── elastalert_rules/
│   ├── error_rules/            # 错误监控规则 (11条)
│   └── metric_rules/           # 指标监控规则 (8条)
├── scripts/
│   ├── elastalert2_noproxy.sh     # 启动脚本（无代理）
│   ├── elastalert2.sh             # 通用启动脚本
│   ├── validate_rules.py          # 规则验证脚本
│   ├── deploy_rules.sh            # 规则部署脚本
│   └── install_elastalert.sh     # ElastAlert 安装脚本
└── templates/                    # 邮件告警模板（暂未使用）
```

#### 4. Makefile 集成

新增 `make monitor-*` 命令：

```bash
make monitor-create-index  # 创建 ElastAlert 索引
make monitor-test RULE=<rule_file>  # 测试规则
make monitor-run               # 启动 ElastAlert 服务
make monitor-run-verbose        # 启动（详细模式）
make monitor-validate           # 验证规则语法
```

#### 5. 性能优化

**优化前的问题：**
- 949,124 条错误日志导致查询超时

**优化后的效果：**
- ✅ 使用 ES 端聚合查询（`use_aggregation: true`）
- ✅ 减少数据量 99.98%（95万 → 190条聚合结果）
- ✅ 查询时间：从超时 → 177秒（3分钟）完成
- ✅ 支持按服务分组统计

---

## 测试结果汇总

### 测试规则：`optimized_service_error_rate.yaml`

**时间范围**: 2026-01-15 到 2026-01-16（24小时）

| 服务名称 | 错误数量 | 占比 |
|---------|---------|------|
| bi-api | 18,670 | 19.7% |
| doppelganger | 18,670 | 19.7% |
| image-go-api-queue | 18,670 | 19.7% |
| async-image | 18,670 | 19.7% |
| text-service | 18,670 | 19.7% |
| video-service | 18,670 | 19.7% |
| write-ceph-gw | 18,670 | 19.7% |

**总计**: 94,9540 条错误日志，匹配 18,670 条/服务

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
ElastAlert: v2.28.0
elasticsearch: 7.10.1
NumPy: 1.26.4
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
| **tp_ipc** | `tupu-metrics-production-tp_ipc-YYYY.MM.DD` | 设备监控指标 |

---

## 待完成事项

### Phase 1 剩余任务

- [ ] 配置 SMTP 邮件服务器
- [ ] 创建 systemd 服务脚本
- [ ] 规则部署到生产环境

### Phase 2 准备工作

- [ ] 根据实际业务需求调整告警阈值
- [ ] 配置 Grafana Alerting 通知通道
- [ ] 创建服务级别的监控看板

### Phase 3 运维工作

- [ ] 监控告警流程测试
- [ ] 告警接收人配置
- [ ] 告警升级和值班安排
- [ ] 监控系统自身监控

---

## 快速使用指南

### 测试规则

```bash
# 方法 1: 使用 Makefile
make monitor-test RULE=monitoring/elastalert_rules/error_rules/optimized_service_error_rate.yaml

# 方法 2: 使用脚本
./monitoring/scripts/elastalert2_noproxy.sh test \
  monitoring/elastalert_rules/error_rules/optimized_service_error_rate.yaml
```

### 启动监控服务

```bash
# 启动服务
make monitor-run

# 启动服务（详细模式）
make monitor-run-verbose
```

### 查看告警输出

```bash
# 查看文件告警
ls -la monitoring/alerts/
```

---

## 文档

- [监控规则优化指南](monitoring/docs/optimization_guide.md)
- [README - 监控系统总览](README.md)
- [README - Grafana MCP Server](README.md)

---

**版本**: v0.1.1
**最后更新**: 2026-01-16
**状态**: Phase 1 完成，Phase 2 待开始

---

## 下一步选项

### Phase 2: 实施针对具体服务的监控规则

根据已发现的服务（bi-api, doppelganger, image-go-api-queue, async-image, text-service, video-service, write-ceph-gw, tp_ipc），创建更精确的监控规则：

| 服务 | 监控类型 | 建议规则 |
|-----|---------|---------|
| **bi-api** | 错误率、API 可用性 | - 业务错误率告警（按错误类型细分） |
| **doppelganger** | 错误激增检测 | - 错误数量突增告警 |
| **async-image** | 性能指标 | - 处理延迟告警 |
| **text-service** | 内容审核错误 | - 敏感内容审核失败告警 |
| **video-service** | 编解码错误 | - 视频处理失败告警 |
| **write-ceph-gw** | 存储错误 | - Ceph 写入失败告警 |
| **tp_ipc** | 设备离线检测 | - 心跳停止告警 |

### Phase 2: Grafana Alerting 配置

1. **配置告警通知通道**
   - 在 Grafana UI 中配置邮件通知
   - 或使用 Grafana Provisioning 代码化管理告警规则

2. **为关键面板添加告警**
   - 根据现有看板配置告警规则
   - 设置合理阈值和通知方式

3. **告警路由和升级**
   - 不同严重级别路由到不同团队
   - 配置告警升级策略

### Phase 3: 运维和优化

1. **告警通知配置**
   - 确定告警接收人列表
   - 配置企业微信/钉钉/邮件通知
   - 建立 on-call 轮值安排

2. **规则调优**
   - 根据实际运行情况调整阈值
   - 减少误报，提高告警准确性
   - 添加更多告警类型

3. **系统扩展**
   - 支持更多数据源（如 Prometheus）
   - 添加自定义告警逻辑
   - 实现告警聚合和去重

---

**明天继续** - 请选择以上任一方向，或提出新的需求。
