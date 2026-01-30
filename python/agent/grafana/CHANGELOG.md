# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added - 2026-01-30

#### Grafana Agent (`agent/grafana/`)

**New Tools - ES 查询增强:**
- `search_es_aggregation` - Elasticsearch 聚合统计查询
  - 解决查询结果不全问题（不受 size 限制）
  - 固定格式的表格输出（包含数量和占比）
  - 支持统计字段的所有唯一值
  - 参数: `lucene_query`, `agg_field`, `time_range`, `agg_size`
  - 示例: 统计今天所有错误类型及其数量

**New Tools - Panel 操作:**
- `get_panel_query_results` - 执行 Panel 查询并返回实际数据
  - 解析 Panel 配置中的查询目标
  - 支持 Elasticsearch 数据源
  - 返回格式化的查询结果

- `get_panel_render_url` - 生成 Panel 直接访问链接
  - 无需 Image Renderer 插件
  - 返回可点击的 Grafana URL
  - 支持自定义时间范围

- `download_panel_render` - 下载 Panel 渲染图片
  - 智能回退机制：render 不可用时自动返回直接链接
  - 支持自定义图片尺寸
  - 图片默认保存到 `./panel_renders/` 目录

- `send_panel_to_email` - 发送 Panel 到邮件
  - 智能回退机制：render 不可用时发送带链接的邮件
  - render 可用时发送内嵌图片的 HTML 邮件
  - render 不可用时发送带按钮链接的 HTML 邮件
  - 支持自定义收件人

**Enhanced:**
- `format_aggregation_results()` - 新增聚合结果格式化函数
  - 固定格式的表格输出（使用 box-drawing 字符）
  - 显示字段值、数量、占比
  - 最多显示 50 个唯一值

- `Agent Instructions` 更新:
  - 新增聚合查询使用指南
  - 新增 Panel 操作工具说明
  - 新增智能回退机制说明

**Email Configuration:**
- 新增邮件配置支持
- 配置文件: `monitoring/config/email.yaml`
- 环境变量: `.env` 文件
- 支持腾讯企业邮箱等 SMTP 服务
- 配置路径自动查找（多路径支持）

**Environment Variables:**
| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SMTP_HOST` | SMTP 服务器地址 | `smtp.exmail.qq.com` |
| `SMTP_PORT` | SMTP 端口 | `465` |
| `SENDER_EMAIL` | 发件人邮箱 | - |
| `SENDER_PASSWORD` | 发件人密码/授权码 | - |
| `RECIPIENTS_TO` | 默认收件人（逗号分隔） | - |

**Bug Fixes:**
- 修复 `send_panel_to_email` 变量作用域问题
- 修复邮件配置文件路径查找问题
- 修复聚合查询结果格式不一致问题

**Documentation:**
- 更新 README.md 添加聚合统计说明
- 更新 README.md 添加 Panel 操作说明
- 更新 README.md 添加智能回退机制说明
- 更新 README.md 添加邮件配置指南

### Usage Examples

```python
# 聚合统计 - 获取所有错误类型（不受 size 限制）
search_es_aggregation(
    lucene_query='metrics.msg: "uploadTrack" AND metrics.msg: "reason"',
    agg_field='metrics.payload.code',
    time_range='today',
    agg_size=200
)

# 执行 Panel 查询
get_panel_query_results(
    dashboard_uid='urJcwIvHz',
    panel_id=13,
    time_range='24h'
)

# 获取 Panel 直接链接
get_panel_render_url(
    dashboard_uid='urJcwIvHz',
    panel_id=13,
    time_range='today'
)

# 下载 Panel 截图（render 不可用时自动回退到链接）
download_panel_render(
    dashboard_uid='urJcwIvHz',
    panel_id=13,
    time_range='today'
)

# 发送 Panel 到邮件（render 不可用时自动发送链接邮件）
send_panel_to_email(
    dashboard_uid='urJcwIvHz',
    panel_id=13,
    recipients='user@example.com',
    time_range='today'
)
```

---

### Added - 2026-01-29

#### Tupu BI MCP Server (`mcp/tupu/bi/`)

**New Tools:**
- `get_beijing_time` - 获取当前北京时间 (UTC+8)
  - 支持多种格式: ISO 8601、Unix 时间戳（秒/毫秒）、可读格式
  - 示例: `2026-01-29T18:30:45+08:00`

**Changes:**
- 修复类型警告：添加 `Dict, Any` 类型导入
- 将整数时间值转换为字符串以符合类型检查

#### Grafana Agent (`agent/grafana/`)

**New Tools:**
- `get_device_full_info` - 获取设备完整信息（整合接口）
  - 自动完成：摄像头配置 → 认证 Token → 客户信息 → 门店信息
  - 支持参数: `device_id`, `token_id`, `secret`
  - 环境变量: `TUPI_BI_TOKEN_ID`, `TUPI_BI_AUTH_SECRET`

- `get_current_beijing_time` - 获取当前北京时间
  - 支持格式: `iso`, `readable`, `date`, `time`
  - 示例: `get_current_beijing_time()` → `"2026-01-29 18:30:45"`

**Enhanced:**
- `AlertResult` 数据类新增字段:
  - `customer_info: Dict[str, Any]` - 客户信息
  - `store_info: Dict[str, Any]` - 门店信息
  - `device_full_info: Dict[str, Any]` - 设备完整信息

- `_enrich_alerts_with_camera_config()` 函数:
  - 现在调用 `get_device_full_info` 替代 `get_camera_config`
  - 自动补充摄像头配置、客户信息、门店信息

- `_format_alerts_summary()` 函数:
  - 新增客户信息显示（👤 图标）
  - 新增门店信息显示（🏪 图标）
  - 显示重要字段: name, email, phone, address, location 等

**Time Zone Support:**
- 新增北京时区常量 `BEIJING_TZ = timezone(timedelta(hours=8))`
- 所有 ES 查询默认使用北京时区 (UTC+8)
- 新增辅助函数:
  - `get_beijing_time()` - 获取北京时间 datetime 对象
  - `format_beijing_time()` - 格式化北京时间
  - `get_beijing_time_str()` - 获取北京时间字符串

**Agent Instructions:**
- 更新时区说明：所有时间查询默认使用北京时区
- 新增 Tupu BI 工具使用示例

**Environment Variables:**
| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TUPI_BI_TOKEN_ID` | Token ID（用于获取认证 Token） | - |
| `TUPI_BI_AUTH_SECRET` | 认证密钥 | - |
| `TUPI_BI_API_BASE` | Tupu BI API 地址 | `https://api.bi.tuputech.com` |

### API Documentation

#### Tupu BI MCP Server - `get_beijing_time`

```json
// 请求
{
  "format": "readable"  // 可选: "iso", "timestamp", "timestamp_ms", "readable"
}

// 响应
{
  "timezone": "Asia/Shanghai (UTC+8)",
  "timezone_offset": "+08:00",
  "datetime": "2026-01-29 18:30:45",
  "format": "Readable"
}
```

#### Tupu BI MCP Server - `get_device_full_info`

```json
// 请求
{
  "device_id": "a8:3f:a1:30:16:fb",
  "token_id": "your-token-id",
  "secret": "your-secret"
}

// 响应
{
  "device_id": "a8:3f:a1:30:16:fb",
  "camera_config": { ... },
  "customer_info": { "name": "...", "email": "..." },
  "store_info": { "name": "...", "address": "..." }
}
```
