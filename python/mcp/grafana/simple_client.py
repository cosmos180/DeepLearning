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
from typing import Any, Optional, List
from datetime import datetime


# ============================================================================
# Data Formatting Utilities
# ============================================================================

class DataFormatter:
    """Format Grafana query results for human-readable display"""

    @staticmethod
    def format_frame_data(data: dict, panel_type: str = "unknown", filter_zero_values: bool = False, min_value_threshold: float = 0) -> str:
        """
        Format frame data from Grafana query into readable output
        Similar to what's displayed in Grafana web interface

        Args:
            data: The query result data
            panel_type: The type of panel (timeseries, table, etc.)
            filter_zero_values: If True, filter out frames with all zero/null values
            min_value_threshold: Minimum value threshold for filtering (only show frames with max >= this)
        """
        if not data or "results" not in data:
            return DataFormatter._format_error("No data available")

        results = data["results"]
        output_parts = []

        for ref_id, frame_data in results.items():
            frames = frame_data.get('frames', [])

            if not frames:
                output_parts.append(f"[{ref_id}] No frames available")
                continue

            for frame_idx, frame in enumerate(frames):
                schema = frame.get('schema', {})
                fields = schema.get('fields', [])
                frame_data_values = frame.get('data', {}).get('values', [])

                # Check if this frame has meaningful data (for filtering)
                if filter_zero_values and not DataFormatter._has_meaningful_data(fields, frame_data_values, min_value_threshold):
                    continue  # Skip frames with no meaningful data

                # Generate a descriptive frame name
                # Try to get a name from the value fields' labels or displayNameFromDS
                frame_name_parts = []
                for field in fields:
                    if field.get('type') != 'time':
                        display_name = field.get('config', {}).get('displayNameFromDS')
                        if display_name:
                            frame_name_parts.append(display_name)
                        labels = field.get('labels', {})
                        if labels and 'deviceId.keyword' in labels:
                            frame_name_parts.append(f"Device: {labels['deviceId.keyword']}")
                        if labels and 'deviceId' in labels:
                            frame_name_parts.append(f"Device: {labels['deviceId']}")

                if frame_name_parts:
                    # Use first unique part as frame name
                    unique_parts = list(dict.fromkeys(frame_name_parts))  # Preserve order, remove duplicates
                    frame_name = f"Frame {frame_idx + 1}: " + " | ".join(unique_parts[:2])  # Max 2 parts
                else:
                    frame_name = schema.get('name', f'Frame {frame_idx + 1}')

                # Attach the frame data values to fields for easier access
                for field_idx, field in enumerate(fields):
                    # Store the field's index and parent frame data for value extraction
                    field['_frame_data'] = frame_data_values
                    field['_field_index'] = field_idx

                # Determine the best display format based on panel type and data
                # Panel type takes priority over data structure detection
                if panel_type in ["timeseries", "graph", "gauge"]:
                    formatted = DataFormatter._format_as_timeseries(fields, frame_name)
                elif panel_type in ["table", "logs"]:
                    formatted = DataFormatter._format_as_table(fields, frame_name)
                elif panel_type in ["stat", "singlestat"]:
                    formatted = DataFormatter._format_as_stat(fields, frame_name)
                elif DataFormatter._is_tabular_data(fields):
                    # If panel type is unknown but data looks tabular
                    formatted = DataFormatter._format_as_table(fields, frame_name)
                else:
                    formatted = DataFormatter._format_as_generic(fields, frame_name)

                output_parts.append(formatted)

        if not output_parts:
            return DataFormatter._format_error("No data available after filtering")

        return "\n\n".join(output_parts)

    @staticmethod
    def _is_tabular_data(fields: List[dict]) -> bool:
        """Check if data is better displayed as a table"""
        if len(fields) < 2:
            return False
        # Table data typically has multiple fields with similar value counts
        value_counts = [len(DataFormatter._get_values(f)) for f in fields]
        return len(set(value_counts)) <= 1 and value_counts[0] > 1

    @staticmethod
    def _has_meaningful_data(fields: List[dict], frame_data_values: list, min_threshold: float = 0) -> bool:
        """
        Check if a frame has meaningful data (not all zeros/nulls)
        This is used to filter out devices with no activity

        Args:
            fields: List of field definitions
            frame_data_values: The data values for the frame
            min_threshold: Minimum max value for considering data as meaningful
        """
        for field_idx, field in enumerate(fields):
            if field.get('type') == 'time':
                continue  # Skip time fields

            # Get values for this field
            if field_idx < len(frame_data_values):
                values = frame_data_values[field_idx]
                if isinstance(values, list):
                    # Check if max value >= threshold
                    numeric_values = [v for v in values if isinstance(v, (int, float)) and v is not None]
                    if numeric_values:
                        max_val = max(numeric_values)
                        if max_val >= min_threshold:
                            return True  # Found meaningful data above threshold

        return False  # No meaningful data found

    @staticmethod
    def _get_values(field: dict) -> list:
        """
        Extract values from a field, handling Grafana's frame data format

        Grafana frame format:
        {
            "schema": {
                "fields": [
                    {"name": "time", "type": "time"},
                    {"name": "value", "type": "number"}
                ]
            },
            "data": {
                "values": [
                    [time_values...],   // Array for field 0
                    [value_values...]   // Array for field 1
                ]
            }
        }
        """
        # First check if we have attached frame data (from format_frame_data)
        if '_frame_data' in field and '_field_index' in field:
            frame_data = field['_frame_data']
            field_index = field['_field_index']

            if isinstance(frame_data, list) and field_index < len(frame_data):
                values = frame_data[field_index]
                return values if isinstance(values, list) else []

        # Legacy format: check for direct 'values' key in field
        values = field.get('values', [])

        if isinstance(values, list):
            return values
        elif isinstance(values, dict):
            # Handle buffered data format
            # Check for keys that look like numeric indices ("0", "1", etc.)
            numeric_keys = [k for k in values.keys() if k.isdigit()]
            if numeric_keys:
                # Buffered format with numeric keys - concatenate all values
                all_values = []
                for key in sorted(numeric_keys, key=int):
                    val_list = values[key]
                    if isinstance(val_list, list):
                        all_values.extend(val_list)
                return all_values
            else:
                # Dict format - try to extract values
                return list(values.values()) if values else []
        else:
            return []

    @staticmethod
    def _format_as_table(fields: List[dict], frame_name: str) -> str:
        """Format data as a table (similar to Grafana table panel)"""
        lines = [f"📊 {frame_name}", "=" * 80]

        # Get column headers with better names
        headers = []
        for f in fields:
            # Prefer displayNameFromDS, then fall back to field name
            display_name = f.get('config', {}).get('displayNameFromDS')
            if not display_name:
                # Add labels if available
                labels = f.get('labels', {})
                if labels:
                    label_str = ", ".join([f"{k}={v}" for k, v in labels.items()])
                    display_name = f"{f.get('name', 'unknown')} ({label_str})"
                else:
                    display_name = f.get('name', 'unknown')
            headers.append(display_name)

        # Calculate column widths based on content
        col_widths = []
        for i, field in enumerate(fields):
            values = DataFormatter._get_values(field)
            # Width is max of header length and sample values
            header_len = len(headers[i])
            max_val_len = 0
            for val in values[:10]:  # Sample first 10 values
                val_str = str(val) if val is not None else "null"
                max_val_len = max(max_val_len, len(val_str))
            col_widths.append(max(header_len, max_val_len, 10))  # Minimum 10 chars

        # Print headers
        header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
        lines.append(header_line)
        lines.append("-" * len(header_line))

        # Get row count from first field
        first_field_values = DataFormatter._get_values(fields[0])
        row_count = min(len(first_field_values), 20)  # Limit to 20 rows for readability

        # Extract rows
        for row_idx in range(row_count):
            row_values = []
            for i, field in enumerate(fields):
                values = DataFormatter._get_values(field)
                if row_idx < len(values):
                    val = values[row_idx]
                    # Format value based on type
                    if val is None:
                        display_val = "null"
                    elif isinstance(val, float):
                        display_val = f"{val:.4f}"
                    elif isinstance(val, bool):
                        display_val = str(val)
                    elif isinstance(val, (int, float)):
                        display_val = str(val)
                    else:
                        display_val = str(val)[:50]  # Truncate long strings
                    row_values.append(display_val)
                else:
                    row_values.append("")
            lines.append(" | ".join(f"{row_values[i]:<{col_widths[i]}}" for i in range(len(row_values))))

        if row_count == 20 and len(first_field_values) > 20:
            lines.append(f"... ({len(first_field_values) - 20} more rows)")

        return "\n".join(lines)

    @staticmethod
    def _format_as_timeseries(fields: List[dict], frame_name: str) -> str:
        """Format data as time series (similar to Grafana graph panel)"""
        lines = [f"📈 {frame_name}", "=" * 80]

        # Find time field
        time_field = None
        value_fields = []

        for field in fields:
            if field.get('name') == 'Time' or field.get('type') == 'time':
                time_field = field
            else:
                value_fields.append(field)

        if not time_field and value_fields:
            time_field = fields[0]  # Use first field as time if no explicit time field

        if not value_fields:
            return lines[0] + "\n" + "No value fields found"

        time_values = DataFormatter._get_values(time_field) if time_field else list(range(len(DataFormatter._get_values(value_fields[0]))))

        for vfield in value_fields:
            # Get display name: prefer displayNameFromDS, then labels, then field name
            display_name = vfield.get('config', {}).get('displayNameFromDS')
            if not display_name:
                # Try to get from labels
                labels = vfield.get('labels', {})
                if labels:
                    label_parts = [f"{k}={v}" for k, v in labels.items()]
                    display_name = vfield.get('name', 'unknown') + " [" + ", ".join(label_parts) + "]"
                else:
                    display_name = vfield.get('name', 'unknown')

            values = DataFormatter._get_values(vfield)

            if not values:
                continue

            lines.append(f"\n📌 {display_name}")
            lines.append(f"   Data points: {len(values)}")

            # Show statistics
            numeric_values = [v for v in values if isinstance(v, (int, float)) and v is not None]
            if numeric_values:
                lines.append(f"   Min: {min(numeric_values):.4f}")
                lines.append(f"   Max: {max(numeric_values):.4f}")
                lines.append(f"   Avg: {sum(numeric_values)/len(numeric_values):.4f}")
                lines.append(f"   Latest: {numeric_values[-1]:.4f}")

            # Show sample data points
            sample_count = min(5, len(values))
            lines.append(f"\n   Sample data points:")
            for i in range(sample_count):
                idx = i * (len(values) // sample_count) if len(values) > sample_count else i
                time_val = time_values[idx] if idx < len(time_values) else None
                val = values[idx] if idx < len(values) else None

                # Format time if it's a Unix timestamp (milliseconds)
                time_str = "N/A"
                if isinstance(time_val, (int, float)):
                    try:
                        # Grafana uses milliseconds timestamp
                        if time_val > 1000000000000:  # milliseconds
                            time_str = datetime.fromtimestamp(time_val / 1000).strftime("%Y-%m-%d %H:%M:%S")
                        else:  # seconds
                            time_str = datetime.fromtimestamp(time_val).strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        time_str = str(time_val)
                else:
                    time_str = str(time_val)[:20]

                # Format value
                val_str = f"{val:.4f}" if isinstance(val, (int, float)) else str(val)
                lines.append(f"   {time_str} → {val_str}")

        return "\n".join(lines)

    @staticmethod
    def _format_as_stat(fields: List[dict], frame_name: str) -> str:
        """Format data as a single stat value (similar to Grafana stat panel)"""
        lines = [f"🔢 {frame_name}", "=" * 80]

        for field in fields:
            name = field.get('name', 'unknown')
            values = DataFormatter._get_values(field)

            if not values:
                continue

            # For stat panels, usually show the latest or first value
            latest_val = values[-1] if values else None
            first_val = values[0] if values else None

            lines.append(f"\n📌 {name}")
            if latest_val is not None:
                lines.append(f"   Current: {latest_val}")
            if first_val is not None and first_val != latest_val:
                lines.append(f"   First: {first_val}")

            # Show stats for numeric values
            if values and isinstance(values[0], (int, float)):
                numeric_values = [v for v in values if isinstance(v, (int, float))]
                if numeric_values:
                    lines.append(f"   Min: {min(numeric_values):.4f}")
                    lines.append(f"   Max: {max(numeric_values):.4f}")
                    lines.append(f"   Avg: {sum(numeric_values)/len(numeric_values):.4f}")

        return "\n".join(lines)

    @staticmethod
    def _format_as_generic(fields: List[dict], frame_name: str) -> str:
        """Format data in generic format"""
        lines = [f"📋 {frame_name}", "=" * 80]

        for field in fields:
            name = field.get('name', 'unknown')
            field_type = field.get('type', 'unknown')
            values = DataFormatter._get_values(field)

            lines.append(f"\n📌 {name} ({field_type})")
            lines.append(f"   Total values: {len(values)}")

            # Show first few values
            sample_count = min(3, len(values))
            if sample_count > 0:
                lines.append(f"   Sample values: {values[:sample_count]}")

        return "\n".join(lines)

    @staticmethod
    def _format_error(message: str) -> str:
        """Format error message"""
        return f"❌ Error: {message}"


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
        # Note: Capabilities may be reported empty until initialized notification is sent
        capabilities = response.get('result', {}).get('capabilities')

        # Send initialized notification (required by MCP protocol)
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        await self._send_notification(initialized_notif)

        # Print after initialized notification is sent
        print(f"[*] Server capabilities (from initialize): {capabilities}")
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
                    print(f"  - ID {panel.get('id')}: {panel.get('title')} ({panel.get('type')}) [Dashboard: {dashboard_uid or self.config.get('dashboard_uid', 'N/A')}]")
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
        panel_type: str = "unknown",
        filter_zero: bool = False,
    ) -> dict:
        """
        Query data from a specific panel

        Args:
            panel_id: The ID of the panel to query
            time_from: Start time (e.g., 'now-24h')
            time_to: End time (e.g., 'now')
            dashboard_uid: Dashboard UID (optional, uses default if not specified)
            grafana_url: Grafana server URL
            api_key: API key for authentication
            panel_type: Type of panel (for formatting)
            filter_zero: If True, filter out devices with all zero/null values
                        (Useful for crash/error panels to show only devices with issues)
        """
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
                if filter_zero:
                    print("    (Filtering: showing only devices with non-zero values)")

                if "error" in data:
                    print(f"  Error: {data['error']}")
                    print(f"  Message: {data.get('message', 'N/A')}")
                elif "results" in data:
                    # DEBUG: Print raw data structure to understand the format
                    import os
                    if os.getenv('DEBUG_RAW_DATA'):
                        print("\n=== RAW DATA (DEBUG) ===")
                        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
                        print("=== END RAW DATA ===\n")

                    # Use DataFormatter for better display
                    formatted_output = DataFormatter.format_frame_data(data, panel_type, filter_zero_values=filter_zero)
                    print(formatted_output)
                else:
                    # Raw data output
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")

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
        # First get panel info to determine panel type
        panel_info = await client.get_panel_info(panel_id)
        panel_type = panel_info.get('type', 'unknown') if panel_info else 'unknown'

        # Then query data with proper panel type
        data = await client.query_panel_data(panel_id, panel_type=panel_type)
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


