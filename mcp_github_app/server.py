import logging
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from pydantic import BaseModel, Field
from .auth import get_installation_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Models ----
class GetTokenArgs(BaseModel):
    owner: str = Field(description="GitHub repository owner")
    repo: str = Field(description="GitHub repository name")


# Create the server instance
app = Server("github-app")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_token",
            description=(
                "Obtain a temporary GitHub authentication token (~1 hour validity) for a repository. "
                "This token can be used for:\n"
                "1. Git operations: git clone, push, pull, fetch\n"
                "   Format: https://x-access-token:<TOKEN>@github.com/<OWNER>/<REPO>.git\n"
                "2. GitHub REST API calls: create issues, PRs, manage repos, etc.\n"
                "   Format: Authorization: Bearer <TOKEN>\n"
                "The same token works for all Git and API operations until it expires."
            ),
            inputSchema=GetTokenArgs.model_json_schema()
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
    """Handle tool calls"""
    if name == "get_token":
        # Validate arguments
        args = GetTokenArgs.model_validate(arguments)

        # Get the GitHub installation token
        # This token can be used for:
        # - Git operations: git clone, push, pull, fetch with https://x-access-token:<TOKEN>@github.com/<OWNER>/<REPO>.git
        # - GitHub API operations: curl with Authorization: Bearer <TOKEN>
        token, expiry = get_installation_token()

        return [
            types.TextContent(
                type="text",
                text=f"GitHub token for {args.owner}/{args.repo}: {token}"
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