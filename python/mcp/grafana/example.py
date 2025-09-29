#!/usr/bin/env python3
"""
Example script demonstrating how to use the Grafana MCP Server
"""

import asyncio
import json
import sys
from typing import Dict, Any


async def simulate_mcp_client():
    """
    Simulate an MCP client using the Grafana server tools.
    This is a demonstration of how the tools would be called.
    """

    # Example configuration - replace with your actual Grafana details
    config = {
        "grafana_url": "https://g.dev.tuputech.com/?orgId=1",
        "api_key": "",
        "dashboard_uid": "ipc",
    }

    print("Grafana MCP Server Example")
    print("=" * 40)

    # Simulate tool calls
    examples = [
        {
            "name": "get_dashboard_panels",
            "arguments": {
                "grafana_url": config["grafana_url"],
                "api_key": config["api_key"],
                "dashboard_uid": config["dashboard_uid"],
            },
        },
        {
            "name": "get_panel_info",
            "arguments": {
                "grafana_url": config["grafana_url"],
                "api_key": config["api_key"],
                "dashboard_uid": config["dashboard_uid"],
                "panel_id": 1,
            },
        },
        {
            "name": "query_panel_data",
            "arguments": {
                "grafana_url": config["grafana_url"],
                "api_key": config["api_key"],
                "dashboard_uid": config["dashboard_uid"],
                "panel_id": 1,
                "time_from": "now-1h",
                "time_to": "now",
            },
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}: {example['name']}")
        print("-" * 30)
        print("Request:")
        print(json.dumps(example, indent=2))
        print("\nExpected Response:")

        if example["name"] == "get_dashboard_panels":
            # Simulate response for dashboard panels
            response = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            [
                                {
                                    "id": 1,
                                    "title": "CPU Usage",
                                    "type": "graph",
                                    "description": "Server CPU utilization",
                                },
                                {
                                    "id": 2,
                                    "title": "Memory Usage",
                                    "type": "graph",
                                    "description": "Server memory utilization",
                                },
                                {
                                    "id": 3,
                                    "title": "Disk I/O",
                                    "type": "graph",
                                    "description": "Disk read/write operations",
                                },
                            ],
                            indent=2,
                        ),
                    }
                ]
            }
        elif example["name"] == "get_panel_info":
            # Simulate response for panel info
            response = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "id": 1,
                                "title": "CPU Usage",
                                "type": "graph",
                                "description": "Server CPU utilization",
                                "datasource": "Prometheus",
                                "targets": [
                                    {
                                        "expr": '100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
                                        "legendFormat": "{{instance}}",
                                    }
                                ],
                                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                            },
                            indent=2,
                        ),
                    }
                ]
            }
        elif example["name"] == "query_panel_data":
            # Simulate response for panel data
            response = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "results": {
                                    "A": {
                                        "frames": [
                                            {
                                                "schema": {
                                                    "name": "cpu_usage",
                                                    "fields": [
                                                        {
                                                            "name": "Time",
                                                            "type": "time",
                                                        },
                                                        {
                                                            "name": "Value",
                                                            "type": "number",
                                                        },
                                                    ],
                                                },
                                                "data": {
                                                    "values": [
                                                        [
                                                            1640995200000,
                                                            1640995260000,
                                                            1640995320000,
                                                        ],
                                                        [45.2, 47.8, 43.1],
                                                    ]
                                                },
                                            }
                                        ]
                                    }
                                }
                            },
                            indent=2,
                        ),
                    }
                ]
            }

        print(json.dumps(response, indent=2))
        print("\n" + "=" * 50)


def print_usage():
    """Print usage instructions"""
    print(
        """
Grafana MCP Server Example Usage
================================

This script demonstrates how to use the Grafana MCP Server tools.

To use with a real MCP client:

1. Start the Grafana MCP server:
   python -m grafana.server

2. Configure your MCP client to connect to the server

3. Use the available tools:
   - list_dashboards: List available dashboards
   - get_dashboard_panels: Get all panels from a dashboard
   - get_panel_info: Get detailed information about a specific panel
   - query_panel_data: Query data from a specific panel

Example tool calls:

1. Get dashboard panels:
   {
     "name": "get_dashboard_panels",
     "arguments": {
       "grafana_url": "https://your-grafana.com",
       "api_key": "your-api-key",
       "dashboard_uid": "your-dashboard-uid"
     }
   }

2. Get panel info:
   {
     "name": "get_panel_info",
     "arguments": {
       "grafana_url": "https://your-grafana.com",
       "api_key": "your-api-key",
       "dashboard_uid": "your-dashboard-uid",
       "panel_id": 1
     }
   }

3. Query panel data:
   {
     "name": "query_panel_data",
     "arguments": {
       "grafana_url": "https://your-grafana.com",
       "api_key": "your-api-key",
       "dashboard_uid": "your-dashboard-uid",
       "panel_id": 1,
       "time_from": "now-1h",
       "time_to": "now"
     }
   }

Note: Replace the example values with your actual Grafana details.
"""
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print_usage()
    else:
        asyncio.run(simulate_mcp_client())
