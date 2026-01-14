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
    ServerCapabilities,
    ToolsCapability,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
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

    async def list_dashboards(
        self,
        query: Optional[str] = None,
        tag: Optional[str] = None,
        folder: Optional[str] = None,
        folder_ids: Optional[list[int]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List dashboards using Grafana search API

        Args:
            query: Search query string
            tag: Filter by tag
            folder: Filter by folder title (client-side filter)
            folder_ids: Filter by folder IDs (server-side filter)
            limit: Maximum number of results
        """
        url = f"{self.base_url}/api/search"

        params = {"type": "dash-db", "limit": limit}
        if query:
            params["query"] = query
        if tag:
            params["tag"] = tag
        if folder_ids:
            params["folderIds"] = ",".join(str(fid) for fid in folder_ids)

        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                dashboards = response.json()

                # Client-side filter by folder title if specified
                if folder:
                    dashboards = [
                        d
                        for d in dashboards
                        if folder.lower() in (d.get("folderTitle", "") or "").lower()
                    ]

                return dashboards
            except httpx.HTTPError as e:
                logger.error(f"Error listing dashboards: {e}")
                raise

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

        # Get datasource info from panel
        datasource = panel.get("datasource", {})
        datasource_uid = datasource.get("uid")
        datasource_type = datasource.get("type", "")

        # Get targets from panel (the query definitions)
        targets = panel.get("targets", [])

        # Get time range
        time_from = (time_range or {"from": "now-1h", "to": "now"})["from"]
        time_to = (time_range or {"from": "now-1h", "to": "now"})["to"]

        # Build query request - use the exact target format from the panel
        queries = []
        ref_id = "A"

        for target in targets:
            # Build query based on datasource type
            if datasource_type == "elasticsearch":
                query = {
                    "refId": ref_id,
                    "datasource": {"type": "elasticsearch", "uid": datasource_uid},
                    "metrics": target.get("metrics", []),
                    "bucketAggs": target.get("bucketAggs", []),
                    "timeField": target.get("timeField", "@timestamp"),
                    "alias": target.get("alias", ""),
                }
            else:
                # For other datasources like Prometheus, use the raw target
                query = {
                    "refId": ref_id,
                    "datasource": {"type": datasource_type, "uid": datasource_uid},
                }
                query.update(target)

            queries.append(query)
            ref_id = chr(ord(ref_id) + 1)

        query_data = {
            "queries": queries,
            "from": time_from,
            "to": time_to,
        }

        logger.info(f"Querying panel {panel_id} with {len(queries)} queries")

        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            try:
                response = await client.post(url, json=query_data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error querying panel data: {e}")
                # Return a more informative error
                return {
                    "error": str(e),
                    "message": f"Failed to query panel {panel_id}. "
                    f"This is expected for complex datasources like Elasticsearch "
                    f"as they may require specialized query formats.",
                    "datasource_type": datasource_type,
                }

    # ========== Alert API Methods ==========

    async def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get all alert rules from Grafana"""
        url = f"{self.base_url}/api/v1/provisioning/alert-rules"

        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error fetching alert rules: {e}")
                raise

    async def get_alert_states(
        self,
        folder_filter: Optional[str] = None,
        state_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get alert rule states (firing, pending, normal, etc.)

        Args:
            folder_filter: Filter by folder name (e.g., "Production")
            state_filter: Filter by state (e.g., "firing", "pending", "normal", "no_data")
        """
        url = f"{self.base_url}/api/v1/rules"

        params = {}
        if folder_filter:
            params["folder"] = folder_filter

        async with httpx.AsyncClient(headers=self.headers, params=params) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Filter by state if requested
                if state_filter:
                    filtered_data = {"data": {"groups": []}}
                    for group in data.get("data", {}).get("groups", []):
                        filtered_rules = [
                            rule
                            for rule in group.get("rules", [])
                            if rule.get("state", "").lower() == state_filter.lower()
                        ]
                        if filtered_rules:
                            filtered_group = group.copy()
                            filtered_group["rules"] = filtered_rules
                            filtered_data["data"]["groups"].append(filtered_group)
                    return filtered_data

                return data
            except httpx.HTTPError as e:
                logger.error(f"Error fetching alert states: {e}")
                raise

    async def get_notification_history(
        self,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get notification history (alert firing history)"""
        url = f"{self.base_url}/api/v1/notifications"

        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(url, params={"limit": limit})
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error fetching notification history: {e}")
                raise

    async def get_firing_alerts(self) -> List[Dict[str, Any]]:
        """Get currently firing alerts (convenience method)"""
        result = await self.get_alert_states(state_filter="firing")
        firing_alerts = []

        for group in result.get("data", {}).get("groups", []):
            for rule in group.get("rules", []):
                if rule.get("state", "").lower() == "firing":
                    firing_alerts.append(
                        {
                            "name": rule.get("name"),
                            "state": rule.get("state"),
                            "folder": group.get("name", "root"),
                            "query": rule.get("query", ""),
                            "url": rule.get("url", ""),
                            "alerts": rule.get("alerts", []),
                        }
                    )

        return firing_alerts

    async def list_datasources(self) -> List[Dict[str, Any]]:
        """List all configured datasources"""
        url = f"{self.base_url}/api/datasources"

        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error fetching datasources: {e}")
                raise

    async def query_datasource(
        self,
        datasource_uid: str,
        query: Dict[str, Any],
        time_range: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Query a datasource directly (useful for Kibana/Elasticsearch queries)

        Args:
            datasource_uid: The UID of the datasource to query
            query: Query payload for the datasource
            time_range: Optional time range {"from": "now-1h", "to": "now"}
        """
        url = f"{self.base_url}/api/ds-query"

        payload = {
            "queries": [
                {
                    "datasource": {"type": "datasource", "uid": datasource_uid},
                    **query,
                }
            ],
            "range": time_range or {"from": "now-1h", "to": "now"},
        }

        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error querying datasource: {e}")
                raise

    async def query_elasticsearch_direct(
        self,
        datasource_uid: str,
        query: str,
        time_from: str = "now-1h",
        time_to: str = "now",
        size: int = 100,
    ) -> Dict[str, Any]:
        """Query Elasticsearch directly with a query string"""
        # Get datasource info first - use correct endpoint path
        ds_url = f"{self.base_url}/api/datasources/uid/{datasource_uid}"

        datasource = None
        async with httpx.AsyncClient(headers=self.headers) as ds_client:
            # Get datasource details
            try:
                ds_response = await ds_client.get(ds_url)
                ds_response.raise_for_status()
                datasource = ds_response.json()
            except httpx.HTTPStatusError as e:
                logger.info(f"Could not get datasource details from {ds_url}: {e}")
            except Exception as e:
                logger.info(f"Error getting datasource details: {e}")

        # If that didn't work, try listing all datasources
        if not datasource:
            datasources = await self.list_datasources()
            for ds in datasources:
                if ds.get("uid") == datasource_uid:
                    datasource = ds
                    break

        if not datasource:
            raise ValueError(f"Datasource {datasource_uid} not found")

        # Build ES query
        es_url = datasource.get("url", "")
        if not es_url:
            raise ValueError(f"Datasource {datasource_uid} has no URL configured")

        logger.info(f"Querying ES at {es_url} with query: {query}")

        # If URL is relative, make it absolute
        if es_url.startswith("/"):
            # Extract host from Grafana URL
            import re
            grafana_host = re.sub(r'^https?://', '', self.base_url.split('/')[0])
            es_url = f"http://{grafana_host}{es_url}"

        # Build ES query DSL
        es_query = {
            "size": size,
            "query": {
                "bool": {
                    "must": [{"query_string": {"query": query}}]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}]
        }

        # Add time range filter
        # Use the time_from parameter for the time range
        es_query["query"]["bool"]["filter"] = [
            {"range": {"@timestamp": {"gte": time_from, "lte": time_to}}}
        ]

        headers = {
            "Content-Type": "application/json",
        }
        # Add basic auth if datasource has credentials
        if datasource.get("basicAuth"):
            import base64
            auth_str = f"{datasource['basicAuth']['user']}:{datasource['basicAuth']['password']}"
            headers["Authorization"] = f"Basic {base64.b64encode(auth_str.encode()).decode()}"

        async with httpx.AsyncClient(timeout=30.0) as es_client:
            try:
                response = await es_client.post(
                    f"{es_url}/_search",
                    json=es_query,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"ES query error: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Response: {e.response.text}")
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
                    "folder": {
                        "type": "string",
                        "description": "Filter by folder title",
                    },
                    "tag": {
                        "type": "string",
                        "description": "Filter by tag",
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query string",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 100)",
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
        # ========== Alert Tools ==========
        Tool(
            name="get_firing_alerts",
            description="Get all currently firing alerts that need attention",
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
            name="get_alert_states",
            description="Get alert states with optional filters (firing, pending, normal, no_data)",
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
                    "folder": {
                        "type": "string",
                        "description": "Filter by folder name (e.g., 'Production')",
                    },
                    "state": {
                        "type": "string",
                        "description": "Filter by state: 'firing', 'pending', 'normal', 'no_data'",
                        "enum": ["firing", "pending", "normal", "no_data"],
                    },
                },
                "required": ["grafana_url"],
            },
        ),
        Tool(
            name="get_alert_rules",
            description="List all configured alert rules",
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
            name="get_notification_history",
            description="Get notification history (past alert firings)",
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
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of notifications to return (default: 100)",
                    },
                },
                "required": ["grafana_url"],
            },
        ),
        Tool(
            name="list_datasources",
            description="List all configured datasources (useful for finding Kibana/Elasticsearch UID)",
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
            name="query_datasource",
            description="Query a datasource directly (useful for Kibana/Elasticsearch queries)",
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
                    "datasource_uid": {
                        "type": "string",
                        "description": "The UID of the datasource to query",
                    },
                    "query": {
                        "type": "object",
                        "description": "Query payload for the datasource (JSON object)",
                    },
                    "time_from": {
                        "type": "string",
                        "description": "Start time (e.g., 'now-1h')",
                    },
                    "time_to": {
                        "type": "string",
                        "description": "End time (e.g., 'now')",
                    },
                },
                "required": ["grafana_url", "datasource_uid", "query"],
            },
        ),
        Tool(
            name="query_elasticsearch",
            description="Query Elasticsearch directly using Lucene query syntax from panel configurations",
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
                    "datasource_uid": {
                        "type": "string",
                        "description": "The UID of the Elasticsearch datasource",
                    },
                    "query": {
                        "type": "string",
                        "description": "Lucene query string (e.g., 'metrics.platform: \"sdc\" AND metrics.msg: \"局域网\"')",
                    },
                    "time_from": {
                        "type": "string",
                        "description": "Start time (e.g., 'now-1h', 'now-24h')",
                    },
                    "time_to": {
                        "type": "string",
                        "description": "End time (e.g., 'now')",
                    },
                    "size": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100)",
                    },
                },
                "required": ["grafana_url", "datasource_uid", "query"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(tool_name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls"""
    global grafana_client

    try:
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
            try:
                query = arguments.get("query")
                tag = arguments.get("tag")
                folder = arguments.get("folder")
                limit = arguments.get("limit", 100)

                dashboards = await grafana_client.list_dashboards(
                    query=query,
                    tag=tag,
                    folder=folder,
                    limit=limit,
                )

                # Format dashboard list
                if not dashboards:
                    filter_info = []
                    if folder:
                        filter_info.append(f"folder='{folder}'")
                    if tag:
                        filter_info.append(f"tag='{tag}'")
                    if query:
                        filter_info.append(f"query='{query}'")

                    filter_str = " with " + ", ".join(filter_info) if filter_info else ""
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"📋 No dashboards found{filter_str}.",
                            )
                        ]
                    )

                # Add filter info to summary
                filter_parts = []
                if folder:
                    filter_parts.append(f"📁 Folder: {folder}")
                if tag:
                    filter_parts.append(f"🏷️ Tag: {tag}")

                filter_line = " | ".join(filter_parts) + "\n\n" if filter_parts else ""
                summary = f"📋 Found {len(dashboards)} dashboards:\n\n{filter_line}"
                for dash in dashboards:
                    title = dash.get("title", "Untitled")
                    uid = dash.get("uid", "N/A")
                    tags = dash.get("tags", [])
                    folder_title = dash.get("folderTitle", "General")
                    uri = dash.get("url", "")
                    summary += f"• {title}\n"
                    summary += f"  UID: {uid}\n"
                    summary += f"  Folder: {folder_title}\n"
                    if tags:
                        summary += f"  Tags: {', '.join(tags)}\n"
                    summary += f"  URL: {grafana_client.base_url}{uri}\n\n"

                return CallToolResult(
                    content=[TextContent(type="text", text=summary)]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Error listing dashboards: {str(e)}"
                        )
                    ],
                    isError=True,
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
                        TextContent(type="text", text=json.dumps(panel_info, indent=2, ensure_ascii=False))
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
                    content=[TextContent(type="text", text=json.dumps(panel, indent=2, ensure_ascii=False))]
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
                    content=[TextContent(type="text", text=json.dumps(data, indent=2, ensure_ascii=False))]
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

        # ========== Alert Tool Handlers ==========

        elif tool_name == "get_firing_alerts":
            try:
                firing_alerts = await grafana_client.get_firing_alerts()

                # Format output
                if not firing_alerts:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text="✅ No firing alerts. All systems normal.",
                            )
                        ]
                    )

                summary = f"🚨 {len(firing_alerts)} Firing Alert(s):\n\n"
                for alert in firing_alerts:
                    summary += f"• [{alert.get('folder', 'root')}] {alert.get('name', 'Unknown')}\n"
                    summary += f"  State: {alert.get('state', 'Unknown')}\n"
                    if alert.get("url"):
                        summary += f"  URL: {alert.get('url')}\n"

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=summary,
                        )
                    ]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Error fetching firing alerts: {str(e)}"
                        )
                    ],
                    isError=True,
                )

        elif tool_name == "get_alert_states":
            folder_filter = arguments.get("folder")
            state_filter = arguments.get("state")

            try:
                result = await grafana_client.get_alert_states(folder_filter, state_filter)

                # Format output
                groups = result.get("data", {}).get("groups", [])

                if not groups:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"No alert states found for the specified filters.",
                            )
                        ]
                    )

                summary = ""
                total_alerts = 0
                state_counts = {}

                for group in groups:
                    folder_name = group.get("name", "root")
                    rules = group.get("rules", [])

                    for rule in rules:
                        state = rule.get("state", "unknown").upper()
                        state_counts[state] = state_counts.get(state, 0) + 1
                        total_alerts += 1

                        summary += f"\n[{folder_name}] {rule.get('name', 'Unknown')}\n"
                        summary += f"  State: {state}\n"
                        if rule.get("query"):
                            query = rule.get("query", "")
                            summary += f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}\n"

                header = f"📊 Alert States Summary ({total_alerts} total)\n"
                for state, count in sorted(state_counts.items()):
                    header += f"  {state}: {count}\n"
                header += "\n"

                return CallToolResult(
                    content=[TextContent(type="text", text=header + summary)]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Error fetching alert states: {str(e)}"
                        )
                    ],
                    isError=True,
                )

        elif tool_name == "get_alert_rules":
            try:
                rules = await grafana_client.get_alert_rules()

                # Format output
                if not rules:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text", text="No alert rules configured."
                            )
                        ]
                    )

                summary = f"📋 Alert Rules ({len(rules)} total):\n\n"
                for rule in rules:
                    summary += f"• {rule.get('title', 'Untitled')}\n"
                    summary += f"  ID: {rule.get('id')}\n"
                    summary += f"  Folder: {rule.get('folderTitle', 'root')}\n"
                    if rule.get("condition"):
                        summary += f"  Condition: {rule.get('condition')}\n"

                return CallToolResult(
                    content=[TextContent(type="text", text=summary)]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Error fetching alert rules: {str(e)}"
                        )
                    ],
                    isError=True,
                )

        elif tool_name == "get_notification_history":
            limit = arguments.get("limit", 100)

            try:
                history = await grafana_client.get_notification_history(limit)

                # Format output
                if not history:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text", text="No notification history found."
                            )
                        ]
                    )

                summary = f"📜 Notification History (last {len(history)} notifications):\n\n"
                for notification in history:
                    summary += f"• {notification.get('title', 'Unknown')}\n"
                    summary += f"  Time: {notification.get('created_at', 'Unknown')}\n"
                    if notification.get("alert"):
                        summary += f"  Alert: {notification.get('alert', {}).get('name', 'Unknown')}\n"
                    summary += "\n"

                return CallToolResult(
                    content=[TextContent(type="text", text=summary)]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error fetching notification history: {str(e)}",
                        )
                    ],
                    isError=True,
                )

        elif tool_name == "list_datasources":
            try:
                datasources = await grafana_client.list_datasources()

                # Format output
                if not datasources:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text", text="No datasources configured."
                            )
                        ]
                    )

                summary = f"🔌 Datasources ({len(datasources)} total):\n\n"
                for ds in datasources:
                    summary += f"• {ds.get('name', 'Unknown')}\n"
                    summary += f"  Type: {ds.get('type', 'Unknown')}\n"
                    summary += f"  UID: {ds.get('uid', 'Unknown')}\n"
                    summary += f"  URL: {ds.get('url', 'N/A')}\n\n"

                return CallToolResult(
                    content=[TextContent(type="text", text=summary)]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Error listing datasources: {str(e)}"
                        )
                    ],
                    isError=True,
                )

        elif tool_name == "query_datasource":
            datasource_uid = arguments.get("datasource_uid")
            query = arguments.get("query")
            time_from = arguments.get("time_from", "now-1h")
            time_to = arguments.get("time_to", "now")

            if not datasource_uid or not query:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: datasource_uid and query are required",
                        )
                    ],
                    isError=True,
                )

            try:
                time_range = {"from": time_from, "to": time_to}
                data = await grafana_client.query_datasource(
                    datasource_uid, query, time_range
                )
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(data, indent=2, ensure_ascii=False))]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Error querying datasource: {str(e)}"
                        )
                    ],
                    isError=True,
                )

        elif tool_name == "query_elasticsearch":
            datasource_uid = arguments.get("datasource_uid")
            query = arguments.get("query")
            time_from = arguments.get("time_from", "now-1h")
            time_to = arguments.get("time_to", "now")
            size = arguments.get("size", 100)

            if not datasource_uid or not query:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: datasource_uid and query are required",
                        )
                    ],
                    isError=True,
                )

            try:
                data = await grafana_client.query_elasticsearch_direct(
                    datasource_uid, query, time_from, time_to, size
                )

                # Format output with summary
                hits = data.get("hits", {}).get("hits", [])
                total = data.get("hits", {}).get("total", {}).get("value", 0)

                summary = f"🔍 Elasticsearch Query Results:\n\n"
                summary += f"Query: {query}\n"
                summary += f"Time Range: {time_from} to {time_to}\n"
                summary += f"Total Hits: {total}\n"
                summary += f"Returned: {len(hits)} documents\n\n"

                # Show first few documents
                if hits:
                    summary += "Sample documents (first 5):\n"
                    for i, hit in enumerate(hits[:5]):
                        source = hit.get("_source", {})
                        summary += f"\n[{i+1}] ID: {hit.get('_id')}\n"
                        # Show key fields
                        for key in ["metrics", "@timestamp", "deviceId"]:
                            if key in source:
                                summary += f"  {key}: {json.dumps(source[key], ensure_ascii=False)}\n"
                else:
                    summary += "No documents found matching the query.\n"

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=summary + "\n\n" + json.dumps(data, indent=2, ensure_ascii=False)
                        )
                    ]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Error querying Elasticsearch: {str(e)}"
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
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(),
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
