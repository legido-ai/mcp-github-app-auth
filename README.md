# MCP GitHub App Server

A lightweight MCP (Model Context Protocol) server that provides GitHub operations using GitHub App authentication instead of personal access tokens.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Docker Usage](#docker-usage)
  - [List Available Tools](#list-available-tools)
  - [Get GitHub Token](#get-github-token)
  - [End-to-End Example](#end-to-end-example)
- [Integration with Claude Desktop](#integration-with-claude-desktop)
- [Integration with Google Gemini CLI](#integration-with-google-gemini-cli)
- [Testing](#testing)
- [Security Notes](#security-notes)

## Prerequisites

- A GitHub App installed with repository permissions for Contents (Read & write) and Pull requests (Read & write)
- **Required environment variables:**
  - `GITHUB_APP_ID` - Your GitHub App ID
  - `GITHUB_PRIVATE_KEY` - Your GitHub App private key (PEM format)
  - `GITHUB_INSTALLATION_ID` - Your GitHub App installation ID

## Tools

The server implements the standard MCP protocol and provides one tool:

- **`get_token`**: Obtain a temporary GitHub token for accessing private repositories using GitHub App authentication
  - Parameters: `owner` (string), `repo` (string)
  - Returns a GitHub token that can be used with git commands to clone repositories

This server does not perform Git operations itself, but provides temporary GitHub tokens for use with standard Git commands.

## Installation

```bash
pip install .
```

## Usage

### Docker Usage

Pull the pre-built image from GitHub Container Registry:
```bash
docker pull ghcr.io/legido-ai/mcp-github-app-auth:latest
```

Or build locally from source:
```bash
docker build . -t mcp-github-app-auth
```

### List Available Tools

List all available tools:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | \
  docker run -i --rm \
  -e GITHUB_APP_ID="$GITHUB_APP_ID" \
  -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" \
  -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" \
  ghcr.io/legido-ai/mcp-github-app-auth:latest
```

This returns a JSON response with the list of tools and their schemas.

### Get GitHub Token

Execute the `get_token` command to obtain a GitHub token:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "get_token", "params": {"owner": "fictional-org", "repo": "private-repo"}}' | \
  docker run -i --rm \
  -e GITHUB_APP_ID="$GITHUB_APP_ID" \
  -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" \
  -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" \
  ghcr.io/legido-ai/mcp-github-app-auth:latest
```

This returns a JSON response with the GitHub token:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"github_token": "ghs_tokenhere"}}
```

You can then use this token to clone the repository:
```bash
git clone https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
```

## End-to-End Example

1. Pull the pre-built image:
```bash
docker pull ghcr.io/legido-ai/mcp-github-app-auth:latest
```

2. List available tools:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | \
  docker run -i --rm \
  -e GITHUB_APP_ID="$GITHUB_APP_ID" \
  -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" \
  -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" \
  ghcr.io/legido-ai/mcp-github-app-auth:latest
```

3. Get a GitHub token:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "get_token", "params": {"owner": "fictional-org", "repo": "private-repo"}}' | \
  docker run -i --rm \
  -e GITHUB_APP_ID="$GITHUB_APP_ID" \
  -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" \
  -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" \
  ghcr.io/legido-ai/mcp-github-app-auth:latest
```

4. Use the returned token to clone the repository:
```bash
git clone https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
```

## Integration with Claude Desktop

Add the MCP server to Claude Desktop using the CLI:

```bash
./claude mcp add-json github '{"command":"docker","args":["run","-i","--rm","-e","GITHUB_APP_ID=$GITHUB_APP_ID","-e","GITHUB_PRIVATE_KEY=$GITHUB_PRIVATE_KEY","-e","GITHUB_INSTALLATION_ID=$GITHUB_INSTALLATION_ID","ghcr.io/legido-ai/mcp-github-app-auth:latest"],"trust":true,"timeout":30000}'
```

## Integration with Google Gemini CLI

Add the server to your Gemini CLI `settings.json` (located at `~/.gemini/settings.json`):

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_APP_ID=$GITHUB_APP_ID",
        "-e",
        "GITHUB_PRIVATE_KEY=$GITHUB_PRIVATE_KEY",
        "-e",
        "GITHUB_INSTALLATION_ID=$GITHUB_INSTALLATION_ID",
        "ghcr.io/legido-ai/mcp-github-app-auth:latest"
      ],
      "trust": true,
      "timeout": 30000
    }
  }
}
```

Verify the connection:
```bash
gemini mcp list
```

You should see:
```
✓ github: docker run -i --rm ... ghcr.io/legido-ai/mcp-github-app-auth:latest (stdio) - Connected
```

## Testing

Run tests with:
```bash
python3 -m pytest tests/ -v
```

## Security Notes

- Installation tokens expire after approximately 1 hour
- The server caches and refreshes tokens automatically
