# Grafana 告警邮件发送工具

Grafana 监控面板批量截图和邮件发送工具，支持按 platform 变量自动分发告警报告。

## 核心功能

**唯一操作**: 批量发送 platform 告警邮件

- ✅ **自动获取 Dashboard 面板** - 无需手动配置 panel ID
- ✅ **按 platform 变量分发** - 为每个 platform 生成独立的告警邮件
- ✅ **智能图片压缩** - 自动压缩图片（10-50%），减小邮件大小
- ✅ **精美 HTML 邮件模板** - 专业的 HTML 邮件，内嵌截图

---

## 快速开始

### 1. 安装依赖

```bash
make install
```

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# Grafana 配置
GRAFANA_URL=https://g.dev.tuputech.com
GRAFANA_API_KEY=your-grafana-api-key

# 邮件配置（腾讯企业邮）
SENDER_EMAIL=your-email@example.com
SENDER_PASSWORD=your-password
SENDER_NAME=[Grafana-Alert-System]

# 默认收件人
RECIPIENTS_TO=jinxinhou@tuputech.com
```

### 3. 发送告警邮件

```bash
# 独立工具（推荐）
python3 grafana_alert_tool.py

# 或使用 Makefile
make send
```

---

## 使用方式

### 方式 1: 独立工具（推荐，快速）

```bash
# 查看帮助
python3 grafana_alert_tool.py --help

# 发送所有平台（今天）
python3 grafana_alert_tool.py

# 发送指定平台
python3 grafana_alert_tool.py --platforms sdc,tpboxv3

# 自定义时间范围
python3 grafana_alert_tool.py --time-range 24h

# 指定收件人
python3 grafana_alert_tool.py --recipients user@example.com
```

### 方式 2: Makefile

```bash
# 查看帮助
make help

# 发送所有平台
make send

# 发送今天的数据
make send-today

# 发送最近24小时的数据
make send-24h

# 发送指定平台
make send PLATFORMS=sdc,tpboxv3

# 自定义参数
make send TIME_RANGE=7d RECIPIENTS=user@example.com
```

### 方式 3: ADK Agent（对话式）

```bash
# 启动对话式 Agent（使用 Makefile）
make agent-run

# 或直接使用 ADK 命令
cd .. && adk run grafana

# 示例对话
> 发送所有平台的告警邮件
> 发送 sdc 和 tpboxv3 平台的告警邮件
> 发送最近24小时的告警邮件，收件人是 user@example.com
> exit
```

**注意**: 使用 ADK Agent 需要先设置 `ZHIPU_API_KEY` 环境变量。

---

## 支持的 Platform

| Platform | 说明 |
|----------|------|
| sdc | SDC 平台 |
| tpboxv3 | TPBox V3 |
| tpboxv2 | TPBox V2 |
| android_armv7 | Android ARMv7 |
| 1800A | 1800A 设备 |
| rv1109 | RV1109 |
| tpboxv1 | TPBox V1 |

---

## 邮件内容

每封邮件包含：

- 📊 **17 个监控面板**的截图
- 📅 **时间范围**: 今天 00:00:00 ~ 现在
- 🏷️ **Platform 变量**: 对应平台的筛选数据

### 监控面板列表

| Panel ID | 面板名称 | 说明 |
|----------|----------|------|
| 29 | 设备在线 | 设备在线状态 |
| 31 | 崩溃率 | 系统崩溃率 |
| 27 | 【crash 设备列表】 | 崩溃设备明细 |
| 19 | 【ffmpeg 拉流异常】 | 视频流异常 |
| 8 | 数据积压【track上传队列】 | Track 队列积压 |
| 6 | 数据积压【jpeg】 | JPEG 缓存积压 |
| 13 | 数据上传失败【uploadTrack】 | Track 上传失败 |
| 10 | 数据积压【track DB 文件】 | Track DB 积压 |
| 9 | 数据积压【imageRecord DB 文件】 | ImageRecord DB 积压 |
| 25 | 【序列化 frame encode】 | 帧编码问题 |
| 23 | 【磁盘使用率】 | 磁盘使用情况 |
| 17 | 【空 token】 | Token 异常 |
| 21 | 【摄像头离线】 | 摄像头离线 |
| 5 | 数据积压【json】 | JSON 缓存积压 |
| 15 | 【deadlock】 | 死锁监控 |
| 11 | 模型调用失败【reid】 | Reid 模型失败 |
| 12 | 模型调用失败【attr】 | Attr 模型失败 |

---

## 配置说明

### Dashboard 配置

默认监控的 Dashboard：
- **UID**: `urJcwIvHz`
- **名称**: 业务异常监控
- **变量**: `platform` (支持多值筛选)

### 邮件服务器

默认使用腾讯企业邮：
- **SMTP**: `smtp.exmail.qq.com:465`
- **SSL**: 是

如需更换邮件服务器，修改 `monitoring/config/email.yaml`。

### 图片压缩

默认压缩配置：
- **分辨率**: 800x400
- **JPEG 质量**: 70
- **压缩率**: 10-50%

---

## 收件人管理

```bash
# 查看收件人列表
make list-recipients

# 添加收件人
make add-recipient EMAIL=user@example.com

# 移除收件人
make remove-recipient EMAIL=user@example.com
```

---

## 故障排查

### 邮件发送失败：bad syntax

**原因**: `.env` 文件配置不正确或未加载

**解决**:
1. 确认 `.env` 文件存在
2. 检查 `SENDER_EMAIL` 和 `SENDER_PASSWORD` 正确
3. 确保安装了 `python-dotenv` (`make install`)

### 截图下载失败

**原因**: Grafana API Key 无效或网络问题

**解决**:
1. 检查 `GRAFANA_API_KEY` 是否有效
2. 确认网络可访问 Grafana 服务器

### 邮件被拒收

**原因**: 邮件大小超限或频率限制

**解决**:
1. 已启用图片压缩，每封邮件约 200-400KB
2. 如需调整压缩率，修改 `AlertReportConfig` 中的 `image_width` 和 `image_height`

---

## 项目结构

```
grafana/
├── grafana_alert_tool.py   # 核心工具（一键发送）
├── agent.py                # ADK Agent（对话式）
├── Makefile                 # 快捷命令
├── requirements.txt         # Python 依赖
├── .env                    # 环境变量配置
├── README.md               # 项目文档
├── .adk/                   # ADK 配置目录
│   └── config.yaml
├── tools/
│   ├── alert_email_reporter.py  # 底层实现
│   └── __init__.py
└── monitoring/
    └── config/
        ├── email.yaml      # 邮件服务器配置
        └── recipients.json # 收件人列表
```

---

## 依赖项

```
google-adk>=0.1.0
httpx>=0.27.0
pyyaml>=6.0.1
Pillow>=10.0.0
python-dotenv>=1.0.0
```

---

## 许可证

MIT License
