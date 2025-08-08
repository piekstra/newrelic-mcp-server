import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

export interface NewRelicClientConfig {
  apiKey: string;
  region?: 'US' | 'EU';
  accountId?: string;
  timeout?: number;
}

export class NewRelicClient {
  private axios: AxiosInstance;
  private nerdGraphAxios: AxiosInstance;
  private accountId?: string;
  
  constructor(apiKey: string, region: 'US' | 'EU' = 'US', accountId?: string) {
    const baseURL = region === 'EU' 
      ? 'https://api.eu.newrelic.com/v2'
      : 'https://api.newrelic.com/v2';
    
    const nerdGraphURL = region === 'EU'
      ? 'https://api.eu.newrelic.com/graphql'
      : 'https://api.newrelic.com/graphql';

    this.accountId = accountId;
    
    this.axios = axios.create({
      baseURL,
      headers: {
        'Api-Key': apiKey,
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    this.nerdGraphAxios = axios.create({
      baseURL: nerdGraphURL,
      headers: {
        'Api-Key': apiKey,
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });
  }

  async listApplications() {
    const response = await this.axios.get('/applications.json');
    return response.data;
  }

  async getApplication(appId: string) {
    const response = await this.axios.get(`/applications/${appId}.json`);
    return response.data;
  }

  async getApplicationMetrics(appId: string, names?: string[]) {
    const params: any = {};
    if (names && names.length > 0) {
      params.name = names.join(',');
    }
    const response = await this.axios.get(`/applications/${appId}/metrics.json`, { params });
    return response.data;
  }

  async getApplicationMetricData(appId: string, metricNames: string[], from?: Date, to?: Date) {
    const params: any = {
      names: metricNames,
    };
    
    if (from) {
      params.from = from.toISOString();
    }
    if (to) {
      params.to = to.toISOString();
    }

    const response = await this.axios.get(`/applications/${appId}/metrics/data.json`, { params });
    return response.data;
  }

  async listAlertPolicies() {
    const response = await this.axios.get('/alerts_policies.json');
    return response.data;
  }

  async getAlertPolicy(policyId: string) {
    const response = await this.axios.get(`/alerts_policies/${policyId}.json`);
    return response.data;
  }

  async listSyntheticMonitors() {
    const response = await this.axios.get('/monitors.json', {
      baseURL: 'https://synthetics.newrelic.com/synthetics/api/v3',
    });
    return response.data;
  }

  async getSyntheticMonitor(monitorId: string) {
    const response = await this.axios.get(`/monitors/${monitorId}`, {
      baseURL: 'https://synthetics.newrelic.com/synthetics/api/v3',
    });
    return response.data;
  }

  async listUsers() {
    const response = await this.axios.get('/users.json');
    return response.data;
  }

  async getUser(userId: string) {
    const response = await this.axios.get(`/users/${userId}.json`);
    return response.data;
  }

  async listServers() {
    const response = await this.axios.get('/servers.json');
    return response.data;
  }

  async getServer(serverId: string) {
    const response = await this.axios.get(`/servers/${serverId}.json`);
    return response.data;
  }

  async listDeployments(appId: string) {
    const response = await this.axios.get(`/applications/${appId}/deployments.json`);
    return response.data;
  }

  async createDeployment(appId: string, deployment: any) {
    const response = await this.axios.post(`/applications/${appId}/deployments.json`, {
      deployment,
    });
    return response.data;
  }

  async nerdGraphQuery(query: string, variables?: Record<string, any>) {
    const response = await this.nerdGraphAxios.post('', {
      query,
      variables,
    });
    return response.data;
  }

  async queryNRQL(accountId: string, nrql: string) {
    const query = `
      query($accountId: Int!, $nrql: Nrql!) {
        actor {
          account(id: $accountId) {
            nrql(query: $nrql) {
              results
            }
          }
        }
      }
    `;

    const variables = {
      accountId: parseInt(accountId),
      nrql,
    };

    return this.nerdGraphQuery(query, variables);
  }

  async listDashboards(accountId?: string) {
    const accId = accountId || this.accountId;
    if (!accId) {
      throw new Error('Account ID is required for dashboard operations');
    }

    const query = `
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
    `;

    const variables = {
      accountId: parseInt(accId),
    };

    return this.nerdGraphQuery(query, variables);
  }

  async getDashboard(guid: string) {
    const query = `
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
    `;

    const variables = {
      guid,
    };

    return this.nerdGraphQuery(query, variables);
  }

  async searchEntities(query: string, limit: number = 25) {
    const gqlQuery = `
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
    `;

    const variables = {
      query,
      limit,
    };

    return this.nerdGraphQuery(gqlQuery, variables);
  }
}