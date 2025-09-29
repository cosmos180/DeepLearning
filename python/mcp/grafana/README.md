# Grafana MCP Server

This MCP (Model Context Protocol) server provides tools to read panels from specified Grafana dashboards.

## Features

- List available Grafana dashboards
- Get all panels from a specific dashboard
- Get detailed information about a specific panel
- Query data from a specific panel

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
- `dashboards:read` - to read dashboards and panels
- `datasources:query` - to query panel data (if using query_panel_data)

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
