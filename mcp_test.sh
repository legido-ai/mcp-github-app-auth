#!/bin/bash
# Simple test wrapper for MCP GitHub App Auth server
# This handles the MCP initialization handshake automatically

set -e

# Check if we're testing via Docker or local
MODE="${1:-list}"
OWNER="${2:-}"
REPO="${3:-}"

# Determine the command to run the server
if [ -n "$USE_DOCKER" ]; then
    SERVER_CMD="docker run -i --rm \
        -e GITHUB_APP_ID=\"$GITHUB_APP_ID\" \
        -e GITHUB_PRIVATE_KEY=\"$GITHUB_PRIVATE_KEY\" \
        -e GITHUB_INSTALLATION_ID=\"$GITHUB_INSTALLATION_ID\" \
        ghcr.io/legido-ai/mcp-github-app-auth:latest"
else
    SERVER_CMD="python -m mcp_github_app.server"
fi

# Create a named pipe for bidirectional communication
PIPE_IN=$(mktemp -u)
PIPE_OUT=$(mktemp -u)
mkfifo "$PIPE_IN" "$PIPE_OUT"

# Cleanup on exit
cleanup() {
    rm -f "$PIPE_IN" "$PIPE_OUT"
    [ -n "$SERVER_PID" ] && kill "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT

# Start the server in background
eval "$SERVER_CMD" < "$PIPE_IN" > "$PIPE_OUT" 2>/dev/null &
SERVER_PID=$!

# Open pipes for reading and writing
exec 3>"$PIPE_IN"  # Write to server
exec 4<"$PIPE_OUT" # Read from server

# Function to send JSON-RPC message
send_message() {
    echo "$1" >&3
}

# Function to read JSON-RPC response
read_response() {
    read -r -u 4 response
    echo "$response"
}

# Step 1: Send initialize request
send_message '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"TestClient","version":"1.0.0"}}}'

# Step 2: Read initialize response
INIT_RESPONSE=$(read_response)
if echo "$INIT_RESPONSE" | grep -q '"error"'; then
    echo "Initialization failed: $INIT_RESPONSE" >&2
    exit 1
fi

# Step 3: Send initialized notification
send_message '{"jsonrpc":"2.0","method":"notifications/initialized"}'

# Step 4: Send the actual request based on mode
case "$MODE" in
    list)
        send_message '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
        RESPONSE=$(read_response)
        echo "$RESPONSE" | jq '.'
        ;;
    get-token)
        if [ -z "$OWNER" ] || [ -z "$REPO" ]; then
            echo "Error: get-token requires OWNER and REPO arguments" >&2
            echo "Usage: $0 get-token OWNER REPO" >&2
            exit 1
        fi
        send_message "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\",\"params\":{\"name\":\"get_token\",\"arguments\":{\"owner\":\"$OWNER\",\"repo\":\"$REPO\"}}}"
        RESPONSE=$(read_response)
        echo "$RESPONSE" | jq -r '.result.content[0].text'
        ;;
    *)
        echo "Error: Unknown mode '$MODE'" >&2
        echo "Usage: $0 [list|get-token] [OWNER] [REPO]" >&2
        exit 1
        ;;
esac

# Close file descriptors
exec 3>&-
exec 4<&-

exit 0
