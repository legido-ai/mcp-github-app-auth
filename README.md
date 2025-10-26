# MCP GitHub App Server

## Table of Contents
- [Purpose](#purpose)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
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

You can also use the example in `examples/qwen-docker/` which includes a complete setup with docker-compose.

## Security Notes

- Installation tokens expire after approximately 1 hour
- The server caches and refreshes tokens automatically
- Actions performed with installation tokens are attributed to the App installation, not a human account