async def interactive_explorer(
    folder: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 50,
    time_from: str = "now-24h",
    time_to: str = "now",
):
    """
    Interactive Grafana Dashboard Explorer

    Flow:
    1. List dashboards and let user select one
    2. List panels of selected dashboard and let user select one
    3. Query and display data for selected panel
    """
    print("\n" + "=" * 70)
    print("Grafana Interactive Dashboard Explorer")
    print("=" * 70)

    async with GrafanaMCPClient() as client:
        # ========================================================================
        # Step 1: List dashboards and select one
        # ========================================================================

        filter_desc = []
        if folder:
            filter_desc.append(f"folder='{folder}'")
        if tag:
            filter_desc.append(f"tag='{tag}'")

        print(f"\n📋 Step 1: Fetching Dashboards (limit={limit}" +
              (f", {', '.join(filter_desc)}" if filter_desc else "") + ")")

        # We need to actually parse the dashboard list
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "list_dashboards",
                "arguments": {
                    "grafana_url": client.config["grafana_url"],
                    "api_key": client.config["api_key"],
                    "limit": limit,
                },
            },
        }

        if folder:
            request["params"]["arguments"]["folder"] = folder
        if tag:
            request["params"]["arguments"]["tag"] = tag

        response = await client._send_request(request)

        if "error" in response:
            print(f"❌ Error fetching dashboards: {response['error']}")
            return

        # Parse dashboard list from formatted text
        content_list = response.get("result", {}).get("content", [])
        dashboards_text = ""
        for content in content_list:
            if content.get("type") == "text":
                dashboards_text = content.get("text", "")
                break

        if "No dashboards found" in dashboards_text or not dashboards_text:
            print("❌ No dashboards found")
            return

        # Extract dashboard info from formatted text
        import re
        dashboard_pattern = r'• (.+?)\n  UID: (.+?)\n  Folder: (.+?)(?:\n  Tags: (.+?))?\n  URL: (.+?)\n\n'
        dashboards = []
        for match in re.finditer(dashboard_pattern, dashboards_text, re.MULTILINE):
            dashboards.append({
                "title": match.group(1).strip(),
                "uid": match.group(2).strip(),
                "folder": match.group(3).strip(),
                "tags": match.group(4).strip() if match.group(4) else "",
                "url": match.group(5).strip(),
            })

        if not dashboards:
            print("❌ Could not parse dashboard list")
            return

        print(f"\n✅ Found {len(dashboards)} dashboards:\n")
        for i, dash in enumerate(dashboards, 1):
            tags_str = f" [Tags: {dash['tags']}]" if dash['tags'] else ""
            print(f"  [{i}] {dash['title']}")
            print(f"      UID: {dash['uid']} | Folder: {dash['folder']}{tags_str}")

        # Get user selection
        while True:
            try:
                user_input = input(f"\n👉 Select dashboard [1-{len(dashboards)}] (or 'q' to quit): ").strip()
                if user_input.lower() == 'q':
                    print("\n👋 Exiting explorer")
                    return

                selection = int(user_input) - 1
                if 0 <= selection < len(dashboards):
                    break
                print(f"❌ Please enter a number between 1 and {len(dashboards)}")
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Exiting explorer")
                return
            except EOFError:
                # Handle non-interactive mode
                print("\n⚠️  Non-interactive mode detected. Please select a dashboard using command-line args.")
                return

        selected_dashboard = dashboards[selection]
        dashboard_uid = selected_dashboard["uid"]
        print(f"\n✅ Selected: {selected_dashboard['title']} (UID: {dashboard_uid})")

        # ========================================================================
        # Step 2: List panels and select one
        # ========================================================================

        print(f"\n📊 Step 2: Fetching Panels from dashboard")

        panels = await client.get_dashboard_panels(dashboard_uid=dashboard_uid)

        if not panels:
            print("❌ No panels found in this dashboard")
            return

        print(f"\n✅ Found {len(panels)} panels:\n")
        for i, panel in enumerate(panels, 1):
            panel_type = panel.get('type', 'unknown')
            panel_title = panel.get('title', 'Untitled')
            print(f"  [{i}] ID: {panel.get('id')} | {panel_title} ({panel_type}) [Dashboard: {dashboard_uid}]")

        # Get user selection
        while True:
            try:
                user_input = input(f"\n👉 Select panel [1-{len(panels)}] (or 'q' to quit): ").strip()
                if user_input.lower() == 'q':
                    print("\n👋 Exiting explorer")
                    return

                selection = int(user_input) - 1
                if 0 <= selection < len(panels):
                    break
                print(f"❌ Please enter a number between 1 and {len(panels)}")
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Exiting explorer")
                return
            except EOFError:
                print("\n⚠️  Non-interactive mode detected.")
                return

        selected_panel = panels[selection]
        panel_id = selected_panel['id']
        panel_title = selected_panel.get('title', 'Untitled')
        panel_type = selected_panel.get('type', 'unknown')
        print(f"\n✅ Selected: {panel_title} (ID: {panel_id})")

        # ========================================================================
        # Step 3: Select time range
        # ========================================================================

        print(f"\n⏰ Step 3: Select Time Range")
        print("\nCommon time ranges:")
        print("  [1]  Last 1 hour  (now-1h)")
        print("  [2]  Last 6 hours (now-6h)")
        print("  [3]  Last 12 hours (now-12h)")
        print("  [4]  Last 24 hours (now-24h) [default]")
        print("  [5]  Last 7 days   (now-7d)")
        print("  [6]  Custom time range")

        time_ranges = {
            '1': ('now-1h', 'Last 1 hour'),
            '2': ('now-6h', 'Last 6 hours'),
            '3': ('now-12h', 'Last 12 hours'),
            '4': ('now-24h', 'Last 24 hours'),
            '5': ('now-7d', 'Last 7 days'),
        }

        selected_time_from = time_from
        selected_time_to = time_to

        while True:
            try:
                user_input = input(f"\n👉 Select time range [1-6] (default: 4, or 'q' to quit): ").strip()
                if user_input.lower() == 'q':
                    print("\n👋 Exiting explorer")
                    return
                elif user_input == '':
                    user_input = '4'  # Default to 24h

                if user_input in time_ranges:
                    selected_time_from, desc = time_ranges[user_input]
                    print(f"   Selected: {desc}")
                    break
                elif user_input == '6':
                    # Custom time range
                    custom_time_from = input("   Enter time_from (e.g., 'now-1h', '2024-01-01 00:00:00'): ").strip()
                    custom_time_to = input("   Enter time_to (e.g., 'now', '2024-01-02 00:00:00'): ").strip() or "now"
                    selected_time_from = custom_time_from
                    selected_time_to = custom_time_to
                    print(f"   Custom range: {selected_time_from} to {selected_time_to}")
                    break
                else:
                    print(f"   ❌ Please enter a number between 1 and 6")
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Exiting explorer")
                return
            except EOFError:
                print("\n⚠️  Non-interactive mode detected. Using default time range.")
                break

        # ========================================================================
        # Step 4: Optional filter for crash/error panels
        # ========================================================================

        filter_zero = False
        panel_lower = panel_title.lower()
        is_crash_panel = any(keyword in panel_lower for keyword in ['crash', 'error', 'fail', 'deadlock'])

        if is_crash_panel:
            print(f"\n🔧 Step 4: Filter Options (detected crash/error panel)")
            print("   This panel appears to track crashes/errors. Filter options:")
            print("   [1] Show all devices (default)")
            print("   [2] Show only devices with crashes (> 0)")

            while True:
                try:
                    user_input = input(f"\n👉 Select filter option [1-2] (default: 1): ").strip()
                    if user_input == '':
                        user_input = '1'
                    if user_input == '1':
                        print("   Showing all devices")
                        break
                    elif user_input == '2':
                        filter_zero = True
                        print("   Filtering: will show only devices with crash counts > 0")
                        break
                    else:
                        print("   ❌ Please enter 1 or 2")
                except (ValueError, KeyboardInterrupt):
                    print("   Showing all devices (default)")
                    break
                except EOFError:
                    print("\n⚠️  Non-interactive mode detected. Showing all devices.")
                    break

        # ========================================================================
        # Step 5: Query panel data
        # ========================================================================

        step_num = 5 if is_crash_panel else 4
        print(f"\n📈 Step {step_num}: Querying Panel Data")
        print(f"   Panel: {panel_title}")
        print(f"   Type: {panel_type}")
        print(f"   Time Range: {selected_time_from} to {selected_time_to}")
        if filter_zero:
            print(f"   Filter: Enabled (only devices with crashes)")

        data = await client.query_panel_data(
            panel_id=panel_id,
            dashboard_uid=dashboard_uid,
            time_from=selected_time_from,
            time_to=selected_time_to,
            panel_type=panel_type,
            filter_zero=filter_zero,
        )

        if not data:
            print("❌ No data returned")
            return

        # Results are already formatted and displayed by query_panel_data
        print("\n" + "=" * 70)
        print("✅ Exploration complete!")
        print("=" * 70)


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
    explore [args]         Interactive dashboard explorer
                           Args: [limit] [folder=name] [tag=name] [time_from] [time_to]
                           Flow: Select dashboard -> Select panel -> View data
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
    python simple_client.py explore
    python simple_client.py explore folder=ipc limit=100
    python simple_client.py explore folder=ipc time_from=now-7d
    python simple_client.py list-dashboards
    python simple_client.py list-dashboards 50
    python simple_client.py list-dashboards folder=ipc
    python simple_client.py list-dashboards folder=ipc tag=API
    python simple_client.py get-panel 5
    python simple_client.py query-data 5
    python simple_client.py list-ds
    python simple_client.py query-es wsnKPH4Nk query='metrics.platform: "sdc"' time_from=now-24h

