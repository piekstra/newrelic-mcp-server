# New Relic MCP Server

A Model Context Protocol (MCP) server that provides programmatic access to New Relic APIs, enabling AI assistants and other tools to interact with New Relic monitoring and observability data.

## Features

- **APM Application Management**: List and retrieve application details, metrics, and metric data
- **NRQL Queries**: Execute NRQL queries via NerdGraph
- **Log Parsing Rules**: Intelligently create, manage, and test GROK patterns for log parsing
- **Alert Policies**: List and manage alert policies
- **Synthetic Monitoring**: Access synthetic monitor information
- **Dashboards**: List and retrieve dashboard configurations
- **Entity Search**: Search across all New Relic entities
- **Infrastructure**: Monitor servers and infrastructure components
- **Deployments**: Track and create application deployments
- **User Management**: List and manage users
- **NerdGraph**: Execute custom GraphQL queries

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install newrelic-mcp-server
```

### Option 2: Install from Source

```bash
# Clone this repository
git clone https://github.com/piekstra/newrelic-mcp-server.git
cd newrelic-mcp-server

# Install in development mode
pip install -e .
```

## Configuration

### Secure Credential Setup (Recommended for macOS)

For enhanced security on macOS, use the built-in keychain storage instead of environment variables:

```bash
# Run the secure setup wizard
newrelic-mcp-setup

# Or set up manually with Python
python -m newrelic_mcp.credentials
```

This will securely store your API key and account ID in the macOS Keychain, eliminating the need to store sensitive credentials in plain text files.

### Environment Variables (Alternative)

If you prefer environment variables or are not on macOS, you can use:

```bash
# Required
export NEWRELIC_API_KEY="your-api-key-here"  # Your New Relic User API key

# Optional
export NEWRELIC_REGION="US"  # or "EU" (default: "US")
export NEWRELIC_ACCOUNT_ID="your-account-id"  # Required for some operations
```

**Note:** The server will automatically prefer keychain storage over environment variables when both are available.

### Getting Your API Key

1. Log in to New Relic
2. Navigate to the [API Keys page](https://one.newrelic.com/api-keys)
3. Create a new User API key (starts with `NRAK`)
4. Copy the key and set it as the `NEWRELIC_API_KEY` environment variable

## Usage

### With Claude Desktop

#### Option 1: Using Secure Keychain (Recommended for macOS)

After setting up credentials with `newrelic-mcp-setup`, add the following to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "newrelic": {
      "command": "newrelic-mcp-server",
      "env": {
        "NEWRELIC_REGION": "US"
      }
    }
  }
}
```

#### Option 2: Using Environment Variables (Less Secure)

```json
{
  "mcpServers": {
    "newrelic": {
      "command": "newrelic-mcp-server",
      "env": {
        "NEWRELIC_API_KEY": "your-api-key-here",
        "NEWRELIC_REGION": "US",
        "NEWRELIC_ACCOUNT_ID": "your-account-id"
      }
    }
  }
}
```

**Security Note:** Option 1 is strongly recommended as it keeps your sensitive API key out of configuration files.

### With Other MCP Clients

```bash
# Start the server directly
newrelic-mcp-server

# Or run as a module
python -m newrelic_mcp
```

## Available Tools

### Application Management

- `list_applications` - List all APM applications
- `get_application` - Get details for a specific application
- `get_application_metrics` - Get available metrics for an application
- `get_application_metric_data` - Get metric data with time range filtering

### Querying

- `query_nrql` - Execute NRQL queries for data analysis
- `nerdgraph_query` - Execute custom NerdGraph GraphQL queries

### Monitoring

- `list_alert_policies` - List all alert policies
- `get_alert_policy` - Get specific alert policy details
- `list_synthetic_monitors` - List synthetic monitors
- `get_synthetic_monitor` - Get synthetic monitor details

### Dashboards & Visualization

- `list_dashboards` - List all dashboards
- `get_dashboard` - Get dashboard configuration and widgets

### Infrastructure

