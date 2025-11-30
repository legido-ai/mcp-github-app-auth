#!/usr/bin/env python3
"""
Test script for MCP GitHub App Auth server.

This script implements a minimal MCP client that:
1. Sends the initialization sequence
2. Lists available tools
3. Optionally calls the get_token tool

Usage:
    python test_mcp_server.py [--get-token OWNER REPO]
"""

import json
import sys
import subprocess
import argparse


def send_message(proc, message):
    """Send a JSON-RPC message to the server."""
    json_str = json.dumps(message) + '\n'
    proc.stdin.write(json_str)
    proc.stdin.flush()


def read_message(proc):
    """Read a JSON-RPC message from the server."""
    line = proc.stdout.readline()
    if not line:
        return None
    return json.loads(line)


def main():
    parser = argparse.ArgumentParser(description='Test MCP GitHub App Auth server')
    parser.add_argument('--get-token', nargs=2, metavar=('OWNER', 'REPO'),
                        help='Test get_token tool with owner and repo')
    args = parser.parse_args()

    # Start the server as a subprocess
    server_proc = subprocess.Popen(
        [sys.executable, '-m', 'mcp_github_app.server'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        # Step 1: Send initialize request
        print("1. Sending initialize request...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {
                    "name": "TestClient",
                    "version": "1.0.0"
                }
            }
        }
        send_message(server_proc, init_request)

        # Step 2: Read initialize response
        print("2. Reading initialize response...")
        init_response = read_message(server_proc)
        if not init_response:
            print("ERROR: No response from server")
            return 1

        print(f"   Response: {json.dumps(init_response, indent=2)}")

        if "error" in init_response:
            print(f"ERROR: Initialization failed: {init_response['error']}")
            return 1

        # Step 3: Send initialized notification
        print("3. Sending initialized notification...")
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        send_message(server_proc, initialized_notif)

        # Step 4: List tools
        print("4. Sending tools/list request...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        send_message(server_proc, tools_request)

        print("5. Reading tools/list response...")
        tools_response = read_message(server_proc)
        if not tools_response:
            print("ERROR: No response from server")
            return 1

        print(f"   Response: {json.dumps(tools_response, indent=2)}")

        if "error" in tools_response:
            print(f"ERROR: tools/list failed: {tools_response['error']}")
            return 1

        # Step 5: Optionally test get_token
        if args.get_token:
            owner, repo = args.get_token
            print(f"6. Testing get_token for {owner}/{repo}...")

            get_token_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_token",
                    "arguments": {
                        "owner": owner,
                        "repo": repo
                    }
                }
            }
            send_message(server_proc, get_token_request)

            print("7. Reading get_token response...")
            token_response = read_message(server_proc)
            if not token_response:
                print("ERROR: No response from server")
                return 1

            print(f"   Response: {json.dumps(token_response, indent=2)}")

            if "error" in token_response:
                print(f"ERROR: get_token failed: {token_response['error']}")
                return 1

        print("\n✓ All tests passed!")
        return 0

    finally:
        # Cleanup
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()


if __name__ == "__main__":
    sys.exit(main())
