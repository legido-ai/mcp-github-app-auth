#!/usr/bin/env python3
"""
Quick test script for MCP server that handles initialization automatically.
Pipe this to the MCP server to test it.

Usage:
    python quick_test.py list | docker run -i --rm -e GITHUB_APP_ID=... ghcr.io/legido-ai/mcp-github-app-auth
    python quick_test.py get-token OWNER REPO | docker run -i --rm -e GITHUB_APP_ID=... ghcr.io/legido-ai/mcp-github-app-auth
"""

import sys
import json

def send_message(msg):
    """Print a JSON-RPC message."""
    print(json.dumps(msg), flush=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_test.py [list|get-token OWNER REPO]", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]

    # Step 1: Send initialize request
    send_message({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {
                "name": "QuickTest",
                "version": "1.0.0"
            }
        }
    })

    # Step 2: Send initialized notification (no need to wait for response in one-way pipe)
    send_message({
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    })

    # Step 3: Send the actual request
    if mode == "list":
        send_message({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        })
    elif mode == "get-token":
        if len(sys.argv) != 4:
            print("Error: get-token requires OWNER and REPO", file=sys.stderr)
            print("Usage: python quick_test.py get-token OWNER REPO", file=sys.stderr)
            sys.exit(1)

        owner = sys.argv[2]
        repo = sys.argv[3]

        send_message({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_token",
                "arguments": {
                    "owner": owner,
                    "repo": repo
                }
            }
        })
    else:
        print(f"Error: Unknown command '{mode}'", file=sys.stderr)
        print("Usage: python quick_test.py [list|get-token OWNER REPO]", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
