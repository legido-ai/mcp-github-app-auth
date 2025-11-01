# MCP GitHub App Server

## Table of Contents
- [Purpose](#purpose)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Available Tools](#available-tools)
- [Docker Example with Qwen Integration](#docker-example-with-qwen-integration)
- [Integration with Qwen Code](#integration-with-qwen-code)
- [Security Notes](#security-notes)

An MCP (Model Context Protocol) server written in Python that provides GitHub operations using GitHub App authentication instead of personal access tokens.

## Purpose

This server mirrors the most-used operations of the official GitHub MCP server (repos, PRs, branches, etc.) but authenticates using GitHub App credentials via `GITHUB_APP_ID`, `GITHUB_PRIVATE_KEY`, and `GITHUB_INSTALLATION_ID`—no Personal Access Token (PAT) required.

This design generates a short-lived installation access token (`ghs_…`) at runtime from your App's credentials and injects it into API and Git operations.

## Features

- Clone repositories
- Create branches
- Push changes
- Create pull requests
- Merge pull requests
- Create/update files

## Prerequisites

- A GitHub App installed on the target org/repo with at least:
  - Repository permissions → Contents: Read & write, Pull requests: Read & write, Metadata: Read
- Environment variables set:
  - `GITHUB_APP_ID` → the App ID (integer)
  - `GITHUB_PRIVATE_KEY` → the App's PEM private key
  - `GITHUB_INSTALLATION_ID` → installation id for the org/user where the app is installed
- Python 3.10+

## Installation

1. Clone this repository
2. Install dependencies: `pip install .`

## Usage

Set the required environment variables:

```bash
export GITHUB_APP_ID=your_app_id
export GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
export GITHUB_INSTALLATION_ID=your_installation_id
```

Then run the server:

```bash
python -m mcp_github_app.server
```

Or use the provided script:

```bash
./scripts/run.sh
```

## Testing

This repository includes a comprehensive test suite in the `tests/` directory:

- `tests/test_auth.py`: Tests for authentication functionality
- `tests/test_git_ops.py`: Tests for Git operations
- `tests/test_server.py`: Tests for the MCP server functionality
- `tests/test_integration.py`: Integration tests for full workflows

### Running Tests

You can run the tests using pytest:
```bash
# Run all tests with verbose output
python3 -m pytest tests/ -v

# Run all tests and show coverage
python3 -m pytest tests/ --cov=mcp_github_app

# Run specific test file
python3 -m pytest tests/test_auth.py
```

Alternatively, you can use the test runner script:
```bash
python3 run_tests.py
```

### Prerequisites for Testing
Make sure you have the required packages installed:
```bash
pip install pytest pytest-cov
```

## Available Tools

The MCP GitHub App server exposes the following tools for interacting with GitHub repositories:

- **`clone_repo`**: Clones a specified repository to a destination directory.
  - **Parameters**: `owner` (string), `repo` (string), `dest_dir` (string)
  - **Example**: `echo '{"jsonrpc": "2.0", "id": 1, "method": "clone_repo", "params": {"owner": "legido-ai", "repo": "quote-agent", "dest_dir": "/tmp/quote-agent"}}' | docker run -i --rm -e GITHUB_APP_ID="$GITHUB_APP_ID" -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" localhost/test`

- **`create_branch`**: Creates a new branch in a repository.
  - **Parameters**: `owner` (string), `repo` (string), `new_branch_name` (string), `base_branch` (string, optional, defaults to 'main')
  - **Example**: `echo '{"jsonrpc": "2.0", "id": 2, "method": "create_branch", "params": {"owner": "legido-ai", "repo": "quote-agent", "new_branch_name": "test-branch-from-readme", "base_branch": "main"}}' | docker run -i --rm -e GITHUB_APP_ID="$GITHUB_APP_ID" -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" localhost/test`

- **`push_changes`**: Pushes local changes to a remote branch.
  - **Parameters**: `owner` (string), `repo` (string), `branch` (string), `commit_message` (string), `file_changes` (object, e.g., `{"path/to/file": "content"}`)

- **`create_pull_request`**: Creates a pull request between two branches.
  - **Parameters**: `owner` (string), `repo` (string), `title` (string), `body` (string), `head` (string, source branch), `base` (string, target branch)

- **`merge_pull_request`**: Merges a pull request.
  - **Parameters**: `owner` (string), `repo` (string), `pull_number` (integer), `merge_method` (string, optional, e.g., 'merge', 'squash', 'rebase')

- **`create_update_file`**: Creates or updates a file in a repository.
  - **Parameters**: `owner` (string), `repo` (string), `path` (string), `content` (string), `commit_message` (string), `branch` (string, optional)

## Docker Example with Qwen Integration

For an example of using Qwen with this server via Docker, see the `examples/qwen-docker/` directory.

## Integration with Qwen Code

### Direct Integration
Add the following to your project's `.qwen/settings.json`:

```json
{
  "mcpServers": {
    "github-app": {
      "command": "python",
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

### Docker Container Integration (Recommended for Qwen)
For integrating with Qwen via a Docker container, you can run the MCP server in a container:

1. Build the Docker image:
```bash
docker build -t mcp-github-app-server .
```

2. Create a `.env` file containing your GitHub App credentials:
```bash
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_INSTALLATION_ID=your_installation_id
```

3. Run the server container:
```bash
docker run -d --env-file .env -p 3000:3000 --name mcp-github-server mcp-github-app-server
```

4. Configure Qwen to connect to the running container instead of running the server locally.

Alternatively, you can configure Qwen to run the MCP server directly in a Docker container by adding the following to your project's `.qwen/settings.json`:

```json
{
  "mcpServers": {
    "github-app": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", 
        "GITHUB_APP_ID=${env:GITHUB_APP_ID}",
        "-e",
        "GITHUB_PRIVATE_KEY=${env:GITHUB_PRIVATE_KEY}",
        "-e",
        "GITHUB_INSTALLATION_ID=${env:GITHUB_INSTALLATION_ID}",
        "mcp-github-app-server"
      ],
      "trust": true,
      "timeout": 30000
    }
  }
}
```

This approach runs the MCP server in an isolated Docker container each time Qwen needs to perform Git operations, providing better isolation and security.

You can also use the example in `examples/qwen-docker/` which includes a complete setup with docker-compose.

## Security Notes

- Installation tokens expire after approximately 1 hour
- The server caches and refreshes tokens automatically
- Actions performed with installation tokens are attributed to the App installation, not a human account