- `list_servers` - List monitored servers
- `get_server` - Get server details
- `search_entities` - Search across all entity types

### Deployment Tracking

- `list_deployments` - List application deployments
- `create_deployment` - Record new deployments

### User Management

- `list_users` - List account users
- `get_user` - Get user details

### Log Parsing Rules

- `list_log_parsing_rules` - List all log parsing rules for an account
- `create_log_parsing_rule` - Create a new log parsing rule with GROK pattern and NRQL filter
- `update_log_parsing_rule` - Update an existing log parsing rule
- `delete_log_parsing_rule` - Delete a log parsing rule
- `test_log_parsing_rule` - Test a GROK pattern against sample logs (generates pattern if not provided)
- `generate_log_parsing_rule` - Intelligently generate GROK patterns from log samples or NRQL queries

### Credential Management

- `manage_credentials` - Securely manage API credentials in keychain
  - `action="status"` - Show current credential storage status
  - `action="store"` - Store new credentials securely (requires `api_key` parameter)
  - `action="delete"` - Remove all stored credentials

## Examples

### Query Application Performance

```python
# List all applications
await list_applications()

# Get specific application metrics
await get_application_metric_data(
    app_id='123456',
    metric_names=['HttpDispatcher', 'Apdex'],
    from_time='2024-01-01T00:00:00Z',
    to_time='2024-01-02T00:00:00Z'
)
```

### Execute NRQL Query

```python
await query_nrql(
    account_id='1234567',
    nrql='SELECT average(duration) FROM Transaction WHERE appName = "My App" SINCE 1 hour ago'
)
```

### Search Entities

```python
await search_entities(
    query='name LIKE "%production%"',
    limit=50
)
```

### Create Deployment Marker

```python
await create_deployment(
    app_id='123456',
    revision='v2.0.1',
    description='Production deployment',
    user='deploy-bot',
    changelog='Fixed critical bug in payment processing'
)
```

### Log Parsing Rules

#### Generate GROK Pattern from Log Samples

```python
# Generate parsing rule from sample logs (sanitized example)
await generate_log_parsing_rule(
    log_samples=[
        "Updated info for user 12345678-1234-5678-9012-123456789012 (updated 1 rows, expected 1) - updated values: EmailAddress test@example.com, FirstName TestName, LastName TestLast, Active True, EmailConfirmed False"
    ]
)

# Returns generated GROK pattern and NRQL filter:
# {
#   "grok_pattern": "Updated info for user %{UUID:user_id:string} \\(updated %{INT:rows_affected:long} rows, expected %{INT:rows_expected:long}\\) - updated values: EmailAddress %{DATA:email:string}, FirstName %{WORD:first_name:string}, LastName %{WORD:last_name:string}, Active %{WORD:active:string}, EmailConfirmed %{WORD:emailconfirmed:string}",
#   "nrql_pattern": "SELECT * FROM Log WHERE message LIKE 'Updated info for user % (updated % rows, expected %) - updated values: EmailAddress %, FirstName %, LastName %, Active %, EmailConfirmed %'",
#   "suggested_description": "Auto-generated parsing rule for single log sample"
# }
```

#### Create Log Parsing Rule

```python
# Create a new parsing rule using generated patterns
await create_log_parsing_rule(
    description="User update audit log parsing",
    grok="Updated info for user %{UUID:user_id:string} \\(updated %{INT:rows_affected:long} rows, expected %{INT:rows_expected:long}\\) - updated values: EmailAddress %{DATA:email:string}, FirstName %{WORD:first_name:string}, LastName %{WORD:last_name:string}, Active %{WORD:active:string}, EmailConfirmed %{WORD:emailconfirmed:string}",
    nrql="SELECT * FROM Log WHERE message LIKE 'Updated info for user % (updated % rows, expected %) - updated values: EmailAddress %, FirstName %, LastName %, Active %, EmailConfirmed %'",
    enabled=True
)
```

#### Generate from Live Logs

