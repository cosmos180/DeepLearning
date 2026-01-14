# Grafana MCP Server

This MCP (Model Context Protocol) server provides tools to interact with Grafana, including dashboard panel reading and alert monitoring.

## Features

### Dashboard & Panel Operations
- List available Grafana dashboards
- Get all panels from a specific dashboard
- Get detailed information about a specific panel
- Query data from a specific panel

### Alert Monitoring
- Get currently firing alerts
- Get alert states with filters (by folder, state)
- List all configured alert rules
- Get notification history
- List all datasources (for Kibana/Elasticsearch integration)
- Query datasources directly

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Or install the package:
```bash
pip install -e .
```

## Usage

### Running the Server

The server can be run using stdio transport:

```bash
python -m grafana.server
```

Or using the installed command:
```bash
grafana-mcp-server
```

### Available Tools

#### 1. list_dashboards
List available Grafana dashboards.

**Parameters:**
- `grafana_url` (required): Grafana server URL
- `api_key` (optional): Grafana API key

**Example:**
```json
{
  "name": "list_dashboards",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key"
  }
}
```

#### 2. get_dashboard_panels
Get all panels from a specific dashboard.

**Parameters:**
- `grafana_url` (required): Grafana server URL
- `api_key` (optional): Grafana API key
- `dashboard_uid` (required): Dashboard UID

**Example:**
```json
{
  "name": "get_dashboard_panels",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key",
    "dashboard_uid": "your-dashboard-uid"
  }
}
```

#### 3. get_panel_info
Get detailed information about a specific panel.

**Parameters:**
- `grafana_url` (required): Grafana server URL
- `api_key` (optional): Grafana API key
- `dashboard_uid` (required): Dashboard UID
- `panel_id` (required): Panel ID

**Example:**
```json
{
  "name": "get_panel_info",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key",
    "dashboard_uid": "your-dashboard-uid",
    "panel_id": 1
  }
}
```

#### 4. query_panel_data
Query data from a specific panel.

**Parameters:**
- `grafana_url` (required): Grafana server URL
- `api_key` (optional): Grafana API key
- `dashboard_uid` (required): Dashboard UID
- `panel_id` (required): Panel ID
- `time_from` (optional): Start time (e.g., "now-1h")
- `time_to` (optional): End time (e.g., "now")

**Example:**
```json
{
  "name": "query_panel_data",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key",
    "dashboard_uid": "your-dashboard-uid",
    "panel_id": 1,
    "time_from": "now-1h",
    "time_to": "now"
  }
}
```

---

## Alert Tools

### 5. get_firing_alerts
Get all currently firing alerts that need attention. This is the most commonly used tool for alert monitoring.

**Parameters:**
- `grafana_url` (required): Grafana server URL
- `api_key` (optional): Grafana API key

**Example:**
```json
{
  "name": "get_firing_alerts",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key"
  }
}
```

**Response Example:**
```
🚨 2 Firing Alert(s):

• [Production] High CPU Usage
  State: FIRING
  URL: https://grafana.example.com/alert/123

• [Production] Disk Space Low
  State: FIRING
  URL: https://grafana.example.com/alert/456
```

### 6. get_alert_states
Get alert states with optional filters by folder or state (firing, pending, normal, no_data).

**Parameters:**
- `grafana_url` (required): Grafana server URL
- `api_key` (optional): Grafana API key
- `folder` (optional): Filter by folder name (e.g., "Production")
- `state` (optional): Filter by state: "firing", "pending", "normal", "no_data"

**Example:**
```json
{
  "name": "get_alert_states",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key",
    "folder": "Production",
    "state": "firing"
  }
}
```

**Example - Get all alerts in a folder:**
```json
{
  "name": "get_alert_states",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key",
    "folder": "Production"
  }
}
```

### 7. get_alert_rules
List all configured alert rules.

**Parameters:**
- `grafana_url` (required): Grafana server URL
- `api_key` (optional): Grafana API key

**Example:**
```json
{
  "name": "get_alert_rules",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key"
  }
}
```

### 8. get_notification_history
Get notification history (past alert firings).

**Parameters:**
- `grafana_url` (required): Grafana server URL
- `api_key` (optional): Grafana API key
- `limit` (optional): Maximum number of notifications to return (default: 100)

**Example:**
```json
{
  "name": "get_notification_history",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key",
    "limit": 50
  }
}
```

### 9. list_datasources
List all configured datasources. Useful for finding the UID of Kibana/Elasticsearch datasources.

**Parameters:**
- `grafana_url` (required): Grafana server URL
- `api_key` (optional): Grafana API key

