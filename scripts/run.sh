#!/bin/bash

# Example launcher for the MCP GitHub App server
# This script sets up the environment and runs the server

set -e

# Check if required environment variables are set
if [ -z "$GITHUB_APP_ID" ] || [ -z "$GITHUB_PRIVATE_KEY" ] || [ -z "$GITHUB_INSTALLATION_ID" ]; then
    echo "Error: Required environment variables GITHUB_APP_ID, GITHUB_PRIVATE_KEY, and GITHUB_INSTALLATION_ID must be set"
    exit 1
fi

# Change to the project directory
cd "$(dirname "$0")/.."

# Run the server
python -m mcp_github_app.server