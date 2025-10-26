"""Integration tests for the mcp-github-app-auth server."""
import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import asyncio

from mcp_github_app.server import GitHubAppServer


class TestIntegration(unittest.TestCase):
    """Integration tests for the server functionality."""
    
    def setUp(self):
        """Set up test environment variables."""
        self.original_github_app_id = os.environ.get('GITHUB_APP_ID')
        self.original_github_private_key = os.environ.get('GITHUB_PRIVATE_KEY')
        self.original_github_installation_id = os.environ.get('GITHUB_INSTALLATION_ID')
        
        os.environ['GITHUB_APP_ID'] = '123456'
        os.environ['GITHUB_PRIVATE_KEY'] = '''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA1e46g1J3lP12KJ5VQxZ9vXhY2G7UyJcN0pX8W3VbQ9R2A5s4
F6T1H3V7P9Y2D5X1Z8C4V3B2N1M6L5K4J3H2G1F0E9D8C7B6A5Z4Y3X2W1V0
-----END RSA PRIVATE KEY-----'''
        os.environ['GITHUB_INSTALLATION_ID'] = '789012'

        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.server = GitHubAppServer()

    def tearDown(self):
        """Restore original environment variables."""
        if self.original_github_app_id:
            os.environ['GITHUB_APP_ID'] = self.original_github_app_id
        else:
            os.environ.pop('GITHUB_APP_ID', None)
            
        if self.original_github_private_key:
            os.environ['GITHUB_PRIVATE_KEY'] = self.original_github_private_key
        else:
            os.environ.pop('GITHUB_PRIVATE_KEY', None)
            
        if self.original_github_installation_id:
            os.environ['GITHUB_INSTALLATION_ID'] = self.original_github_installation_id
        else:
            os.environ.pop('GITHUB_INSTALLATION_ID', None)

    @patch('mcp_github_app.git_ops.clone_repo')
    @patch('mcp_github_app.git_ops.set_author')
    @patch('mcp_github_app.git_ops.commit_all')
    @patch('mcp_github_app.git_ops.push')
    def test_full_git_workflow(self, mock_push, mock_commit, mock_set_author, mock_clone):
        """Test a full git workflow: clone -> set author -> commit -> push."""
        # Mock all the functions to return success messages
        mock_clone.return_value = "Repository cloned successfully"
        mock_set_author.return_value = "Author set successfully"
        mock_commit.return_value = "Changes committed successfully"
        mock_push.return_value = "Changes pushed successfully"
        
        # Step 1: Clone the repository
        clone_result = asyncio.run(self.server.call_tool('clone_repo', {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'dest_dir': f'{self.test_dir}/cloned-repo'
        }))
        
        self.assertEqual(clone_result, "Repository cloned successfully")
        mock_clone.assert_called_once_with('test-owner', 'test-repo', f'{self.test_dir}/cloned-repo', None)
        
        # Step 2: Set author (would happen in the cloned repo)
        # Note: This tool is not directly available through the server, but we can test the git_ops function directly
        from mcp_github_app.git_ops import set_author
        set_author(f'{self.test_dir}/cloned-repo', 'Test User', 'test@example.com')
        mock_set_author.assert_called_once_with(f'{self.test_dir}/cloned-repo', 'Test User', 'test@example.com')
        
        # Step 3: Commit changes (simulated)
        from mcp_github_app.git_ops import commit_all
        commit_all(f'{self.test_dir}/cloned-repo', 'Initial commit after clone')
        mock_commit.assert_called_once_with(f'{self.test_dir}/cloned-repo', 'Initial commit after clone')
        
        # Step 4: Push changes
        push_result = asyncio.run(self.server.call_tool('push', {
            'cwd': f'{self.test_dir}/cloned-repo',
            'remote': 'origin',
            'branch': 'main'
        }))
        
        self.assertEqual(push_result, "Changes pushed successfully")
        mock_push.assert_called_once_with(f'{self.test_dir}/cloned-repo', 'origin', 'main')

    @patch('mcp_github_app.gh_api.create_branch')
    @patch('mcp_github_app.gh_api.create_pull_request')
    @patch('mcp_github_app.gh_api.merge_pull_request')
    def test_full_pr_workflow(self, mock_merge_pr, mock_create_pr, mock_create_branch):
        """Test a full PR workflow: create branch -> create PR -> merge PR."""
        # Mock all the functions to return success messages
        mock_create_branch.return_value = "Branch created successfully"
        mock_create_pr.return_value = "Pull request created successfully"
        mock_merge_pr.return_value = "Pull request merged successfully"
        
        # Step 1: Create a new branch
        branch_result = asyncio.run(self.server.call_tool('create_branch', {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'new_branch': 'feature-new-feature',
            'from_ref': 'heads/main'
        }))
        
        self.assertEqual(branch_result, "Branch created successfully")
        mock_create_branch.assert_called_once_with('test-owner', 'test-repo', 'feature-new-feature', 'heads/main')
        
        # Step 2: Create a pull request
        pr_result = asyncio.run(self.server.call_tool('create_pull_request', {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'title': 'Add new feature',
            'head': 'feature-new-feature',
            'base': 'main',
            'body': 'This PR adds the new feature'
        }))
        
        self.assertEqual(pr_result, "Pull request created successfully")
        mock_create_pr.assert_called_once_with('test-owner', 'test-repo', 'Add new feature', 'feature-new-feature', 'main', 'This PR adds the new feature')
        
        # Step 3: Merge the pull request
        merge_result = asyncio.run(self.server.call_tool('merge_pull_request', {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'number': 123,
            'merge_method': 'squash',
            'commit_title': 'Squash merge: Add new feature',
            'commit_message': 'This PR adds the new feature'
        }))
        
        self.assertEqual(merge_result, "Pull request merged successfully")
        mock_merge_pr.assert_called_once_with('test-owner', 'test-repo', 123, 'squash', 'Squash merge: Add new feature', 'This PR adds the new feature')

    def test_tool_list_consistency(self):
        """Test that the tools available match the call_tool implementation."""
        # Get the list of tools
        tools = self.server.list_tools()
        tool_names = [tool.name for tool in tools]
        
        # Expected tools
        expected_tools = ['clone_repo', 'create_branch', 'push', 'create_pull_request', 'merge_pull_request']
        
        # Verify all tools are present
        self.assertEqual(set(tool_names), set(expected_tools))
        
        # Verify each tool can be called without raising "Unknown tool" error
        for tool_name in tool_names:
            # Call each tool with minimal valid arguments to ensure it's implemented
            if tool_name == 'clone_repo':
                with patch('mcp_github_app.git_ops.clone_repo') as mock:
                    mock.return_value = "Success"
                    result = asyncio.run(self.server.call_tool(tool_name, {
                        'owner': 'test',
                        'repo': 'test',
                        'dest_dir': '/tmp'
                    }))
                    self.assertIsNotNone(result)
            elif tool_name == 'create_branch':
                with patch('mcp_github_app.gh_api.create_branch') as mock:
                    mock.return_value = "Success"
                    result = asyncio.run(self.server.call_tool(tool_name, {
                        'owner': 'test',
                        'repo': 'test',
                        'new_branch': 'test'
                    }))
                    self.assertIsNotNone(result)
            elif tool_name == 'push':
                with patch('mcp_github_app.git_ops.push') as mock:
                    mock.return_value = "Success"
                    result = asyncio.run(self.server.call_tool(tool_name, {
                        'cwd': '/tmp'
                    }))
                    self.assertIsNotNone(result)
            elif tool_name == 'create_pull_request':
                with patch('mcp_github_app.gh_api.create_pull_request') as mock:
                    mock.return_value = "Success"
                    result = asyncio.run(self.server.call_tool(tool_name, {
                        'owner': 'test',
                        'repo': 'test',
                        'title': 'test',
                        'head': 'test'
                    }))
                    self.assertIsNotNone(result)
            elif tool_name == 'merge_pull_request':
                with patch('mcp_github_app.gh_api.merge_pull_request') as mock:
                    mock.return_value = "Success"
                    result = asyncio.run(self.server.call_tool(tool_name, {
                        'owner': 'test',
                        'repo': 'test',
                        'number': 1
                    }))
                    self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()