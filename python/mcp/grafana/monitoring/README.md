# ELK 监控告警系统

本系统基于 ElastAlert + Grafana Alerting 混合架构，为 ELK Stack 中的错误和指标提供监控告警功能。

## 目录结构

```
monitoring/
├── elastalert_rules/         # ElastAlert 规则文件
│   ├── error_rules/          # 错误类监控规则
│   │   ├── example_error_spike.yaml
│   │   ├── example_critical_error.yaml
│   │   └── example_high_error_rate.yaml
│   └── metric_rules/         # 指标类监控规则
│       ├── example_metric_threshold.yaml
│       ├── example_api_latency.yaml
│       └── example_business_metric.yaml
├── templates/                # 邮件告警模板
│   ├── email_error.html.j2   # 错误告警邮件模板
│   └── email_metric.html.j2  # 指标告警邮件模板
├── config/                   # 配置文件
│   ├── elastalert.yaml       # ElastAlert 主配置
│   └── smtp.yaml             # SMTP 邮件认证配置
├── scripts/                  # 管理脚本
│   ├── install_elastalert.sh # ElastAlert 安装脚本
│   ├── validate_rules.py     # 规则验证脚本
│   └── deploy_rules.sh       # 规则部署脚本
└── README.md                 # 本文档
```

## 快速开始

### 1. 安装 ElastAlert

```bash
# 运行安装脚本
sudo ./monitoring/scripts/install_elastalert.sh
```

或手动安装：

```bash
# 克隆 ElastAlert 仓库
git clone https://github.com/Yelp/elastalert.git /opt/elastalert

# 安装依赖
cd /opt/elastalert
pip3 install -e .
pip3 install elasticsearch>=7.0.0 jinja2 pyyaml
```

### 2. 配置 Elasticsearch 连接

编辑 `config/elastalert.yaml`：

```yaml
es_host: localhost
es_port: 9200
# es_username: elastic
# es_password: changeme
```

### 3. 配置 SMTP 邮件服务器

编辑 `config/smtp.yaml`：

```yaml
user: your-email@example.com
password: your-app-password
```

同时在 `config/elastalert.yaml` 中配置 SMTP 服务器：

```yaml
smtp_host: smtp.gmail.com
smtp_port: 587
smtp_ssl: true
```

**常用 SMTP 配置：**

| 邮箱服务商 | smtp_host | smtp_port |
|-----------|-----------|-----------|
| Gmail | smtp.gmail.com | 587 |
| QQ 邮箱 | smtp.qq.com | 587 |
| 163 邮箱 | smtp.163.com | 465 |
| 腾讯企业邮 | smtp.exmail.qq.com | 465 |

### 4. 验证规则

```bash
# 验证所有规则
python3 ./monitoring/scripts/validate_rules.py --rules-dir ./monitoring/elastalert_rules

# 验证单个规则
python3 ./monitoring/scripts/validate_rules.py --file ./monitoring/elastalert_rules/error_rules/example_error_spike.yaml
```

### 5. 测试规则

```bash
# 进入 ElastAlert 目录
cd /opt/elastalert

# 测试单个规则（调试模式）
elastalert --verbose \
    --config /opt/elastalert/config.yaml \
    --rule /path/to/rule.yaml \
    --start 2024-01-01T00:00:00Z \
    --end 2024-01-02T00:00:00Z
```

### 6. 部署规则

```bash
# 部署规则到生产环境
sudo ./monitoring/scripts/deploy_rules.sh
```

### 7. 启动 ElastAlert 服务

```bash
# 启用并启动服务
sudo systemctl enable elastalert
sudo systemctl start elastalert

# 查看服务状态
sudo systemctl status elastalert

# 查看日志
sudo journalctl -u elastalert -f
```

## 规则类型说明

### 错误类规则 (error_rules)

| 规则文件 | 规则类型 | 描述 |
|---------|---------|------|
| example_error_spike.yaml | spike | 检测错误数量激增 |
| example_critical_error.yaml | frequency | 检测严重错误模式 |
| example_high_error_rate.yaml | frequency | 检测高错误率 |

