# New Relic MCP Server

A Model Context Protocol (MCP) server that provides programmatic access to New Relic APIs, enabling AI assistants and other tools to interact with New Relic monitoring and observability data.

## Features

- **APM Application Management**: List and retrieve application details, metrics, and metric data
- **NRQL Queries**: Execute NRQL queries via NerdGraph
- **Alert Policies**: List and manage alert policies
- **Synthetic Monitoring**: Access synthetic monitor information
- **Dashboards**: List and retrieve dashboard configurations
- **Entity Search**: Search across all New Relic entities
- **Infrastructure**: Monitor servers and infrastructure components
- **Deployments**: Track and create application deployments
- **User Management**: List and manage users
- **NerdGraph**: Execute custom GraphQL queries

## Installation

```bash
npm install @piekstras/newrelic-mcp-server
```

## Configuration

The server requires the following environment variables:

```bash
# Required
export NEWRELIC_API_KEY="your-api-key-here"  # Your New Relic User API key

# Optional
export NEWRELIC_REGION="US"  # or "EU" (default: "US")
export NEWRELIC_ACCOUNT_ID="your-account-id"  # Required for some operations
```

### Getting Your API Key

1. Log in to New Relic
2. Navigate to the [API Keys page](https://one.newrelic.com/api-keys)
3. Create a new User API key (starts with `NRAK`)
4. Copy the key and set it as the `NEWRELIC_API_KEY` environment variable

## Usage

### With Claude Desktop

Add the following to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "newrelic": {
      "command": "npx",
      "args": ["@piekstras/newrelic-mcp-server"],
      "env": {
        "NEWRELIC_API_KEY": "your-api-key-here",
        "NEWRELIC_REGION": "US",
        "NEWRELIC_ACCOUNT_ID": "your-account-id"
      }
    }
  }
}
```

### With Other MCP Clients

```bash
# Start the server
npx @piekstras/newrelic-mcp-server

# Or if installed locally
npm start
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

## Examples

### Query Application Performance

```javascript
// List all applications
await tool.call('list_applications');

// Get specific application metrics
await tool.call('get_application_metric_data', {
  appId: '123456',
  metricNames: ['HttpDispatcher', 'Apdex'],
  from: '2024-01-01T00:00:00Z',
  to: '2024-01-02T00:00:00Z'
});
```

### Execute NRQL Query

```javascript
await tool.call('query_nrql', {
  accountId: '1234567',
  nrql: 'SELECT average(duration) FROM Transaction WHERE appName = "My App" SINCE 1 hour ago'
});
```

### Search Entities

```javascript
await tool.call('search_entities', {
  query: 'name LIKE "%production%"',
  limit: 50
});
```

### Create Deployment Marker

```javascript
await tool.call('create_deployment', {
  appId: '123456',
  revision: 'v2.0.1',
  description: 'Production deployment',
  user: 'deploy-bot',
  changelog: 'Fixed critical bug in payment processing'
});
```

## Development

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Run in development mode
npm run dev

# Run tests
npm test

# Type checking
npm run typecheck

# Linting
npm run lint
```

## API Rate Limits

Be aware of New Relic's API rate limits:
- REST API v2: Subject to rate limiting per account
- NerdGraph: Higher rate limits but still enforced
- Synthetic Monitoring API: 3 requests per second

## Security

- Never commit API keys to version control
- Use environment variables for sensitive configuration
- API keys should have minimal required permissions
- Consider using separate keys for different environments

## Troubleshooting

### Authentication Errors

- Ensure your API key starts with `NRAK`
- Verify the key has the necessary permissions
- Check if you're using the correct region (US/EU)

### Rate Limiting

If you encounter rate limit errors:
- Implement exponential backoff
- Cache frequently accessed data
- Batch operations where possible

### Connection Issues

- Verify network connectivity
- Check firewall rules for API endpoints
- Ensure correct base URLs for your region

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/piekstra/newrelic-mcp-server/issues)
- New Relic Documentation: [docs.newrelic.com](https://docs.newrelic.com)