#!/usr/bin/env python3
"""
Simple MCP Client Example - Direct subprocess approach
This demonstrates calling the Grafana MCP server directly.
Each functionality is encapsulated in independent methods for easy testing.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Optional


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_CONFIG = {
    "grafana_url": "https://g.dev.tuputech.com",
    "api_key": "",
    "dashboard_uid": "urJcwIvHz",
}


# ============================================================================
# MCP Client Class
# ============================================================================

class GrafanaMCPClient:
    """Simple MCP client for Grafana server using subprocess"""

    def __init__(self, config: Optional[dict] = None):
        """Initialize client with configuration"""
        self.config = config or DEFAULT_CONFIG
        self.process = None
        self.request_id = 0

        # Get paths
        script_dir = Path(__file__).parent
        self.venv_python = script_dir / ".venv" / "bin" / "python"
        self.server_script = script_dir / "server.py"

    async def __aenter__(self):
        """Start the server process"""
        await self.start_server()
        await self.initialize()
        return self

    async def __aexit__(self, *args):
        """Close the server process"""
        await self.close()

    async def start_server(self) -> None:
        """Start the MCP server process"""
        self.process = await asyncio.create_subprocess_exec(
            str(self.venv_python),
            str(self.server_script),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        print(f"[*] Server started with PID: {self.process.pid}")

    async def initialize(self) -> dict:
        """Initialize the MCP session"""
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "simple-client", "version": "1.0.0"},
            },
        }

        response = await self._send_request(init_request)
        print(f"[*] Server capabilities: {response.get('result', {}).get('capabilities')}")

        # Send initialized notification
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        await self._send_notification(initialized_notif)
        print("[*] Session initialized")

        return response

    async def close(self) -> None:
        """Close the server process"""
        if self.process:
            try:
                self.process.stdin.close()
                await self.process.wait()
            except:
                self.process.kill()
                await self.process.wait()
            print("[*] Connection closed")

    def _next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id

    async def _send_request(self, request: dict) -> dict:
        """Send a JSON-RPC request and get response"""
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()

        response_line = await asyncio.wait_for(
            self.process.stdout.readline(), timeout=10.0
        )
        return json.loads(response_line.decode())

    async def _send_request_large(self, request: dict) -> dict:
        """Send a request and read large response in chunks"""
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()

        # Read response in chunks for large data - increased timeout for ES queries
        response_data = b""
        while True:
            chunk = await asyncio.wait_for(
                self.process.stdout.read(4096), timeout=60.0
            )
            if not chunk:
                break
            response_data += chunk
            if b"\n" in response_data:
                break

        return json.loads(response_data.decode())

    async def _send_notification(self, notification: dict) -> None:
        """Send a JSON-RPC notification (no response expected)"""
        notif_str = json.dumps(notification) + "\n"
        self.process.stdin.write(notif_str.encode())
        await self.process.stdin.drain()

    # ========================================================================
    # Tool Methods
    # ========================================================================

    async def list_tools(self) -> list[dict]:
        """List all available tools"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
        }

        response = await self._send_request(request)
        tools = response.get("result", {}).get("tools", [])

        print(f"\n[*] Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.get('name')}: {tool.get('description')}")

        return tools

    async def list_dashboards(
        self,
        query: Optional[str] = None,
        tag: Optional[str] = None,
        folder: Optional[str] = None,
        limit: int = 50,
        grafana_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> str:
        """List all available dashboards"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "list_dashboards",
                "arguments": {
                    "grafana_url": grafana_url or self.config["grafana_url"],
                    "api_key": api_key or self.config["api_key"],
                },
            },
        }

        # Add optional parameters
        if query:
            request["params"]["arguments"]["query"] = query
        if tag:
            request["params"]["arguments"]["tag"] = tag
        if folder:
            request["params"]["arguments"]["folder"] = folder
        request["params"]["arguments"]["limit"] = limit

        response = await self._send_request(request)

        if "error" in response:
            print(f"[!] Error: {response['error']}")
            return ""

        content_list = response.get("result", {}).get("content", [])
        for content in content_list:
            if content.get("type") == "text":
                text = content.get("text")
                print(f"\n[*] Dashboards:")
                print(text)
                return text

        return ""

    async def get_dashboard_panels(
        self,
        dashboard_uid: Optional[str] = None,
        grafana_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> list[dict]:
        """Get all panels from a dashboard"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "get_dashboard_panels",
                "arguments": {
                    "grafana_url": grafana_url or self.config["grafana_url"],
                    "api_key": api_key or self.config["api_key"],
                    "dashboard_uid": dashboard_uid or self.config["dashboard_uid"],
                },
            },
        }

        response = await self._send_request(request)

        if "error" in response:
            print(f"[!] Error: {response['error']}")
            return []

        content_list = response.get("result", {}).get("content", [])
        for content in content_list:
            if content.get("type") == "text":
                text = content.get("text")
                panels = json.loads(text) if isinstance(text, str) else text
                print(f"\n[*] Found {len(panels)} panels:")
                for panel in panels:
                    print(f"  - ID {panel.get('id')}: {panel.get('title')} ({panel.get('type')})")
                return panels

        return []

    async def get_panel_info(
        self,
        panel_id: int,
        dashboard_uid: Optional[str] = None,
        grafana_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> dict:
        """Get detailed information about a specific panel"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "get_panel_info",
                "arguments": {
                    "grafana_url": grafana_url or self.config["grafana_url"],
                    "api_key": api_key or self.config["api_key"],
                    "dashboard_uid": dashboard_uid or self.config["dashboard_uid"],
                    "panel_id": panel_id,
                },
            },
        }

        response = await self._send_request(request)

        if "error" in response:
            print(f"[!] Error: {response['error']}")
            return {}

        content_list = response.get("result", {}).get("content", [])
        for content in content_list:
            if content.get("type") == "text":
                text = content.get("text")
                panel_info = json.loads(text) if isinstance(text, str) else text
                print(f"\n[*] Panel {panel_id} info:")
                print(f"  Title: {panel_info.get('title', 'N/A')}")
                print(f"  Type: {panel_info.get('type', 'N/A')}")
                print(f"  Datasource: {panel_info.get('datasource', {}).get('type', 'N/A')}")
                return panel_info

        return {}

    async def query_panel_data(
        self,
        panel_id: int,
        time_from: str = "now-24h",
        time_to: str = "now",
        dashboard_uid: Optional[str] = None,
        grafana_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> dict:
        """Query data from a specific panel"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "query_panel_data",
                "arguments": {
                    "grafana_url": grafana_url or self.config["grafana_url"],
                    "api_key": api_key or self.config["api_key"],
                    "dashboard_uid": dashboard_uid or self.config["dashboard_uid"],
                    "panel_id": panel_id,
                    "time_from": time_from,
                    "time_to": time_to,
                },
            },
        }

        response = await self._send_request_large(request)

        if "error" in response:
            print(f"[!] Error: {response['error']}")
            return {}

        content_list = response.get("result", {}).get("content", [])
        for content in content_list:
            if content.get("type") == "text":
                text = content.get("text")
                data = json.loads(text) if isinstance(text, str) else text

                print(f"\n[*] Panel {panel_id} data ({time_from} to {time_to}):")

                if "error" in data:
                    print(f"  Error: {data['error']}")
                    print(f"  Message: {data.get('message', 'N/A')}")
                elif "results" in data:
                    results = data["results"]
                    print(f"  Results: {list(results.keys())}")
                    for ref_id, frame_data in results.items():
                        frames = frame_data.get('frames', [])
                        print(f"  [{ref_id}] Total frames: {len(frames)}")
                        # Show first 3 frames
                        for i, frame in enumerate(frames[:3]):
                            schema = frame.get('schema', {})
                            fields = schema.get('fields', [])
                            print(f"    Frame {i+1}: {len(fields)} fields")
                            for field in fields:
                                name = field.get('name', 'unknown')
                                type_val = field.get('type', 'unknown')
                                values = field.get('values', {})
                                if isinstance(values, list) and len(values) > 0:
                                    print(f"      - {name} ({type_val}): {len(values)} values")
                                else:
                                    print(f"      - {name} ({type_val}): buffered data")
                        if len(frames) > 3:
                            print(f"    ... and {len(frames) - 3} more frames")

                return data

        return {}

    async def get_firing_alerts(
        self,
        grafana_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> str:
        """Get all currently firing alerts"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "get_firing_alerts",
                "arguments": {
                    "grafana_url": grafana_url or self.config["grafana_url"],
                    "api_key": api_key or self.config["api_key"],
                },
            },
        }

        response = await self._send_request(request)

        if "error" in response:
            return f"Error: {response['error']}"

        content_list = response.get("result", {}).get("content", [])
        for content in content_list:
            if content.get("type") == "text":
                text = content.get("text")
                print(f"\n[*] Firing Alerts:")
                print(text)
                return text

        return "No alerts"

    async def get_alert_states(
        self,
        state: Optional[str] = None,
        folder: Optional[str] = None,
        grafana_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> str:
        """Get alert states with optional filters"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "get_alert_states",
                "arguments": {
                    "grafana_url": grafana_url or self.config["grafana_url"],
                    "api_key": api_key or self.config["api_key"],
                },
            },
        }

        # Add optional filters
        if state:
            request["params"]["arguments"]["state"] = state
        if folder:
            request["params"]["arguments"]["folder"] = folder

        response = await self._send_request(request)

        if "error" in response:
            return f"Error: {response['error']}"

        content_list = response.get("result", {}).get("content", [])
        for content in content_list:
            if content.get("type") == "text":
                text = content.get("text")
                return text

        return "No alert states"

    async def list_datasources(
        self,
        grafana_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> str:
        """List all configured datasources"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "list_datasources",
                "arguments": {
                    "grafana_url": grafana_url or self.config["grafana_url"],
                    "api_key": api_key or self.config["api_key"],
                },
            },
        }

        response = await self._send_request(request)

        if "error" in response:
            print(f"[!] Error: {response['error']}")
            return ""

        content_list = response.get("result", {}).get("content", [])
        for content in content_list:
            if content.get("type") == "text":
                text = content.get("text")
                print(f"\n[*] Datasources:")
                # Don't try to parse - it's formatted text, not JSON
                print(text)
                return text

        return ""

    async def query_elasticsearch(
        self,
        datasource_uid: str,
        query: str,
        time_from: str = "now-1h",
        time_to: str = "now",
        size: int = 100,
        grafana_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> dict:
        """Query Elasticsearch directly using Lucene query string from panel configs"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "query_elasticsearch",
                "arguments": {
                    "grafana_url": grafana_url or self.config["grafana_url"],
                    "api_key": api_key or self.config["api_key"],
                    "datasource_uid": datasource_uid,
                    "query": query,
                    "time_from": time_from,
                    "time_to": time_to,
                    "size": size,
                },
            },
        }

        response = await self._send_request_large(request)

        if "error" in response:
            print(f"[!] Error: {response['error']}")
            return {}

        # The response contains formatted text with summary + raw JSON
        content_list = response.get("result", {}).get("content", [])
        for content in content_list:
            if content.get("type") == "text":
                text = content.get("text")
                # Split by the JSON part indicator
                if "\n\n\n" in text:
                    parts = text.split("\n\n\n", 1)
                    summary = parts[0]
                    raw_json = parts[1] if len(parts) > 1 else "{}"
                    print(f"\n[*] Elasticsearch Query Results:")
                    print(summary)
                    return json.loads(raw_json)
                else:
                    print(f"\n[*] Elasticsearch Query Results:")
                    print(text)
                    return {"raw": text}

        return {}


