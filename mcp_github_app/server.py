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

class BranchArgs(BaseModel):
    owner: str
    repo: str
    new_branch: str
    from_ref: str = "heads/main"

class PushArgs(BaseModel):
    cwd: str
    remote: str = "origin"
    branch: str = "main"

class PRCreateArgs(BaseModel):
    owner: str
    repo: str
    title: str
    head: str
    base: str = "main"
    body: str | None = None

class PRMergeArgs(BaseModel):
    owner: str
    repo: str
    number: int
    merge_method: str = "squash"
    commit_title: str | None = None
    commit_message: str | None = None


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
        # Store the tool definitions
        self._tools = {
            "clone_repo": Tool(
                name="clone_repo",
                description="Clone a GitHub repository",
                inputSchema=CloneArgs.model_json_schema(),
            ),
            "create_branch": Tool(
                name="create_branch",
                description="Create a new branch in a GitHub repository",
                inputSchema=BranchArgs.model_json_schema(),
            ),
            "push": Tool(
                name="push",
                description="Push changes to a GitHub repository",
                inputSchema=PushArgs.model_json_schema(),
            ),
            "create_pull_request": Tool(
                name="create_pull_request",
                description="Create a pull request in a GitHub repository",
                inputSchema=PRCreateArgs.model_json_schema(),
            ),
            "merge_pull_request": Tool(
                name="merge_pull_request",
                description="Merge a pull request in a GitHub repository",
                inputSchema=PRMergeArgs.model_json_schema(),
            ),
        }

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Handle tool calls"""
        if name == "clone_repo":
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
        elif name == "create_branch":
            args = BranchArgs.model_validate(arguments)
            return await asyncio.get_event_loop().run_in_executor(
                None, gh_api.create_branch, args.owner, args.repo, args.new_branch, args.from_ref
            )
        elif name == "push":
            args = PushArgs.model_validate(arguments)
            return await asyncio.get_event_loop().run_in_executor(
                None, git_ops.push, args.cwd, args.remote, args.branch
            )
        elif name == "create_pull_request":
            args = PRCreateArgs.model_validate(arguments)
            return await asyncio.get_event_loop().run_in_executor(
                None, gh_api.create_pull_request, args.owner, args.repo, args.title, args.head, args.base, args.body
            )
        elif name == "merge_pull_request":
            args = PRMergeArgs.model_validate(arguments)
            return await asyncio.get_event_loop().run_in_executor(
                None, gh_api.merge_pull_request, args.owner, args.repo, args.number, args.merge_method, args.commit_title, args.commit_message
            )
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
                # After successful clone, list the directory to verify if dest_dir is provided
                if method == "clone_repo":
                    dest_dir = params.get("dest_dir")
                    if dest_dir:
                        try:
                            cloned_files = os.listdir(dest_dir)
                            response = {"jsonrpc": "2.0", "id": request_id, "result": {"clone_output": result, "cloned_files": cloned_files}}
                        except:
                            # If we can't list the directory (e.g., temporary dir was used), just return the result
                            response = {"jsonrpc": "2.0", "id": request_id, "result": result}
                    else:
                        # When dest_dir is not provided, just return the result (which should contain the token)
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