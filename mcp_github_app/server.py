# mcp_github_app/server.py
from mcp.server import Server
from mcp.types import Tool
from pydantic import BaseModel
from typing import Any, List
import asyncio
from . import git_ops, gh_api

# ---- Models ----
class CloneArgs(BaseModel):
    owner: str
    repo: str
    dest_dir: str
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
            args = CloneArgs.model_validate(arguments)
            return await asyncio.get_event_loop().run_in_executor(
                None, git_ops.clone_repo, args.owner, args.repo, args.dest_dir, args.branch
            )
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
        return list(self._tools.values())


# Create the server instance
server = GitHubAppServer()

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    stdio_server()(server)