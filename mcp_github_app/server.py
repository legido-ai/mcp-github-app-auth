import logging
from mcp.server import Server
from mcp.types import Tool
from pydantic import BaseModel
from typing import Any, List, Optional
import asyncio
import io
from . import git_ops, gh_api

# ---- Models ----
from typing import Optional

class CloneArgs(BaseModel):
    owner: str
    repo: str
    dest_dir: Optional[str] = None
    branch: str | None = None


# Create the server by subclassing
class GitHubAppServer(Server):
    def __init__(self):
        super().__init__(
            name="github-app",
            version="0.1.0",
            instructions="A server for performing GitHub operations using GitHub App authentication"
        )
        logging.basicConfig(level=logging.INFO)
        logging.info("Initializing GitHubAppServer")
        # Store the tool definitions - only keeping get_token
        self._tools = {
            "get_token": Tool(
                name="get_token",
                description="Obtain a temporary GitHub token for accessing private repositories using GitHub App authentication. This token can be used with git commands to clone repositories.",
                inputSchema=CloneArgs.model_json_schema(),
            ),
        }

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Handle tool calls"""
        if name == "get_token":
            # Handle the case where dest_dir might not be provided by using a temporary directory
            import tempfile
            validated_args = CloneArgs.model_validate(arguments)
            
            # Use provided dest_dir or create a temporary one
            dest_dir = validated_args.dest_dir or tempfile.mkdtemp()
            
            clone_result = await asyncio.get_event_loop().run_in_executor(
                None, git_ops.clone_repo, validated_args.owner, validated_args.repo, dest_dir, validated_args.branch
            )
            # Extract the token from the clone result and return it
            if isinstance(clone_result, dict) and "github_token" in clone_result:
                return {"github_token": clone_result["github_token"]}
            else:
                return clone_result
        else:
            raise ValueError(f"Unknown tool: {name}")

    def list_tools(self) -> List[Tool]:
        """Return the list of available tools"""
        logging.info("Listing tools")
        return list(self._tools.values())


# Create the server instance
server = GitHubAppServer()


if __name__ == "__main__":
    import sys
    import json
    import asyncio
    import os

    async def main():
        request_str = sys.stdin.read()
        try:
            request = json.loads(request_str)
            method = request["method"]
            params = request["params"]
            request_id = request.get("id", None)

            # Handle tools/list method specifically
            if method == "tools/list":
                tools = server.list_tools()
                # Convert tools to the proper format for MCP
                tool_list = []
                for tool in tools:
                    tool_dict = {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    # Add title if available
                    if hasattr(tool, 'title') and tool.title:
                        tool_dict["title"] = tool.title
                    tool_list.append(tool_dict)
                
                response = {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tool_list}}
            else:
                result = await server.call_tool(method, params)
                # After successful token retrieval, just return the result
                if method == "get_token":
                    response = {"jsonrpc": "2.0", "id": request_id, "result": result}
                else:
                    response = {"jsonrpc": "2.0", "id": request_id, "result": result}
            print(json.dumps(response))
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id", None) if 'request' in locals() else None,
                "error": {"code": -32000, "message": str(e)}
            }
            print(json.dumps(error_response), file=sys.stderr)
            sys.exit(1)

    asyncio.run(main())