Interactive Explorer Usage:
    The 'explore' command provides an interactive workflow:
    1. Lists dashboards and prompts you to select one by number
    2. Lists panels from selected dashboard and prompts you to select one
    3. Select time range from presets or custom range
    4. (For crash/error panels) Choose to filter devices with issues
    5. Queries and displays data for the selected panel

    Time range options:
    - [1] Last 1 hour  (now-1h)
    - [2] Last 6 hours (now-6h)
    - [3] Last 12 hours (now-12h)
    - [4] Last 24 hours (now-24h) [default]
    - [5] Last 7 days   (now-7d)
    - [6] Custom time range

    Optional filters for explore:
    - limit=50           : Maximum dashboards to list (default: 50)
    - folder=ipc         : Filter dashboards by folder name
    - tag=API            : Filter dashboards by tag

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
    elif command == "explore":
        # Parse args: [limit] [folder=xxx] [tag=xxx] [time_from=xxx] [time_to=xxx]
        limit = 50
        folder = None
        tag = None
        time_from = "now-24h"
        time_to = "now"

        for arg in sys.argv[2:]:
            if arg.startswith("folder="):
                folder = arg.split("=", 1)[1]
            elif arg.startswith("tag="):
                tag = arg.split("=", 1)[1]
            elif arg.startswith("time_from="):
                time_from = arg.split("=", 1)[1]
            elif arg.startswith("time_to="):
                time_to = arg.split("=", 1)[1]
            elif arg.startswith("limit="):
                limit = int(arg.split("=", 1)[1])
            elif arg.isdigit():
                limit = int(arg)

        await interactive_explorer(
            folder=folder,
            tag=tag,
            limit=limit,
            time_from=time_from,
            time_to=time_to,
        )
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