# ============================================================================
# Test Functions
# ============================================================================

async def test_list_tools():
    """Test listing all available tools"""
    print("\n" + "=" * 60)
    print("TEST: List Tools")
    print("=" * 60)

    async with GrafanaMCPClient() as client:
        tools = await client.list_tools()
        return tools


async def test_list_dashboards(
    limit: int = 20,
    folder: Optional[str] = None,
    tag: Optional[str] = None,
):
    """Test listing dashboards"""
    print("\n" + "=" * 60)
    filter_desc = f" (limit={limit}"
    if folder:
        filter_desc += f", folder='{folder}'"
    if tag:
        filter_desc += f", tag='{tag}'"
    filter_desc += ")"
    print(f"TEST: List Dashboards{filter_desc}")
    print("=" * 60)

    async with GrafanaMCPClient() as client:
        dashboards = await client.list_dashboards(
            limit=limit,
            folder=folder,
            tag=tag,
        )
        return dashboards


async def test_get_panels():
    """Test getting dashboard panels"""
    print("\n" + "=" * 60)
    print("TEST: Get Dashboard Panels")
    print("=" * 60)

    async with GrafanaMCPClient() as client:
        panels = await client.get_dashboard_panels()
        return panels


async def test_get_panel_info(panel_id: int = 5):
    """Test getting panel information"""
    print("\n" + "=" * 60)
    print(f"TEST: Get Panel Info (panel_id={panel_id})")
    print("=" * 60)

    async with GrafanaMCPClient() as client:
        panel_info = await client.get_panel_info(panel_id)
        return panel_info


