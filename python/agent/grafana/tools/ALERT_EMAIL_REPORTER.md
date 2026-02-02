# Alert Email Reporter Tool

告警邮件报告工具 - 为每个 platform 生成告警 panel 截图并发送邮件。

## 功能

- 为指定的 platform 下载 Grafana Panel 截图
- 将截图嵌入到精美的 HTML 邮件中
- 支持批量发送多个平台的告警报告
- 支持自定义时间范围、收件人等配置

## 快速开始

### 1. 作为模块使用

```python
import os
from tools.alert_email_reporter import send_alert_report_email

# 配置环境变量
os.environ['SENDER_EMAIL'] = 'your@email.com'
os.environ['SENDER_PASSWORD'] = 'your_password'
os.environ['RECIPIENTS_TO'] = 'recipient@email.com'

# 发送所有平台的告警报告
send_alert_report_email()

# 发送指定平台的告警报告
send_alert_report_email(platforms='sdc,tpboxv3')

# 自定义时间范围和收件人
send_alert_report_email(
    platforms='sdc',
    time_range='6h',
    recipient_email='user@example.com'
)
```

### 2. 命令行使用

```bash
# 发送所有平台的告警报告
python3 tools/alert_email_reporter.py

# 发送指定平台的告警报告
python3 tools/alert_email_reporter.py --platforms sdc,tpboxv3

# 自定义时间范围和收件人
python3 tools/alert_email_reporter.py --time-range 6h --recipient user@example.com
```

### 3. 使用 AlertEmailReporter 类

```python
from tools.alert_email_reporter import (
    AlertEmailReporter,
    GrafanaConfig,
    EmailConfig,
    AlertReportConfig,
)

# 创建配置
grafana_config = GrafanaConfig(
    url="https://your-grafana.com",
    api_key="your_api_key",
    dashboard_uid="your_dashboard_uid",
)

email_config = EmailConfig(
    sender_email="your@email.com",
    sender_password="your_password",
    recipient_email="recipient@email.com",
)

report_config = AlertReportConfig(
    time_range="24h",
    platforms=["sdc", "tpboxv3"],
    image_width=1200,
    image_height=600,
)

# 创建报告器
reporter = AlertEmailReporter(
    grafana_config=grafana_config,
    email_config=email_config,
    report_config=report_config,
)

# 发送报告
import asyncio
asyncio.run(reporter.send_all_platforms())
```

## 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `GRAFANA_URL` | Grafana 服务器地址 | `https://g.dev.tuputech.com` |
| `GRAFANA_API_KEY` | Grafana API 密钥 | `eyJrIjoi...` |
| `SENDER_EMAIL` | 发件人邮箱 | `alert@example.com` |
| `SENDER_PASSWORD` | 发件人邮箱密码 | `your_password` |
| `RECIPIENTS_TO` | 默认收件人邮箱 | `user@example.com` |

## 参数说明

### send_alert_report_email()

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `platforms` | str | 所有平台 | 平台列表，逗号分隔 |
| `time_range` | str | `"24h"` | 时间范围（如 `"6h"`, `"24h"`, `"7d"`） |
| `recipient_email` | str | 环境变量 | 收件人邮箱 |

## 邮件内容

每封邮件包含以下 Panel 的截图：

1. 📊 数据积压【json】
2. 📊 数据积压【jpeg】
3. 📊 模型调用失败【reid】
4. 📊 模型调用失败【attr】
5. 📊 数据上传失败【uploadTrack】
6. 📊 磁盘使用率
7. 📊 摄像头离线

## 自定义告警规则

如需添加或修改告警规则对应的 Panel，修改 `DEFAULT_ALERT_PANELS`：

```python
DEFAULT_ALERT_PANELS = {
    "你的告警规则名称": {
        "panel_id": 123,  # Panel ID
        "title": "Panel 标题"
    },
}
```

## 注意事项

1. 需要 Grafana Image Renderer 插件已安装并可用
2. 如果截图不可用，邮件会提供直接访问链接
3. 邮件使用 base64 编码嵌入图片，不需要附件
4. 截图时间范围会应用到所有 Panel
