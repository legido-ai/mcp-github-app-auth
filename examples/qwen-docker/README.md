# Qwen Integration with MCP GitHub App Authentication

This example demonstrates how to use Qwen with the MCP GitHub App Authentication server running in a Docker container.

## Overview

This example shows how to:
1. Run the MCP GitHub App server in a Docker container
2. Configure Qwen to use the server for Git operations
3. Perform authenticated Git operations using GitHub App credentials

## Prerequisites

- Docker installed
- GitHub App credentials:
  - `GITHUB_APP_ID`: Your GitHub App ID
  - `GITHUB_PRIVATE_KEY`: Your GitHub App's private key
  - `GITHUB_INSTALLATION_ID`: Installation ID for your org/repo

## Running the Example

### 1. Build the Docker image

```bash
docker build -t mcp-github-app-server .
```

### 2. Create an environment file

Create a `.env` file with your GitHub App credentials:

```bash
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_INSTALLATION_ID=your_installation_id
```

### 3. Run the server container

```bash
docker run -d --env-file .env -p 3000:3000 --name mcp-github-server mcp-github-app-server
```

### 4. Configure Qwen to use the MCP server

Add the following configuration to your Qwen project's `.qwen/settings.json`:

```json
{
  "mcpServers": {
    "github-app": {
      "command": "python3",
      "args": ["-m", "mcp_github_app.server"],
      "env": {
        "GITHUB_APP_ID": "${env:GITHUB_APP_ID}",
        "GITHUB_PRIVATE_KEY": "${env:GITHUB_PRIVATE_KEY}",
        "GITHUB_INSTALLATION_ID": "${env:GITHUB_INSTALLATION_ID}"
      },
      "trust": true,
      "timeout": 30000
    }
  }
}
```

## Using the Server

Once configured, Qwen will be able to perform Git operations using GitHub App authentication:

- Clone repositories securely with App permissions
- Create branches and push changes
- Create and merge pull requests
- All operations use temporary installation tokens that expire automatically

## Security Benefits

- No need to store long-lived personal access tokens
- Fine-grained permissions based on GitHub App configuration
- Automatic token expiration after ~1 hour
- Actions attributed to the GitHub App installation