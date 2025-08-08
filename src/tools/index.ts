import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { NewRelicClient } from '../client/newrelic-client.js';

export function getTools(): Tool[] {
  return [
    {
      name: 'list_applications',
      description: 'List all New Relic APM applications',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'get_application',
      description: 'Get details for a specific New Relic application',
      inputSchema: {
        type: 'object',
        properties: {
          appId: {
            type: 'string',
            description: 'The application ID',
          },
        },
        required: ['appId'],
      },
    },
    {
      name: 'get_application_metrics',
      description: 'Get available metrics for an application',
      inputSchema: {
        type: 'object',
        properties: {
          appId: {
            type: 'string',
            description: 'The application ID',
          },
          names: {
            type: 'array',
            items: {
              type: 'string',
            },
            description: 'Optional list of metric names to filter',
          },
        },
        required: ['appId'],
      },
    },
    {
      name: 'get_application_metric_data',
      description: 'Get metric data for an application',
      inputSchema: {
        type: 'object',
        properties: {
          appId: {
            type: 'string',
            description: 'The application ID',
          },
          metricNames: {
            type: 'array',
            items: {
              type: 'string',
            },
            description: 'List of metric names to retrieve',
          },
          from: {
            type: 'string',
            description: 'Start time (ISO 8601 format)',
          },
          to: {
            type: 'string',
            description: 'End time (ISO 8601 format)',
          },
        },
        required: ['appId', 'metricNames'],
      },
    },
    {
      name: 'query_nrql',
      description: 'Execute an NRQL query',
      inputSchema: {
        type: 'object',
        properties: {
          accountId: {
            type: 'string',
            description: 'The New Relic account ID',
          },
          nrql: {
            type: 'string',
            description: 'The NRQL query to execute',
          },
        },
        required: ['accountId', 'nrql'],
      },
    },
    {
      name: 'list_alert_policies',
      description: 'List all alert policies',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'get_alert_policy',
      description: 'Get details for a specific alert policy',
      inputSchema: {
        type: 'object',
        properties: {
          policyId: {
            type: 'string',
            description: 'The alert policy ID',
          },
        },
        required: ['policyId'],
      },
    },
    {
      name: 'list_synthetic_monitors',
      description: 'List all synthetic monitors',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'get_synthetic_monitor',
      description: 'Get details for a specific synthetic monitor',
      inputSchema: {
        type: 'object',
        properties: {
          monitorId: {
            type: 'string',
            description: 'The synthetic monitor ID',
          },
        },
        required: ['monitorId'],
      },
    },
    {
      name: 'list_dashboards',
      description: 'List all dashboards for an account',
      inputSchema: {
        type: 'object',
        properties: {
          accountId: {
            type: 'string',
            description: 'The New Relic account ID (optional if set in environment)',
          },
        },
      },
    },
    {
      name: 'get_dashboard',
      description: 'Get details for a specific dashboard',
      inputSchema: {
        type: 'object',
        properties: {
          guid: {
            type: 'string',
            description: 'The dashboard GUID',
          },
        },
        required: ['guid'],
      },
    },
    {
      name: 'search_entities',
      description: 'Search for entities in New Relic',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'The search query',
          },
          limit: {
            type: 'number',
            description: 'Maximum number of results (default: 25)',
          },
        },
        required: ['query'],
      },
    },
    {
      name: 'list_servers',
      description: 'List all servers monitored by New Relic Infrastructure',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'get_server',
      description: 'Get details for a specific server',
      inputSchema: {
        type: 'object',
        properties: {
          serverId: {
            type: 'string',
            description: 'The server ID',
          },
        },
        required: ['serverId'],
      },
    },
    {
      name: 'list_deployments',
      description: 'List deployments for an application',
      inputSchema: {
        type: 'object',
        properties: {
          appId: {
            type: 'string',
            description: 'The application ID',
          },
        },
        required: ['appId'],
      },
    },
    {
      name: 'create_deployment',
      description: 'Record a new deployment for an application',
      inputSchema: {
        type: 'object',
        properties: {
          appId: {
            type: 'string',
            description: 'The application ID',
          },
          revision: {
            type: 'string',
            description: 'The deployment revision or version',
          },
          description: {
            type: 'string',
            description: 'Description of the deployment',
          },
          user: {
            type: 'string',
            description: 'User who performed the deployment',
          },
          changelog: {
            type: 'string',
            description: 'Changelog or release notes',
          },
        },
        required: ['appId', 'revision'],
      },
    },
    {
      name: 'nerdgraph_query',
      description: 'Execute a custom NerdGraph GraphQL query',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'The GraphQL query',
          },
          variables: {
            type: 'object',
            description: 'Optional GraphQL variables',
          },
        },
        required: ['query'],
      },
    },
    {
      name: 'list_users',
      description: 'List all users in the New Relic account',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'get_user',
      description: 'Get details for a specific user',
      inputSchema: {
        type: 'object',
        properties: {
          userId: {
            type: 'string',
            description: 'The user ID',
          },
        },
        required: ['userId'],
      },
    },
  ];
}

