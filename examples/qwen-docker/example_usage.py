"""
Example script demonstrating how to use the MCP GitHub App server with Qwen-like functionality.

This script shows how to programmatically interact with the GitHub App authentication server,
similar to how Qwen would use it via the Model Context Protocol.
"""
import os
import asyncio
from mcp_github_app.server import GitHubAppServer


async def example_usage():
    """Demonstrate the usage of the GitHub App server."""
    # Create server instance
    server = GitHubAppServer()
    
    print("MCP GitHub App Server Example")
    print("=" * 40)
    
    # Example 1: Clone a repository
    print("\n1. Cloning a repository...")
    try:
        result = await server.call_tool('clone_repo', {
            'owner': 'your-org',
            'repo': 'your-repo',
            'dest_dir': '/tmp/example-clone',
            'branch': 'main'
        })
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 2: Create a branch
    print("\n2. Creating a branch...")
    try:
        result = await server.call_tool('create_branch', {
            'owner': 'your-org',
            'repo': 'your-repo',
            'new_branch': 'feature-new-feature',
            'from_ref': 'heads/main'
        })
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 3: Create a pull request
    print("\n3. Creating a pull request...")
    try:
        result = await server.call_tool('create_pull_request', {
            'owner': 'your-org',
            'repo': 'your-repo',
            'title': 'Add new feature',
            'head': 'feature-new-feature',
            'base': 'main',
            'body': 'This PR adds a new feature to the project'
        })
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 4: Push changes
    print("\n4. Pushing changes...")
    try:
        result = await server.call_tool('push', {
            'cwd': '/tmp/example-clone',
            'remote': 'origin',
            'branch': 'main'
        })
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\nExample completed!")


if __name__ == "__main__":
    # Set environment variables for GitHub App (these would normally come from environment)
    os.environ['GITHUB_APP_ID'] = os.environ.get('GITHUB_APP_ID', 'your_app_id_here')
    os.environ['GITHUB_PRIVATE_KEY'] = os.environ.get('GITHUB_PRIVATE_KEY', 'your_private_key_here')
    os.environ['GITHUB_INSTALLATION_ID'] = os.environ.get('GITHUB_INSTALLATION_ID', 'your_installation_id_here')
    
    # Run the example
    asyncio.run(example_usage())