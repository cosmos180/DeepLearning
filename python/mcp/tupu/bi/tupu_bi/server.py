"""
图普 BI API MCP Server
提供摄像头配置等业务 API 的 MCP 能力封装
"""
import asyncio
import os
import json
from typing import List

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
