import logging
import asyncio
import tempfile
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from pydantic import BaseModel, Field
from . import git_ops

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Models ----
class GetTokenArgs(BaseModel):
    owner: str = Field(description="GitHub repository owner")
    repo: str = Field(description="GitHub repository name")
    dest_dir: str | None = Field(default=None, description="Optional destination directory for clone")
    branch: str | None = Field(default=None, description="Optional branch to clone")


# Create the server instance
app = Server("github-app")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_token",
            description="Obtain a temporary GitHub token for accessing private repositories using GitHub App authentication. This token can be used with git commands to clone repositories.",
            inputSchema=GetTokenArgs.model_json_schema()
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
    """Handle tool calls"""
    if name == "get_token":
        # Validate arguments
        args = GetTokenArgs.model_validate(arguments)

        # Use provided dest_dir or create a temporary one
        dest_dir = args.dest_dir or tempfile.mkdtemp()

        # Clone the repository and get the token
        result = await asyncio.get_event_loop().run_in_executor(
            None, git_ops.clone_repo, args.owner, args.repo, dest_dir, args.branch
        )

        # Extract the token from the result
        if isinstance(result, dict) and "github_token" in result:
            token = result["github_token"]
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully cloned {args.owner}/{args.repo}. GitHub token: {token}"
                )
            ]
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"Failed to clone repository: {result}"
                )
            ]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())