async def test_query_panel_data(panel_id: int = 5):
    """Test querying panel data"""
    print("\n" + "=" * 60)
    print(f"TEST: Query Panel Data (panel_id={panel_id})")
    print("=" * 60)

    async with GrafanaMCPClient() as client:
        data = await client.query_panel_data(panel_id)
        return data


async def test_get_alerts():
    """Test getting firing alerts"""
    print("\n" + "=" * 60)
    print("TEST: Get Firing Alerts")
    print("=" * 60)

    async with GrafanaMCPClient() as client:
        alerts = await client.get_firing_alerts()
        return alerts


async def test_list_datasources():
    """Test listing datasources"""
    print("\n" + "=" * 60)
    print("TEST: List Datasources")
    print("=" * 60)

    async with GrafanaMCPClient() as client:
        datasources = await client.list_datasources()
        return datasources


async def test_query_elasticsearch(
    datasource_uid: str = "wsnKPH4Nk",
    query: str = 'metrics.platform: "sdc"',
    time_from: str = "now-24h",
):
    """Test querying Elasticsearch directly"""
    print("\n" + "=" * 60)
    print("TEST: Query Elasticsearch Directly")
    print("=" * 60)
    print(f"Datasource UID: {datasource_uid}")
    print(f"Query: {query}")
    print(f"Time Range: {time_from} to now")
    print("=" * 60)

    async with GrafanaMCPClient() as client:
        results = await client.query_elasticsearch(
            datasource_uid=datasource_uid,
            query=query,
            time_from=time_from,
            time_to="now",
            size=10,
        )
        return results


