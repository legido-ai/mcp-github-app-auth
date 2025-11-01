# MCP GitHub App Server

A lightweight MCP (Model Context Protocol) server that provides GitHub operations using GitHub App authentication instead of personal access tokens.

## Tools

The server implements the standard MCP protocol and supports the `tools/list` method to enumerate available tools. There is only one tool available:

### Primary Tool

- **`get_token`**: Obtain a temporary GitHub token for accessing private repositories using GitHub App authentication
  - Parameters: `owner` (string), `repo` (string)
  - Returns a GitHub token that can be used with git commands to clone repositories

This is the only tool provided by this server. It does not perform any Git operations itself, but instead provides temporary GitHub tokens that can be used with standard Git commands.

## Prerequisites

- A GitHub App installed with repository permissions for Contents (Read & write) and Pull requests (Read & write)
- Environment variables: `GITHUB_APP_ID`, `GITHUB_PRIVATE_KEY`, `GITHUB_INSTALLATION_ID`

## Installation

```bash
pip install .
```

## Usage

### Docker Usage (Recommended)

Build the Docker image:
```bash
docker build . -t localhost/test
```

### List Available Tools

List all available tools:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | docker run -i --rm -e GITHUB_APP_ID="$GITHUB_APP_ID" -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" localhost/test
```

This returns a JSON response with the list of tools and their schemas:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"tools": [{"name": "get_token", "description": "Obtain a temporary GitHub token for accessing private repositories using GitHub App authentication. This token can be used with git commands to clone repositories.", "inputSchema": {"properties": {"owner": {"title": "Owner", "type": "string"}, "repo": {"title": "Repo", "type": "string"}, "dest_dir": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "Dest Dir"}, "branch": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "Branch"}}, "required": ["owner", "repo"], "title": "CloneArgs", "type": "object"}}]}}
```

### Get GitHub Token

Execute the `get_token` command to get a GitHub token:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "get_token", "params": {"owner": "fictional-org", "repo": "private-repo"}}' | docker run -i --rm -e GITHUB_APP_ID="$GITHUB_APP_ID" -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" localhost/test
```

This returns a JSON response with the GitHub token:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"github_token": "ghs_tokenhere"}}
```

You can then use this token to clone the repository directly:
```bash
git clone https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
```

## End-to-End Example

1. Build the server:
```bash
docker build . -t localhost/test
```

2. List available tools:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | docker run -i --rm -e GITHUB_APP_ID="$GITHUB_APP_ID" -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" localhost/test
```

3. Get a GitHub token by running the get_token command:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "get_token", "params": {"owner": "fictional-org", "repo": "private-repo"}}' | docker run -i --rm -e GITHUB_APP_ID="$GITHUB_APP_ID" -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" localhost/test
```

This will return a JSON response like:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"github_token": "ghs_tokenhere"}}
```

4. Use the returned token to clone the repository:
```bash
git clone https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
```

## Image Size

The Docker image has been optimized using Alpine Linux, reducing the size from ~693MB to ~373MB (a ~46% reduction).

## Testing

Run tests with:
```bash
python3 -m pytest tests/ -v
```

## Security Notes

- Installation tokens expire after approximately 1 hour
- The server caches and refreshes tokens automatically