export async function handleToolCall(
  client: NewRelicClient,
  toolName: string,
  args: any
): Promise<any> {
  try {
    switch (toolName) {
      case 'list_applications':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.listApplications(), null, 2),
            },
          ],
        };

      case 'get_application':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.getApplication(args.appId), null, 2),
            },
          ],
        };

      case 'get_application_metrics':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                await client.getApplicationMetrics(args.appId, args.names),
                null,
                2
              ),
            },
          ],
        };

      case 'get_application_metric_data':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                await client.getApplicationMetricData(
                  args.appId,
                  args.metricNames,
                  args.from ? new Date(args.from) : undefined,
                  args.to ? new Date(args.to) : undefined
                ),
                null,
                2
              ),
            },
          ],
        };

      case 'query_nrql':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                await client.queryNRQL(args.accountId, args.nrql),
                null,
                2
              ),
            },
          ],
        };

      case 'list_alert_policies':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.listAlertPolicies(), null, 2),
            },
          ],
        };

      case 'get_alert_policy':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.getAlertPolicy(args.policyId), null, 2),
            },
          ],
        };

      case 'list_synthetic_monitors':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.listSyntheticMonitors(), null, 2),
            },
          ],
        };

      case 'get_synthetic_monitor':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                await client.getSyntheticMonitor(args.monitorId),
                null,
                2
              ),
            },
          ],
        };

      case 'list_dashboards':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                await client.listDashboards(args.accountId),
                null,
                2
              ),
            },
          ],
        };

      case 'get_dashboard':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.getDashboard(args.guid), null, 2),
            },
          ],
        };

      case 'search_entities':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                await client.searchEntities(args.query, args.limit || 25),
                null,
                2
              ),
            },
          ],
        };

      case 'list_servers':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.listServers(), null, 2),
            },
          ],
        };

      case 'get_server':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.getServer(args.serverId), null, 2),
            },
          ],
        };

      case 'list_deployments':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.listDeployments(args.appId), null, 2),
            },
          ],
        };

      case 'create_deployment':
        const deployment = {
          revision: args.revision,
          description: args.description,
          user: args.user,
          changelog: args.changelog,
        };
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                await client.createDeployment(args.appId, deployment),
                null,
                2
              ),
            },
          ],
        };

      case 'nerdgraph_query':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                await client.nerdGraphQuery(args.query, args.variables),
                null,
                2
              ),
            },
          ],
        };

      case 'list_users':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.listUsers(), null, 2),
            },
          ],
        };

      case 'get_user':
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(await client.getUser(args.userId), null, 2),
            },
          ],
        };

      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}\n${error.response?.data ? JSON.stringify(error.response.data, null, 2) : ''}`,
        },
      ],
      isError: true,
    };
  }
}