# ============================================================================
# Main Demo
# ============================================================================

async def run_all_tests():
    """Run all tests sequentially"""
    print("\n" + "=" * 60)
    print("Grafana MCP Client - Running All Tests")
    print("=" * 60)

    await test_list_tools()
    await test_list_dashboards()
    await test_get_panels()
    await test_get_panel_info(5)
    await test_query_panel_data(6)
    await test_get_alerts()
    await test_list_datasources()


def print_usage():
    """Print usage instructions"""
    print("""
Grafana MCP Client - Usage
===========================

Usage:
    python simple_client.py [command] [args]

Commands:
    all                    Run all tests
    list-tools             List all available tools
    list-dashboards [args]  List dashboards
                           Args: [limit] [folder=name] [tag=name]
    get-panels             Get dashboard panels
    get-panel <id>         Get panel info (default: 5)
    query-data <id>        Query panel data (default: 5)
    get-alerts             Get firing alerts
    list-ds                List datasources
    query-es [args]        Query Elasticsearch directly
                           Args: [datasource_uid] [query=lucene_query] [time_from]

Examples:
    python simple_client.py all
    python simple_client.py list-dashboards
    python simple_client.py list-dashboards 50
    python simple_client.py list-dashboards folder=ipc
    python simple_client.py list-dashboards folder=ipc tag=API
    python simple_client.py get-panel 5
    python simple_client.py query-data 5
    python simple_client.py list-ds
    python simple_client.py query-es wsnKPH4Nk query='metrics.platform: "sdc"' time_from=now-24h

Custom Usage:
    from simple_client import GrafanaMCPClient

    async def my_test():
        async with GrafanaMCPClient() as client:
            # List dashboards by folder
            dashboards = await client.list_dashboards(
                limit=50,
                folder="ipc"
            )

            # List dashboards by tag
            dashboards = await client.list_dashboards(
                limit=50,
                tag="API"
            )

            # Get panels
            panels = await client.get_dashboard_panels()

            # Get specific panel info
            info = await client.get_panel_info(panel_id=5)

            # Query panel data
            data = await client.query_panel_data(
                panel_id=5,
                time_from="now-1h",
                time_to="now"
            )

            # Query Elasticsearch directly
            es_results = await client.query_elasticsearch(
                datasource_uid="wsnKPH4Nk",
                query='metrics.platform: "sdc"',
                time_from="now-24h",
                time_to="now",
                size=100
            )

    asyncio.run(my_test())
""")


# ============================================================================
# Entry Point
# ============================================================================

async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        await run_all_tests()
        return

    command = sys.argv[1]

    if command == "all":
        await run_all_tests()
    elif command == "list-tools":
        await test_list_tools()
    elif command == "list-dashboards":
        # Parse args: [limit] [folder=xxx] [tag=xxx]
        limit = 20
        folder = None
        tag = None

        for arg in sys.argv[2:]:
            if arg.startswith("folder="):
                folder = arg.split("=", 1)[1]
            elif arg.startswith("tag="):
                tag = arg.split("=", 1)[1]
            elif arg.isdigit():
                limit = int(arg)

        await test_list_dashboards(limit, folder, tag)
    elif command == "get-panels":
        await test_get_panels()
    elif command == "get-panel":
        panel_id = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        await test_get_panel_info(panel_id)
    elif command == "query-data":
        panel_id = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        await test_query_panel_data(panel_id)
    elif command == "get-alerts":
        await test_get_alerts()
    elif command == "list-ds":
        await test_list_datasources()
    elif command == "query-es":
        # Parse args: [datasource_uid] [query=xxx] [time_from=xxx]
        datasource_uid = "wsnKPH4Nk"
        query = 'metrics.platform: "sdc"'
        time_from = "now-24h"

        for arg in sys.argv[2:]:
            if arg.startswith("datasource_uid="):
                datasource_uid = arg.split("=", 1)[1]
            elif arg.startswith("query="):
                query = arg.split("=", 1)[1]
            elif arg.startswith("time_from="):
                time_from = arg.split("=", 1)[1]
            elif "=" not in arg and len(arg) > 0:
                # Positional arg: treat as datasource_uid
                datasource_uid = arg

        await test_query_elasticsearch(datasource_uid, query, time_from)
    elif command in ["-h", "--help", "help"]:
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())
