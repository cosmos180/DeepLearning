#!/usr/bin/env python3
"""
MCP Server for Grafana Dashboard Panel Reading
This server provides tools to read panels from specified Grafana dashboards.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    Tool,
    TextContent,
    INTERNAL_ERROR,
    INVALID_PARAMS,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("grafana-mcp-server")


class GrafanaClient:
    """Client for interacting with Grafana API"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    async def get_dashboard(self, dashboard_uid: str) -> Dict[str, Any]:
        """Get dashboard by UID"""
        url = f"{self.base_url}/api/dashboards/uid/{dashboard_uid}"

        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return data.get("dashboard", {})
            except httpx.HTTPError as e:
                logger.error(f"Error fetching dashboard {dashboard_uid}: {e}")
                raise

    async def get_dashboard_panels(self, dashboard_uid: str) -> List[Dict[str, Any]]:
        """Get all panels from a dashboard"""
        dashboard = await self.get_dashboard(dashboard_uid)
        panels = dashboard.get("panels", [])
        return panels

    async def get_panel(self, dashboard_uid: str, panel_id: int) -> Dict[str, Any]:
        """Get a specific panel from a dashboard"""
        panels = await self.get_dashboard_panels(dashboard_uid)

        for panel in panels:
            if panel.get("id") == panel_id:
                return panel

        raise ValueError(f"Panel {panel_id} not found in dashboard {dashboard_uid}")

    async def query_panel_data(
        self,
        dashboard_uid: str,
        panel_id: int,
        time_range: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Query data for a specific panel"""
        url = f"{self.base_url}/api/ds/query"

        # Get panel details first
        panel = await self.get_panel(dashboard_uid, panel_id)

        # Prepare query request
        query_data = {
            "queries": [],
            "range": time_range or {"from": "now-1h", "to": "now"},
        }

        # This is a simplified version - in practice, you'd need to construct
        # the proper query based on the panel's datasource and configuration
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.post(url, json=query_data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error querying panel data: {e}")
                raise


# Global Grafana client instance
grafana_client: Optional[GrafanaClient] = None


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="list_dashboards",
            description="List available Grafana dashboards",
            inputSchema={
                "type": "object",
                "properties": {
                    "grafana_url": {
                        "type": "string",
                        "description": "Grafana server URL",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Grafana API key (optional)",
                    },
                },
                "required": ["grafana_url"],
            },
        ),
        Tool(
            name="get_dashboard_panels",
            description="Get all panels from a specific dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "grafana_url": {
                        "type": "string",
                        "description": "Grafana server URL",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Grafana API key (optional)",
                    },
                    "dashboard_uid": {"type": "string", "description": "Dashboard UID"},
                },
                "required": ["grafana_url", "dashboard_uid"],
            },
        ),
        Tool(
            name="get_panel_info",
            description="Get detailed information about a specific panel",
            inputSchema={
                "type": "object",
                "properties": {
                    "grafana_url": {
                        "type": "string",
                        "description": "Grafana server URL",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Grafana API key (optional)",
                    },
                    "dashboard_uid": {"type": "string", "description": "Dashboard UID"},
                    "panel_id": {"type": "integer", "description": "Panel ID"},
                },
                "required": ["grafana_url", "dashboard_uid", "panel_id"],
            },
        ),
        Tool(
            name="query_panel_data",
            description="Query data from a specific panel",
            inputSchema={
                "type": "object",
                "properties": {
                    "grafana_url": {
                        "type": "string",
                        "description": "Grafana server URL",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Grafana API key (optional)",
                    },
                    "dashboard_uid": {"type": "string", "description": "Dashboard UID"},
                    "panel_id": {"type": "integer", "description": "Panel ID"},
                    "time_from": {
                        "type": "string",
                        "description": "Start time (e.g., 'now-1h')",
                    },
                    "time_to": {
                        "type": "string",
                        "description": "End time (e.g., 'now')",
                    },
                },
                "required": ["grafana_url", "dashboard_uid", "panel_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls"""
    global grafana_client

    try:
        tool_name = request.params.name
        arguments = request.params.arguments or {}

        # Initialize Grafana client
        grafana_url = arguments.get("grafana_url")
        api_key = arguments.get("api_key")

        if not grafana_url:
            return CallToolResult(
                content=[
                    TextContent(type="text", text="Error: grafana_url is required")
                ],
                isError=True,
            )

        grafana_client = GrafanaClient(grafana_url, api_key)

        if tool_name == "list_dashboards":
            # Note: This would need to be implemented with proper search API
            # For now, we'll return a placeholder
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Dashboard listing not yet implemented. Please use dashboard UID directly.",
                    )
                ]
            )

        elif tool_name == "get_dashboard_panels":
            dashboard_uid = arguments.get("dashboard_uid")
            if not dashboard_uid:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text="Error: dashboard_uid is required"
                        )
                    ],
                    isError=True,
                )

            try:
                panels = await grafana_client.get_dashboard_panels(dashboard_uid)

                # Format panel information
                panel_info = []
                for panel in panels:
                    panel_info.append(
                        {
                            "id": panel.get("id"),
                            "title": panel.get("title", "Untitled"),
                            "type": panel.get("type", "unknown"),
                            "description": panel.get("description", ""),
                        }
                    )

                return CallToolResult(
                    content=[
                        TextContent(type="text", text=json.dumps(panel_info, indent=2))
                    ]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error fetching dashboard panels: {str(e)}",
                        )
                    ],
                    isError=True,
                )

        elif tool_name == "get_panel_info":
            dashboard_uid = arguments.get("dashboard_uid")
            panel_id = arguments.get("panel_id")

            if not dashboard_uid or panel_id is None:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: dashboard_uid and panel_id are required",
                        )
                    ],
                    isError=True,
                )

            try:
                panel = await grafana_client.get_panel(dashboard_uid, panel_id)
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(panel, indent=2))]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Error fetching panel info: {str(e)}"
                        )
                    ],
                    isError=True,
                )

        elif tool_name == "query_panel_data":
            dashboard_uid = arguments.get("dashboard_uid")
            panel_id = arguments.get("panel_id")
            time_from = arguments.get("time_from", "now-1h")
            time_to = arguments.get("time_to", "now")

            if not dashboard_uid or panel_id is None:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: dashboard_uid and panel_id are required",
                        )
                    ],
                    isError=True,
                )

            try:
                time_range = {"from": time_from, "to": time_to}
                data = await grafana_client.query_panel_data(
                    dashboard_uid, panel_id, time_range
                )
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(data, indent=2))]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Error querying panel data: {str(e)}"
                        )
                    ],
                    isError=True,
                )

        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {tool_name}")],
                isError=True,
            )

    except Exception as e:
        logger.error(f"Error in call_tool: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Internal error: {str(e)}")],
            isError=True,
        )


async def main():
    """Run the MCP server"""
    # Run the server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="grafana-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
