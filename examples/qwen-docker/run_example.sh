#!/bin/bash

# Script to demonstrate running the MCP GitHub App server with Qwen integration

set -e  # Exit on any error

echo "MCP GitHub App Server with Qwen Integration Example"
echo "==================================================="

# Check if required environment variables are set
if [ -z "$GITHUB_APP_ID" ] || [ -z "$GITHUB_PRIVATE_KEY" ] || [ -z "$GITHUB_INSTALLATION_ID" ]; then
    echo "Error: Required environment variables not set."
    echo "Please set GITHUB_APP_ID, GITHUB_PRIVATE_KEY, and GITHUB_INSTALLATION_ID"
    echo "Example:"
    echo "  export GITHUB_APP_ID=your_app_id"
    echo "  export GITHUB_PRIVATE_KEY='-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----'"
    echo "  export GITHUB_INSTALLATION_ID=your_installation_id"
    exit 1
fi

echo "Environment variables are set. Proceeding with example..."

# Build the Docker image
echo -e "\n1. Building Docker image..."
docker build -t mcp-github-app-server .. 

# Run the container with docker-compose
echo -e "\n2. Starting MCP GitHub App server container..."
docker-compose -f docker-compose.yml up -d

echo -e "\n3. Server is running! To test the connection, you can:"
echo "   - Check logs with: docker logs mcp-github-app-server"
echo "   - Verify the service is running: docker ps"
echo "   - Connect Qwen to use this server via MCP protocol"

echo -e "\n4. To stop the server:"
echo "   docker-compose -f docker-compose.yml down"

echo -e "\nExample setup complete!"