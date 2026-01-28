# 图普 BI MCP Server

将图普科技 BI 业务 API 封装为 MCP (Model Context Protocol) 能力。

## 功能特性

- 支持获取摄像头基本参数配置
- 支持获取认证 Token
- 自动识别设备标识符类型（MAC 地址或序列号）
- 异步 HTTP 请求
- 标准 MCP 协议接口

## 安装

```bash
pip install -r requirements.txt
# 或
pip install -e .
```

## 使用方法

### 作为 MCP 服务器运行

```bash
# 设置环境变量（推荐）
export TUPI_BI_AUTH_SECRET="your-secret-here"

python -m tupu_bi.server
# 或
tupu-bi-mcp-server
```

### MCP 工具

#### get_camera_config

获取摄像头基本参数配置。

**参数：**
- `device_id` (必填): 设备标识符
  - MAC 地址格式：`a8:3f:a1:30:16:fb`
  - 序列号格式：`6AB2F0C3E97DD45610FE4C45EA1E71B1`
- `api_base` (可选): API 基础地址

**示例：**
```json
{"device_id": "a8:3f:a1:30:16:fb"}
```

#### get_auth_token

获取认证 Token。

**参数：**
- `token_id` (必填): Token ID，如 `0oiis773qijrlem5e0q27ag49bt20r0eh6l7qdbd`
- `secret` (可选): 认证密钥。**推荐通过环境变量 `TUPI_BI_AUTH_SECRET` 设置**，而非每次传递
- `expires_in` (可选): 过期时间（秒），默认 7200
- `api_base` (可选): API 基础地址

**安全使用方式：**
```bash
# 推荐方式：通过环境变量设置 secret
export TUPI_BI_AUTH_SECRET="your-secret-here"
# 然后调用时只需传递 token_id
{"token_id": "0oiis773qijrlem5e0q27ag49bt20r0eh6l7qdbd"}
```

## 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `TUPI_BI_API_BASE` | API 基础地址 | `https://api.bi.tuputech.com` |
| `TUPI_BI_AUTH_SECRET` | 认证密钥（推荐使用此方式传递 secret） | `your-secret-here` |

## 开发

### 测试客户端

```python
from tupu_bi.client import TupuBiClient

client = TupuBiClient()

# 异步调用摄像头配置
config = await client.get_camera_config("a8:3f:a1:30:16:fb")

# 同步调用
config = client.get_camera_config_sync("6AB2F0C3E97DD45610FE4C45EA1E71B1")

# 获取认证 token（secret 建议从环境变量读取）
import os
token = await client.get_auth_token(
    token_id="your-token-id",
    secret=os.getenv("TUPI_BI_AUTH_SECRET"),
    expires_in=7200
)
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/v1/inner/camera/config/json` | GET | 获取摄像头配置 |
| `/v1/auth/token/{token_id}` | POST | 获取认证 Token |

## 设备标识符说明

系统会自动判断设备标识符类型：

- **MAC 地址**: 格式为 `xx:xx:xx:xx:xx:xx`，构建为 `box_{mac}`
- **序列号**: 其他格式，构建为 `boxsn_{serial}`

## 安全注意事项

1. **secret 管理**：推荐使用环境变量 `TUPI_BI_AUTH_SECRET` 存储认证密钥，避免在调用参数中传递
2. **日志安全**：secret 参数不会被记录到日志中
3. **响应脱敏**：API 响应中不包含原始 secret
