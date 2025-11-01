#!/bin/bash

set -e

# Build the docker image
docker build . -t localhost/test

# Test the MCP server
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | docker run -i --rm \
  -e GITHUB_APP_ID="$GITHUB_APP_ID" \
  -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" \
  -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" \
  localhost/test &

sleep 5

docker kill $(docker ps -q)
