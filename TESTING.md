# MCP GitHub App Authentication Test

This project demonstrates the usage of Model Context Protocol (MCP) with GitHub App authentication for Git operations.

## Test Summary

### Test 1: Building mcp-github-app-auth with Docker

Successfully built the `mcp-github-app-auth` repository with Docker:
1. Cloned the repository `https://github.com/legido-ai/mcp-github-app-auth/` using GitHub App authentication
2. Fixed an issue in the Dockerfile where it was trying to install a non-existent package
3. Built the Docker image with the command `docker build . -t localhost/test`
4. Verified the image was created successfully (547MB in size)

### Test 2: Using MCP to Clone Repository

Successfully used MCP (Model Context Protocol) with GitHub App authentication to clone another repository:
1. Explored the `mcp-github-app` server implementation to understand how MCP works
2. Installed the `mcp-github-app` package in development mode
3. Used the server's `git_ops.clone_repo` function directly to clone `https://github.com/legido-ai/quote-agent/` 
4. Verified that the repository was cloned successfully to `/projects/quote-agent-test`
5. The clone operation used GitHub App authentication credentials (`GITHUB_APP_ID`, `GITHUB_PRIVATE_KEY`, `GITHUB_INSTALLATION_ID`) to generate a temporary installation access token

## How MCP Works

The Model Context Protocol (MCP) server for GitHub App provides a way to perform Git operations using GitHub App authentication instead of personal access tokens. The server:

- Generates a short-lived installation access token at runtime from GitHub App credentials
- Provides tools like `clone_repo`, `create_branch`, `push`, `create_pull_request`, and `merge_pull_request`
- Handles authentication transparently for Git operations

## Environment Variables Required

- `GITHUB_APP_ID` - The GitHub App ID
- `GITHUB_PRIVATE_KEY` - The GitHub App's PEM private key
- `GITHUB_INSTALLATION_ID` - The installation ID for the organization where the app is installed

## Security Notes

- Installation tokens expire after approximately 1 hour
- The server caches and refreshes tokens automatically
- Actions performed with installation tokens are attributed to the App installation, not a human account