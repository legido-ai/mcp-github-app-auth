"""Tests for the server module of mcp-github-app-auth."""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from pydantic import ValidationError

from mcp_github_app.server import GitHubAppServer, CloneArgs, BranchArgs, PushArgs, PRCreateArgs, PRMergeArgs


class TestServer(unittest.TestCase):
    """Test the server functionality."""
    
    def setUp(self):
        """Set up the server instance."""
        self.server = GitHubAppServer()

    def test_clone_args_validation(self):
        """Test CloneArgs Pydantic model validation."""
        # Valid arguments
        args = CloneArgs(owner='test-owner', repo='test-repo', dest_dir='/tmp/test')
        self.assertEqual(args.owner, 'test-owner')
        self.assertEqual(args.repo, 'test-repo')
        self.assertEqual(args.dest_dir, '/tmp/test')
        self.assertIsNone(args.branch)

        # Valid arguments with branch
        args = CloneArgs(owner='test-owner', repo='test-repo', dest_dir='/tmp/test', branch='develop')
        self.assertEqual(args.branch, 'develop')

        # Invalid arguments (missing required fields)
        with self.assertRaises(ValidationError):
            CloneArgs(owner='test-owner', dest_dir='/tmp/test')

    def test_branch_args_validation(self):
        """Test BranchArgs Pydantic model validation."""
        # Valid arguments
        args = BranchArgs(owner='test-owner', repo='test-repo', new_branch='new-branch')
        self.assertEqual(args.owner, 'test-owner')
        self.assertEqual(args.repo, 'test-repo')
        self.assertEqual(args.new_branch, 'new-branch')
        self.assertEqual(args.from_ref, 'heads/main')

        # Valid arguments with from_ref
        args = BranchArgs(owner='test-owner', repo='test-repo', new_branch='new-branch', from_ref='heads/develop')
        self.assertEqual(args.from_ref, 'heads/develop')

    def test_push_args_validation(self):
        """Test PushArgs Pydantic model validation."""
        # Valid arguments
        args = PushArgs(cwd='/tmp/test')
        self.assertEqual(args.cwd, '/tmp/test')
        self.assertEqual(args.remote, 'origin')
        self.assertEqual(args.branch, 'main')

        # Valid arguments with custom remote and branch
        args = PushArgs(cwd='/tmp/test', remote='upstream', branch='develop')
        self.assertEqual(args.remote, 'upstream')
        self.assertEqual(args.branch, 'develop')

    def test_pr_create_args_validation(self):
        """Test PRCreateArgs Pydantic model validation."""
        # Valid arguments
        args = PRCreateArgs(owner='test-owner', repo='test-repo', title='Test PR', head='feature-branch')
        self.assertEqual(args.owner, 'test-owner')
        self.assertEqual(args.repo, 'test-repo')
        self.assertEqual(args.title, 'Test PR')
        self.assertEqual(args.head, 'feature-branch')
        self.assertEqual(args.base, 'main')
        self.assertIsNone(args.body)

        # Valid arguments with all fields
        args = PRCreateArgs(
            owner='test-owner', 
            repo='test-repo', 
            title='Test PR', 
            head='feature-branch',
            base='develop',
            body='PR description'
        )
        self.assertEqual(args.base, 'develop')
        self.assertEqual(args.body, 'PR description')

    def test_pr_merge_args_validation(self):
        """Test PRMergeArgs Pydantic model validation."""
        # Valid arguments
        args = PRMergeArgs(owner='test-owner', repo='test-repo', number=1)
        self.assertEqual(args.owner, 'test-owner')
        self.assertEqual(args.repo, 'test-repo')
        self.assertEqual(args.number, 1)
        self.assertEqual(args.merge_method, 'squash')
        self.assertIsNone(args.commit_title)
        self.assertIsNone(args.commit_message)

        # Valid arguments with all fields
        args = PRMergeArgs(
            owner='test-owner',
            repo='test-repo',
            number=1,
            merge_method='merge',
            commit_title='Merge commit title',
            commit_message='Merge commit message'
        )
        self.assertEqual(args.merge_method, 'merge')
        self.assertEqual(args.commit_title, 'Merge commit title')
        self.assertEqual(args.commit_message, 'Merge commit message')

    @patch('mcp_github_app.git_ops.clone_repo')
    def test_call_tool_clone_repo_returns_token(self, mock_clone_repo):
        """Test that clone_repo tool returns only the GitHub token."""
        # Mock the clone_repo function to return a dictionary with github_token
        mock_clone_repo.return_value = {
            "clone_output": "Repository cloned successfully",
            "github_token": "ghs_testtoken12345"
        }
        
        # Call the tool
        result = asyncio.run(self.server.call_tool('clone_repo', {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'dest_dir': '/tmp/test'
        }))

        # Verify the function was called with correct arguments
        mock_clone_repo.assert_called_once_with('test-owner', 'test-repo', '/tmp/test', None)
        # Verify that the result is a dictionary containing only the github_token
        self.assertEqual(result, {"github_token": "ghs_testtoken12345"})

    @patch('mcp_github_app.git_ops.clone_repo')
    def test_call_tool_clone_repo(self, mock_clone_repo):
        """Test calling the clone_repo tool."""
        # Mock the clone_repo function to return a success message
        mock_clone_repo.return_value = "Repository cloned successfully"
        
        # Call the tool
        result = asyncio.run(self.server.call_tool('clone_repo', {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'dest_dir': '/tmp/test'
        }))

        # Verify the function was called with correct arguments
        mock_clone_repo.assert_called_once_with('test-owner', 'test-repo', '/tmp/test', None)
        self.assertEqual(result, "Repository cloned successfully")

    @patch('mcp_github_app.git_ops.clone_repo')
    def test_call_tool_clone_repo_with_branch(self, mock_clone_repo):
        """Test calling the clone_repo tool with branch parameter."""
        # Mock the clone_repo function to return a dictionary with github_token
        mock_clone_repo.return_value = {
            "clone_output": "Repository cloned successfully",
            "github_token": "ghs_testtoken12345"
        }
        
        # Call the tool
        result = asyncio.run(self.server.call_tool('clone_repo', {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'dest_dir': '/tmp/test',
            'branch': 'develop'
        }))

        # Verify the function was called with correct arguments
        mock_clone_repo.assert_called_once_with('test-owner', 'test-repo', '/tmp/test', 'develop')
        # Verify that the result is a dictionary containing only the github_token
        self.assertEqual(result, {"github_token": "ghs_testtoken12345"})

    @patch('mcp_github_app.git_ops.clone_repo')
    def test_call_tool_clone_repo_without_dest_dir(self, mock_clone_repo):
        """Test calling the clone_repo tool without dest_dir parameter."""
        # Mock the clone_repo function to return a dictionary with github_token
        mock_clone_repo.return_value = {
            "clone_output": "Repository cloned successfully",
            "github_token": "ghs_testtoken12345"
        }
        
        # Call the tool without dest_dir
        result = asyncio.run(self.server.call_tool('clone_repo', {
            'owner': 'test-owner',
            'repo': 'test-repo'
        }))

        # Verify the function was called with correct arguments (dest_dir would be filled in by the server logic)
        # Since the actual call happens inside run_in_executor with dynamically created temp dir, 
        # we just need to ensure it was called at all
        # The mock_clone_repo should have been called with some dest_dir value
        self.assertTrue(mock_clone_repo.called)
        # Verify that the result is a dictionary containing only the github_token
        self.assertEqual(result, {"github_token": "ghs_testtoken12345"})

    @patch('mcp_github_app.gh_api.create_branch')
    def test_call_tool_create_branch(self, mock_create_branch):
        """Test calling the create_branch tool."""
        # Mock the create_branch function to return a success message
        mock_create_branch.return_value = "Branch created successfully"
        
        # Call the tool
        result = asyncio.run(self.server.call_tool('create_branch', {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'new_branch': 'new-feature',
            'from_ref': 'heads/main'
        }))

        # Verify the function was called with correct arguments
        mock_create_branch.assert_called_once_with('test-owner', 'test-repo', 'new-feature', 'heads/main')
        self.assertEqual(result, "Branch created successfully")

    @patch('mcp_github_app.git_ops.push')
    def test_call_tool_push(self, mock_push):
        """Test calling the push tool."""
        # Mock the push function to return a success message
        mock_push.return_value = "Changes pushed successfully"
        
        # Call the tool
        result = asyncio.run(self.server.call_tool('push', {
            'cwd': '/tmp/test-repo',
            'remote': 'origin',
            'branch': 'main'
        }))

        # Verify the function was called with correct arguments
        mock_push.assert_called_once_with('/tmp/test-repo', 'origin', 'main')
        self.assertEqual(result, "Changes pushed successfully")

    @patch('mcp_github_app.gh_api.create_pull_request')
    def test_call_tool_create_pull_request(self, mock_create_pr):
        """Test calling the create_pull_request tool."""
        # Mock the create_pull_request function to return a success message
        mock_create_pr.return_value = "Pull request created successfully"
        
        # Call the tool
        result = asyncio.run(self.server.call_tool('create_pull_request', {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'title': 'New Feature',
            'head': 'feature-branch',
            'base': 'main',
            'body': 'Description of the new feature'
        }))

        # Verify the function was called with correct arguments
        mock_create_pr.assert_called_once_with('test-owner', 'test-repo', 'New Feature', 'feature-branch', 'main', 'Description of the new feature')
        self.assertEqual(result, "Pull request created successfully")

    @patch('mcp_github_app.gh_api.merge_pull_request')
    def test_call_tool_merge_pull_request(self, mock_merge_pr):
        """Test calling the merge_pull_request tool."""
        # Mock the merge_pull_request function to return a success message
        mock_merge_pr.return_value = "Pull request merged successfully"
        
        # Call the tool
        result = asyncio.run(self.server.call_tool('merge_pull_request', {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'number': 42,
            'merge_method': 'squash',
            'commit_title': 'Squash and merge commit',
            'commit_message': 'Merged PR #42'
        }))

        # Verify the function was called with correct arguments
        mock_merge_pr.assert_called_once_with('test-owner', 'test-repo', 42, 'squash', 'Squash and merge commit', 'Merged PR #42')
        self.assertEqual(result, "Pull request merged successfully")

    def test_call_tool_invalid_tool(self):
        """Test calling an invalid tool."""
        with self.assertRaises(ValueError) as context:
            asyncio.run(self.server.call_tool('invalid_tool', {}))
        
        self.assertEqual(str(context.exception), "Unknown tool: invalid_tool")

    def test_list_tools(self):
        """Test listing available tools."""
        tools = self.server.list_tools()
        
        # Check that we get the expected number of tools
        self.assertEqual(len(tools), 5)
        
        # Check that we have the expected tools
        tool_names = [tool.name for tool in tools]
        expected_tools = ['clone_repo', 'create_branch', 'push', 'create_pull_request', 'merge_pull_request']
        self.assertEqual(set(tool_names), set(expected_tools))


if __name__ == '__main__':
    unittest.main()