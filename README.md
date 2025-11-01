# MCP GitHub App Server

A lightweight MCP (Model Context Protocol) server that provides GitHub operations using GitHub App authentication instead of personal access tokens.

## Features

- Clone repositories 
- Create branches
- Push changes
- Create pull requests
- Merge pull requests
- Create/update files

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

Execute the `clone_repo` command to get a GitHub token:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "clone_repo", "params": {"owner": "legido-ai", "repo": "quote-agent"}}' | docker run -i --rm -e GITHUB_APP_ID="$GITHUB_APP_ID" -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" localhost/test
```

This returns a JSON response with the GitHub token:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"github_token": "ghs_tokenhere"}}
```

You can then use this token to clone the repository directly:
```bash
git clone https://x-access-token:ghs_tokenhere@github.com/legido-ai/quote-agent.git
```

## End-to-End Example

1. Build the server:
```bash
docker build . -t localhost/test
```

2. Get a GitHub token by running the clone_repo command:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "clone_repo", "params": {"owner": "legido-ai", "repo": "quote-agent"}}' | docker run -i --rm -e GITHUB_APP_ID="$GITHUB_APP_ID" -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" localhost/test
```

This will return a JSON response like:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"github_token": "ghs_tokenhere"}}
```

3. Use the returned token to clone the repository:
```bash
git clone https://x-access-token:ghs_tokenhere@github.com/legido-ai/quote-agent.git
```

## Testing

Run tests with:
```bash
python3 -m pytest tests/ -v
```

## Security Notes

- Installation tokens expire after approximately 1 hour
- The server caches and refreshes tokens automatically