**Example:**
```json
{
  "name": "list_datasources",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key"
  }
}
```

**Response Example:**
```
🔌 Datasources (3 total):

• Prometheus
  Type: prometheus
  UID: prometheus-main
  URL: http://localhost:9090

• Kibana
  Type: elasticsearch
  UID: kibana-main
  URL: http://localhost:5601

• Grafana
  Type: grafana
  UID: grafana-main
  URL: http://localhost:3000
```

### 10. query_datasource
Query a datasource directly. Useful for querying Kibana/Elasticsearch with custom queries.

**Parameters:**
- `grafana_url` (required): Grafana server URL
- `api_key` (optional): Grafana API key
- `datasource_uid` (required): The UID of the datasource to query
- `query` (required): Query payload for the datasource (JSON object)
- `time_from` (optional): Start time (e.g., "now-1h")
- `time_to` (optional): End time (e.g., "now")

**Example:**
```json
{
  "name": "query_datasource",
  "arguments": {
    "grafana_url": "https://grafana.example.com",
    "api_key": "your-api-key",
    "datasource_uid": "kibana-main",
    "query": {
      "queryType": "logs",
      "expr": "status:500"
    },
    "time_from": "now-1h",
    "time_to": "now"
  }
}
```

## Configuration

### Grafana API Key

To use this server, you need a Grafana API key with appropriate permissions. You can create one in Grafana:

1. Go to Configuration → API Keys
2. Click "Add API key"
3. Give it a name and select the appropriate role (Editor or Viewer)
4. Copy the generated key

### How to Find Dashboard UID

To get the dashboard UID, you have several options:

#### Method 1: From Grafana Web Interface
1. Open your dashboard in Grafana
2. Look at the URL in your browser's address bar
3. The UID is the part after `/d/` in the URL
   - Example: `https://grafana.example.com/d/your-dashboard-uid/dashboard-name`
   - In this case, `your-dashboard-uid` is the dashboard UID

#### Method 2: From Dashboard Settings
1. Open your dashboard in Grafana
2. Click the gear icon (Settings) in the top menu
3. The dashboard UID is displayed in the "General" section
4. You can also find it under "JSON Model" as `uid`

#### Method 3: Using the API
You can get a list of all dashboards and their UIDs using the Grafana API:
```bash
curl -H "Authorization: Bearer your-api-key" \
     https://grafana.example.com/api/search?type=dash-db
```

#### Method 4: From Dashboard JSON
1. Open your dashboard in Grafana
2. Click Share → Export → Save to file
3. Open the JSON file and look for the `uid` field

### Permissions

The API key needs at least the following permissions:

#### For Dashboard Operations:
- `dashboards:read` - to read dashboards and panels
- `datasources:query` - to query panel data (if using query_panel_data)

#### For Alert Monitoring:
- `alert.rules:read` - to read alert rules and states
- `alert.provisioning:read` - to access provisioning API for alert rules
- `notifications:read` - to read notification history (optional)
- `datasources:read` - to list datasources

## Example Usage with MCP Client

Here's an example of how to use the server with an MCP client:

```python
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client() as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:", tools)

            # Get dashboard panels
            result = await session.call_tool(
                "get_dashboard_panels",
                {
                    "grafana_url": "https://grafana.example.com",
                    "api_key": "your-api-key",
                    "dashboard_uid": "your-dashboard-uid"
                }
            )
            print("Dashboard panels:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Alert Monitoring Example

Here's an example of using the alert monitoring tools:

```python
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def monitor_alerts():
    async with stdio_client() as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Check for firing alerts
            result = await session.call_tool(
                "get_firing_alerts",
                {
                    "grafana_url": "https://grafana.example.com",
                    "api_key": "your-api-key"
                }
            )

            # Process the result
            if "No firing alerts" in result.content[0].text:
                print("All systems normal!")
            else:
                print(f"Alerts detected: {result.content[0].text}")

            # Get detailed alert states for a specific folder
            result = await session.call_tool(
                "get_alert_states",
                {
                    "grafana_url": "https://grafana.example.com",
                    "api_key": "your-api-key",
                    "folder": "Production",
                    "state": "firing"
                }
            )
            print(f"Production alerts: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(monitor_alerts())
```

## Error Handling

The server returns appropriate error messages for:
- Missing required parameters
- Invalid dashboard UID or panel ID
- Network connectivity issues
- Authentication failures
- Grafana API errors

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

### Code Style

The project follows PEP 8 style guidelines. You can check the code style using:

```bash
flake8 grafana/
black --check grafana/
```

## License

This project is licensed under the MIT License.
