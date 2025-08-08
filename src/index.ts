#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { NewRelicClient } from './client/newrelic-client.js';
import { getTools, handleToolCall } from './tools/index.js';

const server = new Server(
  {
    name: 'newrelic-mcp-server',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

let client: NewRelicClient;

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: getTools(),
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (!client) {
    const apiKey = process.env.NEWRELIC_API_KEY || process.env.NEW_RELIC_API_KEY;
    const region = (process.env.NEWRELIC_REGION || 'US') as 'US' | 'EU';
    
    if (!apiKey) {
      throw new Error('NEWRELIC_API_KEY environment variable is required');
    }
    
    client = new NewRelicClient(apiKey, region);
  }

  return handleToolCall(client, request.params.name, request.params.arguments);
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});