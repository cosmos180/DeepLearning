# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added - 2026-01-29

#### New Tools

**`get_beijing_time`** - 获取当前北京时间 (UTC+8)

一个新的 MCP 工具，用于获取当前北京时间，支持多种输出格式。

**参数:**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `format` | string | `"iso"` | 时间格式 |

**支持的格式:**
| 格式值 | 返回内容 | 示例 |
|--------|----------|------|
| `"iso"` | ISO 8601 格式 | `2026-01-29T18:30:45+08:00` |
| `"timestamp"` | Unix 时间戳（秒） | `1738177845` |
| `"timestamp_ms"` | Unix 时间戳（毫秒） | `1738177845000` |
| `"readable"` | 可读格式 + 详细字段 | `2026-01-29 18:30:45` |

**请求示例:**
```json
{
  "format": "readable"
}
```

**响应示例:**
```json
{
  "timezone": "Asia/Shanghai (UTC+8)",
  "timezone_offset": "+08:00",
  "datetime": "2026-01-29 18:30:45",
  "format": "Readable",
  "year": "2026",
  "month": "1",
  "day": "29",
  "hour": "18",
  "minute": "30",
  "second": "45",
  "weekday": "Wednesday"
}
```

### Changes

**类型修复:**
- 添加 `Dict, Any` 类型导入以修复类型检查警告
- 将 `readable` 格式中的整数时间值转换为字符串

**时区支持:**
- 新增北京时区常量 `BEIJING_TZ = timezone(timedelta(hours=8))`
- 所有时间工具默认使用 Asia/Shanghai 时区 (UTC+8)

### Updated Tools

**`get_device_full_info`** - 获取设备完整信息（之前已存在）

整合接口，自动完成以下流程：
1. 获取摄像头配置（包含 UID 和 SID）
2. 获取认证 Token
3. 获取客户信息
4. 获取门店信息

**环境变量:**
| 变量 | 说明 |
|------|------|
| `TUPI_BI_TOKEN_ID` | Token ID（用于获取认证 Token） |
| `TUPI_BI_AUTH_SECRET` | 认证密钥（推荐使用环境变量） |
| `TUPI_BI_API_BASE` | API 基础地址（默认: `https://api.bi.tuputech.com`） |

### Usage Examples

```python
# MCP 工具调用
from mcp.client import Client

async with Client() as client:
    # 获取当前北京时间（ISO 格式）
    result = await client.call_tool("get_beijing_time", {"format": "iso"})
    print(result)
    # {"timezone": "Asia/Shanghai (UTC+8)", "datetime": "2026-01-29T18:30:45+08:00", ...}

    # 获取时间戳
    result = await client.call_tool("get_beijing_time", {"format": "timestamp"})
    print(result)
    # {"timezone": "Asia/Shanghai (UTC+8)", "timestamp": 1738177845, ...}

    # 获取设备完整信息
    result = await client.call_tool("get_device_full_info", {
        "device_id": "a8:3f:a1:30:16:fb",
        "token_id": "your-token-id"
        # secret 从环境变量 TUPI_BI_AUTH_SECRET 读取
    })
    print(result)
    # {"device_id": "...", "camera_config": {...}, "customer_info": {...}, "store_info": {...}}
```

```bash
# 设置环境变量
export TUPI_BI_AUTH_SECRET="your-secret-here"
export TUPI_BI_TOKEN_ID="your-token-id-here"

# 运行 MCP Server
python -m tupu_bi.server
```

### API Endpoints Summary

| 工具 | 方法 | 端点 | 说明 |
|------|------|------|------|
| `get_camera_config` | GET | `/v1/inner/camera/config/json` | 获取摄像头配置 |
| `get_auth_token` | POST | `/v1/auth/token/{token_id}` | 获取认证 Token |
| `get_customer_info` | GET | `/v1/customer/{uid}` | 获取客户信息 |
| `get_store_info` | GET | `/v1/store/{sid}?UID={uid}` | 获取门店信息 |
| `get_device_full_info` | 整合 | 以上所有接口 | 获取设备完整信息（一站式） |
| `get_beijing_time` | 本地 | - | 获取当前北京时间 |