### 指标类规则 (metric_rules)

| 规则文件 | 规则类型 | 描述 |
|---------|---------|------|
| example_metric_threshold.yaml | frequency | 指标阈值告警 |
| example_api_latency.yaml | frequency | API 延迟告警 |
| example_business_metric.yaml | frequency | 业务指标告警 |

## 规则编写指南

### 规则文件模板

```yaml
# 规则名称
name: My Alert Rule

# 规则类型
type: frequency

# Elasticsearch 索引
index: logs-*

# 触发阈值
num_events: 10

# 时间窗口
timeframe:
  minutes: 5

# 查询条件
filter:
- query:
    query_string:
        query: 'level:ERROR'

# 告警方式
alert:
  - email

# 邮件接收者
email:
  - "ops@example.com"

# 邮件主题
alert_subject: "Alert: {0}"

# 重复告警间隔
realert:
  minutes: 30
```

### 支持的规则类型

- **any**: 只要匹配就告警
- **frequency**: 事件数量达到阈值
- **spike**: 检测激增/下降
- **flatline**: 检测事件数量低于阈值
- **blacklist/whitelist**: 黑/白名单
- **change**: 检测字段值变化
- **cardinality**: 检测唯一值数量

更多规则类型请参考：[ElastAlert 规则类型](https://elastalert.readthedocs.io/en/latest/ruletypes.html)

## Grafana Alerting 配置

### 1. 配置告警通知通道

在 Grafana 中：
1. 导航到 Configuration → Alerting → Notification channels
2. 添加新的通知通道，选择 Email
3. 配置 SMTP 服务器信息
4. 测试并保存

### 2. 为面板添加告警

1. 编辑面板
2. 点击 Alert 标签页
3. 设置告警条件
4. 配置通知通道

### 3. 使用 Grafana Provisioning (推荐)

在 `grafana/provisioning/alerting/` 目录下创建配置文件：

```yaml
apiVersion: 1

contactPoints:
  - name: email_alerts
    orgId: 1
    receivers:
      - uid: email_receiver
        type: email
        settings:
          addresses: ops@example.com

policies:
  - orgId: 1
    receiver: email_alerts
    group_by: ['alertname', 'cluster']
    match:
      severity: critical
```

## 维护和操作

### 添加新规则

1. 在 `elastalert_rules/error_rules/` 或 `elastalert_rules/metric_rules/` 下创建新的 YAML 文件
2. 使用 `validate_rules.py` 验证规则语法
3. 运行 `deploy_rules.sh` 部署规则

### 删除规则

1. 删除对应的规则文件
2. 运行 `deploy_rules.sh` 同步变更

### 修改规则

1. 编辑规则文件
2. 使用 `validate_rules.py` 验证
3. 运行 `deploy_rules.sh` 部署

### 查看告警历史

```bash
# ElastAlert 告警存储在 elastalert_status 索引中
curl -XGET 'localhost:9200/elastalert_status/_search?pretty'
```

## 故障排查

### ElastAlert 无法启动

1. 检查配置文件语法：
```bash
python3 -m yaml /opt/elastalert/config.yaml
```

2. 检查 Elasticsearch 连接：
```bash
curl http://localhost:9200
```

3. 查看详细日志：
```bash
journalctl -u elastalert -n 100
```

### 邮件告警不发送

1. 确认 SMTP 配置正确
2. 使用 `debug` 告警类型测试：
```yaml
alert:
  - debug
```
3. 检查防火墙是否阻止 SMTP 端口

### 规则不触发

1. 使用 ElastAlert 测试模式
2. 检查 Elasticsearch 查询是否返回数据
3. 调整阈值或时间窗口

## 参考资源

- [ElastAlert 官方文档](https://elastalert.readthedocs.io/)
- [Grafana 告警文档](https://grafana.com/docs/grafana/latest/alerting/)
- [Elasticsearch 查询 DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
