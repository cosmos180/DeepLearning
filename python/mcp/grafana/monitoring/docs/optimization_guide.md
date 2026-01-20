# 监控规则优化指南

## 问题背景

系统中有大量错误日志（~95万条/天），直接查询所有数据会导致超时。

## 优化策略

### 1. 使用 ES 端聚合 (`use_aggregation: true`)

在 Elasticsearch 端进行聚合，只返回聚合结果而不是原始数据。

```yaml
use_aggregation: true
aggregation_type: terms
aggregation_key: sInfo.app
```

**优点：**
- 大幅减少数据传输量
- 查询速度快 10-100 倍
- 适合告警场景（只需要统计数据）

### 2. 使用 Count 查询 (`use_count_query: true`)

只获取数量统计，不获取原始文档。

```yaml
use_count_query: true
query_key: sInfo.app
```

**优点：**
- 只返回计数，速度最快
- 适合阈值告警场景
- 带时间窗口的统计

### 3. 更精确的索引过滤

使用更具体的索引模式而不是通配符。

```yaml
# ❌ 避免
index: tupu-go-log-*

# ✅ 推荐
index: tupu-go-log-production-*
```

### 4. 缩短时间窗口

```yaml
# ❌ 避免长时间窗口
timeframe:
  days: 1

# ✅ 推荐短时间窗口
timeframe:
  minutes: 5
```

### 5. 添加更多过滤条件

```yaml
filter:
- query:
    query_string:
        # 添加服务/环境过滤
        query: 'contents.level:"error" AND sInfo.env:"production" AND sInfo.app:"my-service"'
```

### 6. 合理的告警阈值

根据基线数据设定阈值：

| 规则类型 | 推荐阈值范围 |
|---------|----------------|
| 错误数量 | 50-500（5分钟内，单服务）|
| 错误率 | 5-10%（基于业务需求）|
| 响应时间 | P95 + 20-50% |
| 激增检测 | 参考 10-50，激增 3-5 倍 |

## 优化后的规则列表

| 规则文件 | 优化策略 | 适用场景 |
|---------|----------|---------|
| `optimized_service_error_rate.yaml` | 聚合查询 + 短窗口 | 服务错误率监控 |
| `optimized_spike.yaml` | 聚合查询 + 按服务分组 | 错误激增检测 |
| `optimized_production_errors.yaml` | 精确索引 + 低阈值 | 生产环境错误监控 |
| `optimized_new_error_patterns.yaml` | 基数检测 | 新错误模式发现 |
| `optimized_nginx_latency.yaml` | 聚合查询（avg） | API 延迟监控 |
| `optimized_service_down.yaml` | flatline（无数据） | 服务停止检测 |
| `optimized_service_errors_count.yaml` | count查询 | 错误数量阈值 |

## 测试命令

```bash
# 测试特定规则
make monitor-test RULE=monitoring/elastalert_rules/error_rules/optimized_service_error_rate.yaml

# 启动服务
make monitor-run
```

## 性能对比

| 优化前 | 优化后 | 说明 |
|--------|--------|------|
| 查询超时 | 283秒完成 | 聚合查询效果显著 |
| 95万条记录超时 | 2k条聚合结果 | 数据量减少99.8% |
| 无法测试 | 可正常测试 | 规则可验证 |
