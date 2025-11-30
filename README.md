# MCP GitHub App Server

A lightweight MCP (Model Context Protocol) server that provides GitHub operations using GitHub App authentication instead of personal access tokens.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Docker Usage](#docker-usage)
  - [Testing the Server](#testing-the-server)
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
  - Parameters:
    - `owner` (string, required): GitHub repository owner/organization
    - `repo` (string, required): GitHub repository name
  - Returns: A temporary GitHub token (valid for ~1 hour) that can be used with Git commands and GitHub REST API calls

**What is `get_token`?**

The `get_token` tool generates a temporary GitHub authentication token that can be used for various Git operations AND GitHub API calls. This is NOT just for cloning - the token can be used for:

**Git Operations:**
- **git clone**: Clone private repositories
- **git push**: Push commits to remote repositories
- **git pull**: Pull updates from remote repositories
- **git fetch**: Fetch remote branches and tags
- Any other Git operation that requires authentication

**GitHub REST API Operations:**
- **Create/manage issues**: Create, update, comment on issues
- **Pull requests**: Create, review, merge pull requests
- **Repository management**: List contents, download files, get repository info
- **Releases**: Create and manage releases
- **Any GitHub REST API endpoint**: The token works with all authenticated API operations

**Token Format:**

For Git operations, use the token in URLs:
```
https://x-access-token:<GITHUB_TOKEN>@github.com/<ORGANIZATION>/<REPOSITORY>.git
```

For GitHub REST API operations, use the token in the Authorization header:
```
Authorization: Bearer <GITHUB_TOKEN>
```

**Important Notes for Agents:**

- The token is temporary and expires after approximately 1 hour
- The token can be used for ANY Git operation that requires authentication (clone, push, pull, fetch, etc.)
- The token can also be used for ANY GitHub REST API operation (create issues, PRs, manage repos, etc.)
- You do NOT need to call `get_token` separately for each operation - one token works for all Git and API operations
- If an operation fails with authentication errors, the token may have expired - simply call `get_token` again to get a fresh token

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

### Testing the Server

This server implements the Model Context Protocol (MCP), which requires a proper initialization handshake before any operations can be performed. Direct JSON-RPC requests without initialization will be rejected.

**Using the Test Script (Recommended):**

The repository includes a test script that properly implements the MCP protocol:

```bash
# List available tools only
python test_mcp_server.py

# List tools and test get_token
python test_mcp_server.py --get-token legido-ai mcp-github-app-auth
```

**Using with MCP Clients:**

The server is designed to be used with MCP-compatible clients such as:
- Claude Desktop/Code
- Google Gemini CLI
- Other MCP-compatible AI assistants

See the integration sections below for setup instructions.

**Note on Direct JSON-RPC Testing:**

MCP requires a three-step initialization sequence before accepting requests:
1. Client sends `initialize` request with protocol version and capabilities
2. Server responds with its capabilities
3. Client sends `initialized` notification
4. Only then can the client send requests like `tools/list` or `tools/call`

Simple echo commands bypassing this sequence will fail with "Received request before initialization was complete". Use the test script above for proper testing.

### Using the Token for Git Operations

Once you have the token, you can use it for various Git operations:

#### Clone a repository:
```bash
git clone https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
```

#### Clone a specific branch:
```bash
git clone -b feature-branch https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
```

#### Push to a repository:
```bash
cd private-repo
# Make some changes
git add .
git commit -m "Update files"
git push https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git main
```

#### Pull updates:
```bash
git pull https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git main
```

#### Fetch remote branches:
```bash
git fetch https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
```

#### Set as remote URL:
```bash
git remote set-url origin https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
# Now you can use regular git push/pull commands
git push origin main
```

### Using the Token for GitHub API Operations

The token can also be used with GitHub's REST API for various operations beyond Git commands:

#### Create an Issue:
```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ghs_tokenhere" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/fictional-org/private-repo/issues \
  -d '{"title":"Found a bug","body":"Description of the issue","labels":["bug"]}'
```

#### Create a Pull Request:
```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ghs_tokenhere" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/fictional-org/private-repo/pulls \
  -d '{"title":"Amazing new feature","body":"Please pull these changes","head":"feature-branch","base":"main"}'
```

#### Add a Comment to an Issue:
```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ghs_tokenhere" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/fictional-org/private-repo/issues/1/comments \
  -d '{"body":"This is a comment on the issue"}'
```

#### List Repository Contents:
```bash
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ghs_tokenhere" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/fictional-org/private-repo/contents/path/to/directory
```

#### Download a File from Private Repository:
```bash
curl -H "Authorization: Bearer ghs_tokenhere" \
  -H "Accept: application/vnd.github.v3.raw" \
  -o downloaded-file.txt \
  -L https://api.github.com/repos/fictional-org/private-repo/contents/path/to/file.txt
```

#### Get Repository Information:
```bash
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ghs_tokenhere" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/fictional-org/private-repo
```

#### List Pull Requests:
```bash
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ghs_tokenhere" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/fictional-org/private-repo/pulls
```

#### Create a Release:
```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ghs_tokenhere" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/fictional-org/private-repo/releases \
  -d '{"tag_name":"v1.0.0","name":"Release v1.0.0","body":"Description of the release"}'
```

## End-to-End Example

### Example 1: Clone a Repository

1. Pull the pre-built image:
```bash
docker pull ghcr.io/legido-ai/mcp-github-app-auth:latest
```

2. Get a GitHub token:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_token", "arguments": {"owner": "fictional-org", "repo": "private-repo"}}}' | \
  docker run -i --rm \
  -e GITHUB_APP_ID="$GITHUB_APP_ID" \
  -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" \
  -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" \
  ghcr.io/legido-ai/mcp-github-app-auth:latest
```

3. Use the returned token to clone the repository:
```bash
# Extract the token from the response (example shows ghs_tokenhere)
git clone https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
```

### Example 2: Clone, Modify, and Push

1. Get a GitHub token:
```bash
TOKEN=$(echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_token", "arguments": {"owner": "fictional-org", "repo": "private-repo"}}}' | \
  docker run -i --rm \
  -e GITHUB_APP_ID="$GITHUB_APP_ID" \
  -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" \
  -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" \
  ghcr.io/legido-ai/mcp-github-app-auth:latest | \
  jq -r '.result.content[0].text' | grep -oP 'ghs_\w+')
```

2. Clone the repository:
```bash
git clone https://x-access-token:$TOKEN@github.com/fictional-org/private-repo.git
cd private-repo
```

3. Make changes and push:
```bash
echo "# New content" >> README.md
git add README.md
git commit -m "Update README"
git push https://x-access-token:$TOKEN@github.com/fictional-org/private-repo.git main
```

### Example 3: Using Token with Multiple Operations

```bash
# Get token
TOKEN=$(echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_token", "arguments": {"owner": "fictional-org", "repo": "private-repo"}}}' | \
  docker run -i --rm \
  -e GITHUB_APP_ID="$GITHUB_APP_ID" \
  -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" \
  -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" \
  ghcr.io/legido-ai/mcp-github-app-auth:latest | \
  jq -r '.result.content[0].text' | grep -oP 'ghs_\w+')

# Clone repository
git clone https://x-access-token:$TOKEN@github.com/fictional-org/private-repo.git
cd private-repo

# Set remote URL with token for subsequent operations
git remote set-url origin https://x-access-token:$TOKEN@github.com/fictional-org/private-repo.git

# Now you can use regular git commands
git pull origin main
git push origin main
git fetch --all
```

## Integration with Claude Desktop

### ⚠️ CRITICAL: Variable Expansion Does Not Work

**Claude Desktop/Code does NOT support environment variable expansion in configuration files.**

This is a fundamental limitation of Claude's configuration system. If you try to use variables like `$GITHUB_APP_ID`, Claude will treat them as **literal strings**, not as references to environment variables.

**What This Means:**
- ❌ `GITHUB_APP_ID=$GITHUB_APP_ID` → Claude passes the literal string `"$GITHUB_APP_ID"` to Docker
- ❌ This causes authentication to fail with errors like "Could not parse the provided public key"
- ❌ The MCP server receives invalid credentials and cannot authenticate with GitHub

**Why This Happens:**
Claude's JSON configuration parser does not perform shell-style variable substitution. The `$VARIABLE` syntax is passed unchanged to the underlying command, causing the Docker container to receive the literal string instead of the actual credential values.

### ❌ This Configuration WILL NOT WORK:
```json
{
  "projects": {
    "/path/to/your/project": {
      "mcpServers": {
        "github": {
          "command": "docker",
          "args": [
            "run",
            "-i",
            "--rm",
            "-e",
            "GITHUB_APP_ID=$GITHUB_APP_ID",    ← Passed as literal "$GITHUB_APP_ID"
            "-e",
            "GITHUB_PRIVATE_KEY=$GITHUB_PRIVATE_KEY",    ← Passed as literal string
            "-e",
            "GITHUB_INSTALLATION_ID=$GITHUB_INSTALLATION_ID",    ← Not expanded
            "ghcr.io/legido-ai/mcp-github-app-auth:latest"
          ]
        }
      }
    }
  }
}
```

**Result:** Authentication fails because the MCP receives literal strings instead of your actual credentials.

### Option 1: Manual Configuration (Not Recommended)

You can manually edit `~/.claude.json` with hardcoded values, but this is **not recommended** for security reasons:

```json
{
  "projects": {
    "/path/to/your/project": {
      "mcpServers": {
        "github": {
          "command": "docker",
          "args": [
            "run",
            "-i",
            "--rm",
            "-e",
            "GITHUB_APP_ID=123456",
            "-e",
            "GITHUB_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\n...",
            "-e",
            "GITHUB_INSTALLATION_ID=78910",
            "ghcr.io/legido-ai/mcp-github-app-auth:latest"
          ]
        }
      }
    }
  }
}
```

### ✅ Option 2: Automated Setup Script (Recommended)

**Why You Need This Script:**

Since Claude cannot expand variables, you need an external script to:
1. Read your environment variables (`$GITHUB_APP_ID`, etc.)
2. Extract their actual values
3. Write those literal values into Claude's `~/.claude.json` configuration file

This script automates the process and is the **recommended solution** for setting up the MCP server with Claude.

**The Script:**

This script is available in the [docker-claude-code repository](https://github.com/legido-ai/docker-claude-code/blob/main/utils/setup-mcp-github.sh) or can be copied from below:

```bash
#!/bin/bash
#
# Setup script for configuring GitHub MCP server in Claude Code
# This script properly expands environment variables when adding the MCP server configuration
#

set -e

echo "Configuring GitHub MCP server for Claude Code..."

# Check if required environment variables are set
if [ -z "$GITHUB_APP_ID" ] || [ -z "$GITHUB_INSTALLATION_ID" ] || [ -z "$GITHUB_PRIVATE_KEY" ]; then
    echo "ERROR: Missing required environment variables!"
    echo "Please ensure the following environment variables are set:"
    echo "  - GITHUB_APP_ID"
    echo "  - GITHUB_INSTALLATION_ID"
    echo "  - GITHUB_PRIVATE_KEY"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is required but not found in PATH"
    exit 1
fi

# Ensure .claude.json exists
if [ ! -f "$HOME/.claude.json" ]; then
    echo "Creating $HOME/.claude.json..."
    echo '{}' > "$HOME/.claude.json"
fi

# Use Python to safely update the JSON configuration with expanded environment variables
python3 << 'EOFPYTHON'
import json
import os
import sys

config_path = os.path.expanduser("~/.claude.json")

# Read the current config
try:
    with open(config_path, "r") as f:
        config = json.load(f)
except Exception as e:
    print(f"ERROR: Failed to read {config_path}: {e}", file=sys.stderr)
    sys.exit(1)

# Get environment variables with actual values
github_app_id = os.environ.get("GITHUB_APP_ID")
github_installation_id = os.environ.get("GITHUB_INSTALLATION_ID")
github_private_key = os.environ.get("GITHUB_PRIVATE_KEY")

if not all([github_app_id, github_installation_id, github_private_key]):
    print("ERROR: Missing required environment variables", file=sys.stderr)
    sys.exit(1)

# Create MCP server configuration with expanded values
mcp_config = {
    "command": "docker",
    "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        f"GITHUB_APP_ID={github_app_id}",
        "-e",
        f"GITHUB_PRIVATE_KEY={github_private_key}",
        "-e",
        f"GITHUB_INSTALLATION_ID={github_installation_id}",
        "ghcr.io/legido-ai/mcp-github-app-auth:latest"
    ]
}

# Get current working directory
cwd = os.getcwd()

# Initialize nested structure if needed
if "projects" not in config:
    config["projects"] = {}
if cwd not in config["projects"]:
    config["projects"][cwd] = {}
if "mcpServers" not in config["projects"][cwd]:
    config["projects"][cwd]["mcpServers"] = {}

# Add/update the github MCP server
config["projects"][cwd]["mcpServers"]["github"] = mcp_config

# Create backup
backup_path = f"{config_path}.backup"
try:
    with open(config_path, "r") as f:
        with open(backup_path, "w") as b:
            b.write(f.read())
except Exception:
    pass  # Ignore backup errors

# Write back the updated config
try:
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✓ MCP configuration updated successfully for project: {cwd}")
    print(f"✓ Backup saved to: {backup_path}")
except Exception as e:
    print(f"ERROR: Failed to write {config_path}: {e}", file=sys.stderr)
    sys.exit(1)

EOFPYTHON

echo ""
echo "GitHub MCP server configured successfully!"
echo ""
echo "To verify the configuration, run:"
echo "  claude mcp list"
echo ""
echo "NOTE: This configuration uses expanded environment variable values."
echo "If you change your GitHub App credentials, you must run this script again."
```

**Step-by-Step Setup Instructions:**

1. **Save the script** as `setup-mcp-github.sh`

2. **Make it executable:**
   ```bash
   chmod +x setup-mcp-github.sh
   ```

3. **Set your environment variables** with your actual GitHub App credentials:
   ```bash
   export GITHUB_APP_ID="123456"
   export GITHUB_INSTALLATION_ID="78910"
   export GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
   MIIEpAIBAAKCAQEA...
   -----END RSA PRIVATE KEY-----"
   ```

4. **Run the setup script:**
   ```bash
   ./setup-mcp-github.sh
   ```

   The script will:
   - ✓ Validate that all required environment variables are set
   - ✓ Read the actual values from your environment
   - ✓ Create/update `~/.claude.json` with the literal values (not variable references)
   - ✓ Create a backup of your existing configuration

5. **Verify the configuration:**
   ```bash
   claude mcp list
   ```

   You should see:
   ```
   ✓ github: docker run -i --rm ... ghcr.io/legido-ai/mcp-github-app-auth:latest - Connected
   ```

**Important Notes:**
- The script writes the **actual credential values** (not `$VARIABLE` references) into `~/.claude.json`
- If you change your GitHub App credentials, you must run this script again to update the configuration
- The script creates a backup at `~/.claude.json.backup` before making changes

## Integration with Google Gemini CLI

**IMPORTANT:** Google Gemini CLI also does not support environment variable expansion in configuration files. Variables like `$GITHUB_APP_ID` will be passed as literal strings, not their values.

You must manually edit your Gemini CLI `settings.json` (located at `~/.gemini/settings.json`) with the actual expanded values:

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
        "GITHUB_APP_ID=123456",
        "-e",
        "GITHUB_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\n...",
        "-e",
        "GITHUB_INSTALLATION_ID=78910",
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

## Troubleshooting

### Common Authentication Errors

#### Error: "Could not parse the provided public key"

**Symptom:**
```
ERROR: Could not parse the provided public key
Failed to get installation token: 401 ...
```

**Cause:**
This error occurs when Claude passes literal variable names (like `"$GITHUB_PRIVATE_KEY"`) to the MCP server instead of the actual private key value.

**Solution:**
1. ✅ Use the [automated setup script](#-option-2-automated-setup-script-recommended) to configure Claude
2. ❌ Do NOT use `$VARIABLE` syntax in `~/.claude.json`
3. ✅ Ensure your `~/.claude.json` contains the actual credential values, not variable references

**How to Verify:**
```bash
# Check what's actually in your configuration
cat ~/.claude.json | grep -A 5 "GITHUB_PRIVATE_KEY"
```

If you see `"$GITHUB_PRIVATE_KEY"` or `"GITHUB_PRIVATE_KEY=$GITHUB_PRIVATE_KEY"`, the variable was not expanded. Re-run the setup script.

#### Error: "Missing required environment variables"

**Symptom:**
```
ERROR: Missing GITHUB_APP_ID / GITHUB_INSTALLATION_ID / GITHUB_PRIVATE_KEY
```

**Cause:**
The MCP server is not receiving the required environment variables.

**Solution:**
1. Verify environment variables are set before running the setup script:
   ```bash
   echo $GITHUB_APP_ID
   echo $GITHUB_INSTALLATION_ID
   echo $GITHUB_PRIVATE_KEY | head -1
   ```
2. If any are empty, set them and re-run the setup script
3. Ensure you're setting variables in the same shell session where you run the setup script

#### Error: MCP Server Shows as "Disconnected"

**Symptom:**
```
✗ github: docker run -i --rm ... ghcr.io/legido-ai/mcp-github-app-auth:latest - Disconnected
```

**Possible Causes and Solutions:**

1. **Docker is not running:**
   ```bash
   docker ps  # Should not error
   ```

2. **Docker image is not available:**
   ```bash
   docker pull ghcr.io/legido-ai/mcp-github-app-auth:latest
   ```

3. **Invalid credentials in configuration:**
   - Re-run the setup script with correct credentials
   - Verify credentials work by testing manually:
     ```bash
     echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_token", "arguments": {"owner": "your-org", "repo": "your-repo"}}}' | \
       docker run -i --rm \
       -e GITHUB_APP_ID="$GITHUB_APP_ID" \
       -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" \
       -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" \
       ghcr.io/legido-ai/mcp-github-app-auth:latest
     ```

#### Error: "401 Unauthorized" from GitHub API

**Symptom:**
```
Failed to get installation token: 401 {"message":"Bad credentials",...}
```

**Possible Causes:**

1. **Incorrect GitHub App ID:**
   - Verify at: `https://github.com/settings/apps/your-app`
   - The App ID is shown at the top of the settings page

2. **Wrong Private Key:**
   - Regenerate if needed at: `https://github.com/settings/apps/your-app`
   - Scroll to "Private keys" section
   - Ensure you're using the complete key including headers:
     ```
     -----BEGIN RSA PRIVATE KEY-----
     ...
     -----END RSA PRIVATE KEY-----
     ```

3. **Incorrect Installation ID:**
   - Find it in the installation URL: `https://github.com/settings/installations/INSTALLATION_ID`
   - Or via API: `curl -H "Authorization: Bearer <jwt_token>" https://api.github.com/app/installations`

#### How to Test Configuration Manually

To verify your setup works before configuring Claude:

```bash
# 1. Set environment variables
export GITHUB_APP_ID="your-app-id"
export GITHUB_INSTALLATION_ID="your-installation-id"
export GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----"

# 2. Test the MCP server directly
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_token", "arguments": {"owner": "legido-ai", "repo": "tasks"}}}' | \
  docker run -i --rm \
  -e GITHUB_APP_ID="$GITHUB_APP_ID" \
  -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" \
  -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" \
  ghcr.io/legido-ai/mcp-github-app-auth:latest

# 3. You should get a response with a token like:
# {"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"GitHub token for legido-ai/tasks: ghs_..."}]}}
```

If this works, your credentials are correct and you can proceed with Claude configuration.

## Testing

Run tests with:
```bash
python3 -m pytest tests/ -v
```

## Security Notes

- Installation tokens expire after approximately 1 hour
- The server caches and refreshes tokens automatically