```python
# Generate patterns from logs matching a query
await generate_log_parsing_rule(
    log_query="service = 'user-service' AND message LIKE '%Updated info for user%'",
    time_range="1 day ago",
    field_hints={"user_id": "UUID", "email": "EMAIL"}
)
```

#### Test Parsing Rules

```python
# Test a GROK pattern against samples
await test_log_parsing_rule(
    log_samples=["Updated info for user 12345678-1234-5678-9012-123456789012 (updated 1 rows, expected 1)"],
    grok_pattern="Updated info for user %{UUID:user_id:string} \\(updated %{INT:rows_affected:long} rows, expected %{INT:rows_expected:long}\\)"
)
```

#### Manage Parsing Rules

```python
# List all parsing rules
await list_log_parsing_rules()

# Update a rule
await update_log_parsing_rule(
    rule_id="12345",
    description="Updated user audit log parsing",
    enabled=False
)

# Delete a rule
await delete_log_parsing_rule(rule_id="12345")
```

## Development

```bash
# Clone the repository
git clone https://github.com/piekstra/newrelic-mcp-server.git
cd newrelic-mcp-server

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run the server
newrelic-mcp-server

# Run tests (when available)
pytest

# Format code
black newrelic_mcp

# Lint code
flake8 newrelic_mcp

# Run all pre-commit checks
pre-commit run --all-files
```

## Dependencies

- `fastmcp` - FastMCP framework for building MCP servers
- `httpx` - Async HTTP client for API requests
- `python-dotenv` - Environment variable management (optional)

## API Rate Limits

Be aware of New Relic's API rate limits:
- REST API v2: Subject to rate limiting per account
- NerdGraph: Higher rate limits but still enforced
- Synthetic Monitoring API: 3 requests per second

## Security

- **Use keychain storage on macOS**: Run `newrelic-mcp-setup` to store credentials securely in the system keychain
- Never commit API keys to version control
- Avoid storing sensitive credentials in plain text configuration files
- API keys should have minimal required permissions
- Consider using separate keys for different environments
- The server automatically prioritizes keychain storage over environment variables for enhanced security

## Troubleshooting

### Authentication Errors

- Ensure your API key starts with `NRAK`
- Verify the key has the necessary permissions
- Check if you're using the correct region (US/EU)
- If using keychain storage, verify credentials are stored with `manage_credentials` action="status"
- Try re-running `newrelic-mcp-setup` if keychain access fails

### Rate Limiting

If you encounter rate limit errors:
- Implement exponential backoff in your client code
- Cache frequently accessed data
- Batch operations where possible

### Connection Issues

- Verify network connectivity
- Check firewall rules for API endpoints
- Ensure correct base URLs for your region

### Python Environment

- Ensure Python 3.10+ is installed
- Install dependencies with `pip install -r requirements.txt`
- Check that the script is executable: `chmod +x newrelic_mcp_server.py`

### Command Not Found Issues

If you encounter "command not found" errors after installation:
- Try using the full path to the installed package:
  - Linux/macOS (user install): `~/.local/bin/newrelic-mcp-server`
  - macOS (Python framework): `/Library/Frameworks/Python.framework/Versions/3.13/bin/newrelic-mcp-server`
  - System-wide: `/usr/local/bin/newrelic-mcp-server`
- Or add the installation directory to your PATH: `export PATH="$HOME/.local/bin:$PATH"`
- In Claude Desktop config, use the full path if the command isn't found:
  ```json
  {
    "mcpServers": {
      "newrelic": {
        "command": "/Library/Frameworks/Python.framework/Versions/3.13/bin/newrelic-mcp-server",
        "env": {
          "NEWRELIC_API_KEY": "your-api-key-here",
          "NEWRELIC_REGION": "US",
          "NEWRELIC_ACCOUNT_ID": "your-account-id"
        }
      }
    }
  }
  ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/piekstra/newrelic-mcp-server/issues)
- New Relic Documentation: [docs.newrelic.com](https://docs.newrelic.com)
