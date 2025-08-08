#!/usr/bin/env python3
"""
New Relic MCP Server
Provides Claude Code access to New Relic monitoring APIs
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("newrelic-mcp-server")

class NewRelicClient:
    def __init__(self, api_key: str, region: str = "US", account_id: Optional[str] = None):
        self.api_key = api_key
        self.region = region
        self.account_id = account_id
        
        # Set base URLs based on region
        if region == "EU":
            self.base_url = "https://api.eu.newrelic.com/v2"
            self.nerdgraph_url = "https://api.eu.newrelic.com/graphql"
            self.synthetics_url = "https://synthetics.eu.newrelic.com/synthetics/api/v3"
        else:
            self.base_url = "https://api.newrelic.com/v2"
            self.nerdgraph_url = "https://api.newrelic.com/graphql"
            self.synthetics_url = "https://synthetics.newrelic.com/synthetics/api/v3"
        
        # Common headers
        self.headers = {
            "Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            
            if response.status_code >= 400:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = f" - {json.dumps(error_data)}"
                except:
                    error_detail = f" - {response.text}"
                
                raise Exception(f"HTTP {response.status_code}: {response.reason_phrase}{error_detail}")
            
            return response.json()
    
    async def list_applications(self) -> Dict[str, Any]:
        """List all New Relic APM applications"""
        url = f"{self.base_url}/applications.json"
        return await self._make_request("GET", url)
    
    async def get_application(self, app_id: str) -> Dict[str, Any]:
        """Get details for a specific application"""
        url = f"{self.base_url}/applications/{app_id}.json"
        return await self._make_request("GET", url)
    
    async def get_application_metrics(self, app_id: str, names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get available metrics for an application"""
        url = f"{self.base_url}/applications/{app_id}/metrics.json"
        params = {}
        if names:
            params["name"] = ",".join(names)
        return await self._make_request("GET", url, params=params)
    
    async def get_application_metric_data(
        self, 
        app_id: str, 
        metric_names: List[str], 
        from_time: Optional[str] = None, 
        to_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get metric data for an application"""
        url = f"{self.base_url}/applications/{app_id}/metrics/data.json"
        params = {"names": metric_names}
        
        if from_time:
            params["from"] = from_time
        if to_time:
            params["to"] = to_time
            
        return await self._make_request("GET", url, params=params)
    
    async def list_alert_policies(self) -> Dict[str, Any]:
        """List all alert policies"""
        url = f"{self.base_url}/alerts_policies.json"
        return await self._make_request("GET", url)
    
    async def get_alert_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get details for a specific alert policy"""
        url = f"{self.base_url}/alerts_policies/{policy_id}.json"
        return await self._make_request("GET", url)
    
    async def list_synthetic_monitors(self) -> Dict[str, Any]:
        """List all synthetic monitors"""
        return await self._make_request("GET", f"{self.synthetics_url}/monitors.json")
    
    async def get_synthetic_monitor(self, monitor_id: str) -> Dict[str, Any]:
        """Get details for a specific synthetic monitor"""
        return await self._make_request("GET", f"{self.synthetics_url}/monitors/{monitor_id}")
    
    async def list_users(self) -> Dict[str, Any]:
        """List all users in the account"""
        url = f"{self.base_url}/users.json"
        return await self._make_request("GET", url)
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get details for a specific user"""
        url = f"{self.base_url}/users/{user_id}.json"
        return await self._make_request("GET", url)
    
    async def list_servers(self) -> Dict[str, Any]:
        """List all servers monitored by New Relic Infrastructure"""
        url = f"{self.base_url}/servers.json"
        return await self._make_request("GET", url)
    
    async def get_server(self, server_id: str) -> Dict[str, Any]:
        """Get details for a specific server"""
        url = f"{self.base_url}/servers/{server_id}.json"
        return await self._make_request("GET", url)
    
    async def list_deployments(self, app_id: str) -> Dict[str, Any]:
        """List deployments for an application"""
        url = f"{self.base_url}/applications/{app_id}/deployments.json"
        return await self._make_request("GET", url)
    
    async def create_deployment(self, app_id: str, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Record a new deployment for an application"""
        url = f"{self.base_url}/applications/{app_id}/deployments.json"
        return await self._make_request("POST", url, json={"deployment": deployment})
    
    async def nerdgraph_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a NerdGraph GraphQL query"""
        data = {"query": query}
        if variables:
            data["variables"] = variables
        return await self._make_request("POST", self.nerdgraph_url, json=data)
    
    async def query_nrql(self, account_id: str, nrql: str) -> Dict[str, Any]:
        """Execute an NRQL query"""
        query = """
        query($accountId: Int!, $nrql: Nrql!) {
            actor {
                account(id: $accountId) {
                    nrql(query: $nrql) {
                        results
                    }
                }
            }
        }
        """
        
        variables = {
            "accountId": int(account_id),
            "nrql": nrql
        }
        
        return await self.nerdgraph_query(query, variables)
    
    async def list_dashboards(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """List all dashboards for an account"""
        acc_id = account_id or self.account_id
        if not acc_id:
            raise Exception("Account ID is required for dashboard operations")
        
        query = """
        query($accountId: Int!) {
            actor {
                account(id: $accountId) {
                    dashboards {
                        results {
                            guid
                            name
                            description
                            createdAt
                            updatedAt
                            permissions
                        }
                    }
                }
            }
        }
        """
        
        variables = {"accountId": int(acc_id)}
        return await self.nerdgraph_query(query, variables)
    
    async def get_dashboard(self, guid: str) -> Dict[str, Any]:
        """Get details for a specific dashboard"""
        query = """
        query($guid: EntityGuid!) {
            actor {
                entity(guid: $guid) {
                    ... on DashboardEntity {
                        guid
                        name
                        description
                        createdAt
                        updatedAt
                        permissions
                        pages {
                            guid
                            name
                            widgets {
                                id
                                title
                                visualization {
                                    id
                                }
                                configuration
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {"guid": guid}
        return await self.nerdgraph_query(query, variables)
    
    async def search_entities(self, query: str, limit: int = 25) -> Dict[str, Any]:
        """Search for entities in New Relic"""
        gql_query = """
        query($query: String!, $limit: Int!) {
            actor {
                entitySearch(query: $query) {
                    results(limit: $limit) {
                        entities {
                            guid
                            name
                            type
                            entityType
                            domain
                            tags {
                                key
                                values
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {"query": query, "limit": limit}
        return await self.nerdgraph_query(gql_query, variables)

# Initialize client
client: Optional[NewRelicClient] = None

def initialize_client():
    """Initialize the New Relic client with environment variables"""
    global client
    
    api_key = os.getenv("NEWRELIC_API_KEY") or os.getenv("NEW_RELIC_API_KEY")
    region = os.getenv("NEWRELIC_REGION", "US")
    account_id = os.getenv("NEWRELIC_ACCOUNT_ID")
    
    if not api_key:
        raise Exception("NEWRELIC_API_KEY environment variable is required")
    
    client = NewRelicClient(api_key, region, account_id)
    logger.info(f"New Relic client initialized - Region: {region}, Account ID: {account_id or 'not provided'}")

# Tool functions
@mcp.tool()
async def list_applications() -> str:
    """List all New Relic APM applications"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.list_applications()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_application(app_id: str) -> str:
    """Get details for a specific New Relic application"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.get_application(app_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_application_metrics(app_id: str, names: Optional[List[str]] = None) -> str:
    """Get available metrics for an application"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.get_application_metrics(app_id, names)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_application_metric_data(
    app_id: str, 
    metric_names: List[str], 
    from_time: Optional[str] = None, 
    to_time: Optional[str] = None
) -> str:
    """Get metric data for an application"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.get_application_metric_data(app_id, metric_names, from_time, to_time)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def query_nrql(account_id: str, nrql: str) -> str:
    """Execute an NRQL query"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.query_nrql(account_id, nrql)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def list_alert_policies() -> str:
    """List all alert policies"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.list_alert_policies()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_alert_policy(policy_id: str) -> str:
    """Get details for a specific alert policy"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.get_alert_policy(policy_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def list_synthetic_monitors() -> str:
    """List all synthetic monitors"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.list_synthetic_monitors()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_synthetic_monitor(monitor_id: str) -> str:
    """Get details for a specific synthetic monitor"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.get_synthetic_monitor(monitor_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def list_dashboards(account_id: Optional[str] = None) -> str:
    """List all dashboards for an account"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.list_dashboards(account_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_dashboard(guid: str) -> str:
    """Get details for a specific dashboard"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.get_dashboard(guid)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def search_entities(query: str, limit: int = 25) -> str:
    """Search for entities in New Relic"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.search_entities(query, limit)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def list_servers() -> str:
    """List all servers monitored by New Relic Infrastructure"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.list_servers()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_server(server_id: str) -> str:
    """Get details for a specific server"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.get_server(server_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def list_deployments(app_id: str) -> str:
    """List deployments for an application"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.list_deployments(app_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def create_deployment(
    app_id: str, 
    revision: str, 
    description: Optional[str] = None,
    user: Optional[str] = None, 
    changelog: Optional[str] = None
) -> str:
    """Record a new deployment for an application"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        deployment = {"revision": revision}
        if description:
            deployment["description"] = description
        if user:
            deployment["user"] = user
        if changelog:
            deployment["changelog"] = changelog
        
        result = await client.create_deployment(app_id, deployment)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def nerdgraph_query(query: str, variables: Optional[Dict[str, Any]] = None) -> str:
    """Execute a custom NerdGraph GraphQL query"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.nerdgraph_query(query, variables)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def list_users() -> str:
    """List all users in the New Relic account"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.list_users()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_user(user_id: str) -> str:
    """Get details for a specific user"""
    if not client:
        return json.dumps({"error": "New Relic client not initialized"})
    
    try:
        result = await client.get_user(user_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

def main():
    """Initialize and run the FastMCP server"""
    try:
        logger.info("Starting New Relic MCP server...")
        
        # Initialize the client
        initialize_client()
        
        logger.info("New Relic MCP server initialized successfully!")
        
        # Run the FastMCP server
        mcp.run(transport="stdio")
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        exit(1)

if __name__ == "__main__":
    main()