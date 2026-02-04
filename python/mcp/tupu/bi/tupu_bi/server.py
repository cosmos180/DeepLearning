"""
图普 BI API MCP Server
提供摄像头配置等业务 API 的 MCP 能力封装
"""
import asyncio
import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ServerCapabilities,
    ToolsCapability,
)

from .client import TupuBiClient

server = Server("tupu-bi-mcp-server")

DEFAULT_API_BASE = "https://api.bi.tuputech.com"

# 北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))


@server.list_tools()
async def list_tools() -> List[Tool]:
    """声明可用的 MCP 工具"""
    return [
        Tool(
            name="get_camera_config",
            description="获取摄像头基本参数配置",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "设备标识符，支持 MAC 地址（如 a8:3f:a1:30:16:fb）或序列号（如 6AB2F0C3E97DD45610FE4C45EA1E71B1）"
                    },
                    "api_base": {
                        "type": "string",
                        "description": "API 基础地址（可选，默认为图普 BI API 地址）"
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="get_auth_token",
            description="获取认证 Token（secret 可通过环境变量 TUPI_BI_AUTH_SECRET 设置，也可作为参数传递）",
            inputSchema={
                "type": "object",
                "properties": {
                    "token_id": {
                        "type": "string",
                        "description": "Token ID（URL 路径参数，如 0oiis773qijrlem5e0q27ag49bt20r0eh6l7qdbd）"
                    },
                    "secret": {
                        "type": "string",
                        "description": "认证密钥（可选，优先使用环境变量 TUPI_BI_AUTH_SECRET）"
                    },
                    "expires_in": {
                        "type": "integer",
                        "description": "过期时间（秒），默认 7200",
                        "default": 7200,
                    },
                    "api_base": {
                        "type": "string",
                        "description": "API 基础地址（可选，默认为图普 BI API 地址）"
                    },
                },
                "required": ["token_id"],
            },
        ),
        Tool(
            name="get_customer_info",
            description="获取客户信息（通过 UID 和 Token）",
            inputSchema={
                "type": "object",
                "properties": {
                    "uid": {
                        "type": "string",
                        "description": "客户 UID（URL 路径参数，如 682ffb703953c231e8cc46a7）"
                    },
                    "token": {
                        "type": "string",
                        "description": "认证 Token（请求头，如 eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...）"
                    },
                    "api_base": {
                        "type": "string",
                        "description": "API 基础地址（可选，默认为图普 BI API 地址）"
                    },
                },
                "required": ["uid", "token"],
            },
        ),
        Tool(
            name="get_store_info",
            description="获取门店信息（通过 SID、UID 和 Token）",
            inputSchema={
                "type": "object",
                "properties": {
                    "sid": {
                        "type": "string",
                        "description": "门店 SID（URL 路径参数，如 682ffbae23e8639b53ec6aad）"
                    },
                    "uid": {
                        "type": "string",
                        "description": "客户 UID（查询参数，如 682ffb703953c231e8cc46a7）"
                    },
                    "token": {
                        "type": "string",
                        "description": "认证 Token（请求头，如 eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...）"
                    },
                    "api_base": {
                        "type": "string",
                        "description": "API 基础地址（可选，默认为图普 BI API 地址）"
                    },
                },
                "required": ["sid", "uid", "token"],
            },
        ),
        Tool(
            name="get_device_full_info",
            description="获取设备完整信息（整合接口）\n\n自动完成以下流程：\n1. 获取摄像头配置（包含 UID 和 SID）\n2. 获取认证 Token\n3. 获取客户信息\n4. 获取门店信息\n\n返回整合后的完整信息，包含硬件 ID、用户信息、门店信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "设备标识符，支持 MAC 地址（如 a8:3f:a1:30:16:fb）或序列号（如 6AB2F0C3E97DD45610FE4C45EA1E71B1）"
                    },
                    "token_id": {
                        "type": "string",
                        "description": "Token ID（用于获取认证 Token，如 0oiis773qijrlem5e0q27ag49bt20r0eh6l7qdbd）"
                    },
                    "secret": {
                        "type": "string",
                        "description": "认证密钥（可选，优先使用环境变量 TUPI_BI_AUTH_SECRET）"
                    },
                    "expires_in": {
                        "type": "integer",
                        "description": "Token 过期时间（秒），默认 7200",
                        "default": 7200,
                    },
                    "api_base": {
                        "type": "string",
                        "description": "API 基础地址（可选，默认为图普 BI API 地址）"
                    },
                },
                "required": ["device_id", "token_id"],
            },
        ),
        Tool(
            name="get_beijing_time",
            description="获取当前北京时间（UTC+8）",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "时间格式。支持: 'iso' (ISO 8601格式), 'timestamp' (Unix时间戳，秒), 'timestamp_ms' (Unix时间戳，毫秒), 'readable' (可读格式)。默认 'iso'",
                        "enum": ["iso", "timestamp", "timestamp_ms", "readable"],
                        "default": "iso",
                    }
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(tool_name: str, arguments: dict) -> CallToolResult:
    """处理工具调用"""
    try:
        api_base = arguments.get("api_base") or os.getenv("TUPI_BI_API_BASE", DEFAULT_API_BASE)
        client = TupuBiClient(base_url=api_base)

        if tool_name == "get_camera_config":
            device_id = arguments.get("device_id")

            if not device_id:
                return CallToolResult(
                    content=[TextContent(type="text", text="错误: device_id 参数必填")],
                    isError=True,
                )

            result = await client.get_camera_config(device_id)

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )

        elif tool_name == "get_auth_token":
            token_id = arguments.get("token_id")
            # 优先使用参数中的 secret，否则使用环境变量
            secret = arguments.get("secret") or os.getenv("TUPI_BI_AUTH_SECRET")
            expires_in = arguments.get("expires_in", 7200)

            if not token_id:
                return CallToolResult(
                    content=[TextContent(type="text", text="错误: token_id 参数必填")],
                    isError=True,
                )

            if not secret:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="错误: secret 未提供。请通过环境变量 TUPI_BI_AUTH_SECRET 设置，或作为参数传递"
                        )
                    ],
                    isError=True,
                )

            # 调用 API（secret 不会被记录到日志）
            result = await client.get_auth_token(token_id, secret, expires_in)

            # 脱敏处理：不返回原始 secret
            safe_result = {
                "token": result.get("token", ""),
                "expiresIn": result.get("expiresIn", expires_in),
                "token_id": token_id,
                "_note": "secret 参数已脱敏，未包含在响应中",
            }

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(safe_result, ensure_ascii=False, indent=2))]
            )

        elif tool_name == "get_customer_info":
            uid = arguments.get("uid")
            token = arguments.get("token")

            if not uid:
                return CallToolResult(
                    content=[TextContent(type="text", text="错误: uid 参数必填")],
                    isError=True,
                )

            if not token:
                return CallToolResult(
                    content=[TextContent(type="text", text="错误: token 参数必填")],
                    isError=True,
                )

            result = await client.get_customer_info(uid, token)

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )

        elif tool_name == "get_store_info":
            sid = arguments.get("sid")
            uid = arguments.get("uid")
            token = arguments.get("token")

            if not sid:
                return CallToolResult(
                    content=[TextContent(type="text", text="错误: sid 参数必填")],
                    isError=True,
                )

            if not uid:
                return CallToolResult(
                    content=[TextContent(type="text", text="错误: uid 参数必填")],
                    isError=True,
                )

            if not token:
                return CallToolResult(
                    content=[TextContent(type="text", text="错误: token 参数必填")],
                    isError=True,
                )

            result = await client.get_store_info(sid, uid, token)

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )

        elif tool_name == "get_device_full_info":
            device_id = arguments.get("device_id")
            token_id = arguments.get("token_id")
            # 优先使用参数中的 secret，否则使用环境变量
            secret = arguments.get("secret") or os.getenv("TUPI_BI_AUTH_SECRET")
            expires_in = arguments.get("expires_in", 7200)

            if not device_id:
                return CallToolResult(
                    content=[TextContent(type="text", text="错误: device_id 参数必填")],
                    isError=True,
                )

            if not token_id:
                return CallToolResult(
                    content=[TextContent(type="text", text="错误: token_id 参数必填")],
                    isError=True,
                )

            if not secret:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="错误: secret 未提供。请通过环境变量 TUPI_BI_AUTH_SECRET 设置，或作为参数传递"
                        )
                    ],
                    isError=True,
                )

            result = await client.get_device_full_info(device_id, token_id, secret, expires_in)

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )

        elif tool_name == "get_beijing_time":
            # 获取当前北京时间
            format_type = arguments.get("format", "iso")
            now_beijing = datetime.now(BEIJING_TZ)

            result: Dict[str, Any] = {
                "timezone": "Asia/Shanghai (UTC+8)",
                "timezone_offset": "+08:00",
            }

            if format_type == "iso":
                result["datetime"] = now_beijing.isoformat()
                result["format"] = "ISO 8601"
            elif format_type == "timestamp":
                result["timestamp"] = int(now_beijing.timestamp())
                result["format"] = "Unix timestamp (seconds)"
            elif format_type == "timestamp_ms":
                result["timestamp_ms"] = int(now_beijing.timestamp() * 1000)
                result["format"] = "Unix timestamp (milliseconds)"
            elif format_type == "readable":
                result["datetime"] = now_beijing.strftime("%Y-%m-%d %H:%M:%S")
                result["format"] = "Readable"
                result["year"] = str(now_beijing.year)
                result["month"] = str(now_beijing.month)
                result["day"] = str(now_beijing.day)
                result["hour"] = str(now_beijing.hour)
                result["minute"] = str(now_beijing.minute)
                result["second"] = str(now_beijing.second)
                result["weekday"] = now_beijing.strftime("%A")

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )

        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"未知工具: {tool_name}")],
                isError=True,
            )

    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"调用失败: {str(e)}")],
            isError=True,
        )


async def main():
    """MCP 服务器入口"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="tupu-bi-mcp-server",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(),
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
