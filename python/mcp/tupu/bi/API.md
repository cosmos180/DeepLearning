# Tupu BI MCP Server API 文档

本文档详细描述图普 BI MCP Server 提供的 API 接口。

## 目录

- [概述](#概述)
- [环境变量](#环境变量)
- [API 端点](#api-端点)
  - [获取摄像头配置](#1-获取摄像头配置-get_camera_config)
  - [获取认证 Token](#2-获取认证-token-get_auth_token)
  - [获取客户信息](#3-获取客户信息-get_customer_info)
  - [获取门店信息](#4-获取门店信息-get_store_info)
- [设备标识符说明](#设备标识符说明)
- [错误处理](#错误处理)
- [代码示例](#代码示例)

---

## 概述

Tupu BI MCP Server 提供四个核心 API 工具：

| 工具 | 方法 | 端点 | 说明 |
|------|------|------|------|
| `get_camera_config` | GET | `/v1/inner/camera/config/json` | 获取摄像头基本参数配置 |
| `get_auth_token` | POST | `/v1/auth/token/{token_id}` | 获取认证 Token |
| `get_customer_info` | GET | `/v1/customer/{uid}` | 获取客户信息 |
| `get_store_info` | GET | `/v1/store/{sid}?UID={uid}` | 获取门店信息 |

---

## 环境变量

| 变量名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `TUPI_BI_API_BASE` | string | 否 | `https://api.bi.tuputech.com` | API 基础地址 |
| `TUPI_BI_AUTH_SECRET` | string | 否* | - | 认证密钥（推荐使用环境变量） |

*注：`secret` 也可作为参数传递，但推荐使用环境变量。

---

## API 端点

### 1. 获取摄像头配置 (`get_camera_config`)

获取摄像头基本参数配置，支持通过 MAC 地址或序列号查询。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device_id` | string | 是 | 设备标识符，支持 MAC 地址或序列号 |
| `api_base` | string | 否 | API 基础地址（默认使用环境变量或默认值） |

#### 设备标识符格式

**MAC 地址格式：**
```
a8:3f:a1:30:16:fb
```

**序列号格式：**
```
6AB2F0C3E97DD45610FE4C45EA1E71B1
```

#### 请求示例

```json
{
  "device_id": "a8:3f:a1:30:16:fb"
}
```

#### 响应示例

```json
{
  "status": "ok",
  "config": {
    "resolution": "1080p",
    "framerate": 30,
    "encoding": "H.264"
  }
}
```

#### 错误响应

```json
{
  "error": "device_id 参数必填"
}
```

---

### 2. 获取认证 Token (`get_auth_token`)

获取认证 Token，用于后续 API 访问的鉴权。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `token_id` | string | 是 | - | Token ID（URL 路径参数） |
| `secret` | string | 否* | - | 认证密钥（推荐使用环境变量） |
| `expires_in` | integer | 否 | 7200 | 过期时间（秒） |
| `api_base` | string | 否 | - | API 基础地址 |

#### token_id 格式

```
0oiis773qijrlem5e0q27ag49bt20r0eh6l7qdbd
```

#### 安全使用方式

**推荐：通过环境变量设置 secret**
```bash
export TUPI_BI_AUTH_SECRET="your-secret-here"
```

然后调用时无需传递 secret 参数：
```json
{
  "token_id": "0oiis773qijrlem5e0q27ag49bt20r0eh6l7qdbd"
}
```

#### 请求示例（带参数）

```json
{
  "token_id": "0oiis773qijrlem5e0q27ag49bt20r0eh6l7qdbd",
  "secret": "your-secret-here",
  "expires_in": 3600
}
```

#### 响应示例（脱敏）

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 7200,
  "token_id": "0oiis773qijrlem5e0q27ag49bt20r0eh6l7qdbd",
  "_note": "secret 参数已脱敏，未包含在响应中"
}
```

#### 错误响应

**缺少 token_id：**
```json
{
  "error": "token_id 参数必填"
}
```

**缺少 secret：**
```json
{
  "error": "secret 未提供。请通过环境变量 TUPI_BI_AUTH_SECRET 设置，或作为参数传递"
}
```

---

### 3. 获取客户信息 (`get_customer_info`)

根据客户 UID 和认证 Token 获取客户信息。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `uid` | string | 是 | 客户 UID（URL 路径参数） |
| `token` | string | 是 | 认证 Token（请求头） |
| `api_base` | string | 否 | API 基础地址（默认使用环境变量或默认值） |

#### uid 格式

```
682ffb703953c231e8cc46a7
```

#### 请求示例

```json
{
  "uid": "682ffb703953c231e8cc46a7",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiIwb2lpczc3M3FpanJsZW01ZTBxMjdhZzQ5YnQyMHIwZWg2bDdxZGJkIiwiYWNjb3VudCI6ImJveDMzOTlAdHVwdXRlY2guY29tIiwiaWF0IjoxNzY5MTM5NTg3fQ..."
}
```

#### cURL 示例

```bash
curl --location 'https://api.bi.tuputech.com/v1/customer/682ffb703953c231e8cc46a7' \
--header 'token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

#### 响应示例

```json
{
  "uid": "682ffb703953c231e8cc46a7",
  "name": "客户名称",
  "email": "customer@example.com",
  "status": "active"
}
```

#### 错误响应

**缺少 uid：**
```json
{
  "error": "uid 参数必填"
}
```

**缺少 token：**
```json
{
  "error": "token 参数必填"
}
```

**认证失败：**
```json
{
  "error": "Unauthorized"
}
```

---

### 4. 获取门店信息 (`get_store_info`)

根据门店 SID、客户 UID 和认证 Token 获取门店信息。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sid` | string | 是 | 门店 SID（URL 路径参数） |
| `uid` | string | 是 | 客户 UID（查询参数） |
| `token` | string | 是 | 认证 Token（请求头） |
| `api_base` | string | 否 | API 基础地址（默认使用环境变量或默认值） |

#### sid 格式

```
682ffbae23e8639b53ec6aad
```

#### uid 格式

```
682ffb703953c231e8cc46a7
```

#### 请求示例

```json
{
  "sid": "682ffbae23e8639b53ec6aad",
  "uid": "682ffb703953c231e8cc46a7",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiIwb2lpczc3M3FpanJsZW01ZTBxMjdhZzQ5YnQyMHIwZWg2bDdxZGJkIiwiYWNjb3VudCI6ImJveDMzOTlAdHVwdXRlY2guY29tIiwiaWF0IjoxNzY5MTM5NTg3fQ..."
}
```

#### cURL 示例

```bash
curl --location 'https://api.bi.tuputech.com/v1/store/682ffbae23e8639b53ec6aad?UID=682ffb703953c231e8cc46a7' \
--header 'token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

#### 响应示例

```json
{
  "sid": "682ffbae23e8639b53ec6aad",
  "name": "门店名称",
  "address": "门店地址",
  "status": "active"
}
```

#### 错误响应

**缺少 sid：**
```json
{
  "error": "sid 参数必填"
}
```

**缺少 uid：**
```json
{
  "error": "uid 参数必填"
}
```

**缺少 token：**
```json
{
  "error": "token 参数必填"
}
```

**认证失败：**
```json
{
  "error": "Unauthorized"
}
```

---

## 设备标识符说明

系统会自动判断设备标识符类型：

| 标识符类型 | 格式 | User-Agent 构建 |
|-----------|------|-----------------|
| **MAC 地址** | `xx:xx:xx:xx:xx:xx` | `tupu-smart-endpoint:1.0/box_{mac}` |
| **序列号** | 其他格式 | `tupu-smart-endpoint:1.0/boxsn_{serial}` |

### MAC 地址正则表达式

```regex
^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}$
```

### 示例

| 输入 | 识别类型 | User-Agent |
|------|---------|-----------|
| `a8:3f:a1:30:16:fb` | MAC 地址 | `tupu-smart-endpoint:1.0/box_a8:3f:a1:30:16:fb` |
| `AA:BB:CC:DD:EE:FF` | MAC 地址 | `tupu-smart-endpoint:1.0/box_AA:BB:CC:DD:EE:FF` |
| `6AB2F0C3E97DD45610FE4C45EA1E71B1` | 序列号 | `tupu-smart-endpoint:1.0/boxsn_6AB2F0C3E97DD45610FE4C45EA1E71B1` |

---

## 错误处理

### HTTP 错误

API 调用可能返回以下 HTTP 错误状态码：

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 参数验证错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `device_id 参数必填` | 调用 `get_camera_config` 未提供设备标识符 | 添加 `device_id` 参数 |
| `token_id 参数必填` | 调用 `get_auth_token` 未提供 Token ID | 添加 `token_id` 参数 |
| `secret 未提供` | 调用 `get_auth_token` 未提供 secret | 通过环境变量设置或传递参数 |
| `uid 参数必填` | 调用 `get_customer_info` 或 `get_store_info` 未提供客户 UID | 添加 `uid` 参数 |
| `token 参数必填` | 调用 `get_customer_info` 或 `get_store_info` 未提供认证 Token | 添加 `token` 参数 |
| `sid 参数必填` | 调用 `get_store_info` 未提供门店 SID | 添加 `sid` 参数 |
| `未知工具: {name}` | 调用了不存在的工具 | 检查工具名称拼写 |

---

## 代码示例

### Python 客户端（异步）

```python
import asyncio
from tupu_bi.client import TupuBiClient

async def main():
    client = TupuBiClient()

    # 获取摄像头配置（MAC 地址）
    config = await client.get_camera_config("a8:3f:a1:30:16:fb")
    print(config)

    # 获取摄像头配置（序列号）
    config = await client.get_camera_config("6AB2F0C3E97DD45610FE4C45EA1E71B1")
    print(config)

    # 获取认证 Token
    token_result = await client.get_auth_token(
        token_id="your-token-id",
        secret="your-secret",
        expires_in=7200
    )
    token = token_result["token"]
    print(token_result)

    # 获取客户信息
    customer = await client.get_customer_info("682ffb703953c231e8cc46a7", token)
    print(customer)

    # 获取门店信息
    store = await client.get_store_info("682ffbae23e8639b53ec6aad", "682ffb703953c231e8cc46a7", token)
    print(store)

asyncio.run(main())
```

### Python 客户端（同步）

```python
from tupu_bi.client import TupuBiClient

client = TupuBiClient()

# 同步方式获取摄像头配置
config = client.get_camera_config_sync("a8:3f:a1:30:16:fb")
print(config)

# 同步方式获取认证 Token
token_result = client.get_auth_token_sync(
    token_id="your-token-id",
    secret="your-secret"
)
token = token_result["token"]
print(token_result)

# 同步方式获取客户信息
customer = client.get_customer_info_sync("682ffb703953c231e8cc46a7", token)
print(customer)

# 同步方式获取门店信息
store = client.get_store_info_sync("682ffbae23e8639b53ec6aad", "682ffb703953c231e8cc46a7", token)
print(store)
```

### 使用环境变量

```python
import os
from tupu_bi.client import TupuBiClient

# 设置环境变量
os.environ["TUPI_BI_AUTH_SECRET"] = "your-secret-here"
os.environ["TUPI_BI_API_BASE"] = "https://custom.api.com"

client = TupuBiClient()

# 使用环境变量中的 secret
token = await client.get_auth_token(token_id="your-token-id", secret=os.getenv("TUPI_BI_AUTH_SECRET"))
```

### MCP 工具调用

```python
from mcp.client import Client

# 通过 MCP 协议调用
async with Client() as client:
    # 获取摄像头配置
    result = await client.call_tool("get_camera_config", {
        "device_id": "a8:3f:a1:30:16:fb"
    })
    print(result)

    # 获取认证 Token（secret 从环境变量读取）
    result = await client.call_tool("get_auth_token", {
        "token_id": "your-token-id"
    })
    print(result)

    # 获取客户信息
    result = await client.call_tool("get_customer_info", {
        "uid": "682ffb703953c231e8cc46a7",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    })
    print(result)

    # 获取门店信息
    result = await client.call_tool("get_store_info", {
        "sid": "682ffbae23e8639b53ec6aad",
        "uid": "682ffb703953c231e8cc46a7",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    })
    print(result)
```

---

## 测试

运行单元测试：

```bash
# 安装测试依赖
pip install -r requirements.txt

# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_client.py
pytest tests/test_server.py

# 显示详细输出
pytest tests/ -v

# 显示代码覆盖率
pytest tests/ --cov=tupu_bi --cov-report=html
```

---

## 安全注意事项

1. **secret 管理**
   - 推荐使用环境变量 `TUPI_BI_AUTH_SECRET` 存储认证密钥
   - 避免在代码中硬编码 secret
   - 不要将 secret 提交到版本控制系统

2. **日志安全**
   - secret 参数不会被记录到日志中
   - API 响应中不包含原始 secret

3. **Token 过期**
   - 默认过期时间为 7200 秒（2 小时）
   - 根据安全需求调整 `expires_in` 参数

4. **HTTPS**
   - 生产环境务必使用 HTTPS
   - 验证 SSL 证书有效性
