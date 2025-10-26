"""Tests for the git operations module of mcp-github-app-auth."""
import os
import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
import shutil
from pathlib import Path

from mcp_github_app.git_ops import clone_repo, set_author, commit_all, push, GitError


class TestGitOps(unittest.TestCase):
    """Test the git operations functions."""
    
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

    def tearDown(self):
        """Restore original environment variables and cleanup."""
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
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('mcp_github_app.git_ops._run')
    @patch('mcp_github_app.git_ops.get_installation_token')
    def test_clone_repo(self, mock_get_token, mock_run):
        """Test cloning a repository."""
        # Mock the token retrieval
        mock_get_token.return_value = ('test_token_12345', '2023-12-31T23:59:59Z')
        
        # Call the function
        result = clone_repo('test-owner', 'test-repo', f'{self.test_dir}/test-clone')
        
        # Verify the calls
        mock_get_token.assert_called_once()
        mock_run.assert_called_once_with([
            'git', 'clone', 
            'https://x-access-token:test_token_12345@github.com/test-owner/test-repo.git', 
            f'{self.test_dir}/test-clone'
        ])

    @patch('mcp_github_app.git_ops._run')
    @patch('mcp_github_app.git_ops.get_installation_token')
    def test_clone_repo_with_branch(self, mock_get_token, mock_run):
        """Test cloning a repository with a specific branch."""
        # Mock the token retrieval
        mock_get_token.return_value = ('test_token_12345', '2023-12-31T23:59:59Z')
        
        # Call the function
        result = clone_repo('test-owner', 'test-repo', f'{self.test_dir}/test-clone', branch='develop')
        
        # Verify the calls
        mock_get_token.assert_called_once()
        mock_run.assert_called_once_with([
            'git', 'clone', 
            'https://x-access-token:test_token_12345@github.com/test-owner/test-repo.git', 
            f'{self.test_dir}/test-clone',
            '-b', 'develop'
        ])

    @patch('mcp_github_app.git_ops._run')
    def test_set_author(self, mock_run):
        """Test setting git author information."""
        # Call the function
        set_author(f'{self.test_dir}/test-repo', 'Test User', 'test@example.com')
        
        # Verify the calls
        expected_calls = [
            call(['git', 'config', 'user.name', 'Test User'], cwd=f'{self.test_dir}/test-repo'),
            call(['git', 'config', 'user.email', 'test@example.com'], cwd=f'{self.test_dir}/test-repo')
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch('mcp_github_app.git_ops._run')
    def test_commit_all(self, mock_run):
        """Test committing all changes."""
        # Call the function
        commit_all(f'{self.test_dir}/test-repo', 'Test commit message')
        
        # Verify the calls
        expected_calls = [
            call(['git', 'add', '-A'], cwd=f'{self.test_dir}/test-repo'),
            call(['git', 'commit', '-m', 'Test commit message'], cwd=f'{self.test_dir}/test-repo')
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch('mcp_github_app.git_ops._run')
    @patch('mcp_github_app.git_ops.get_installation_token')
    def test_push(self, mock_get_token, mock_run):
        """Test pushing changes to remote repository."""
        # Mock the token retrieval
        mock_get_token.return_value = ('test_token_12345', '2023-12-31T23:59:59Z')
        
        # Set up mock_run to return a default value
        mock_run.return_value = 'github.com/test-owner/test-repo.git'
        
        # Call the function
        push(f'{self.test_dir}/test-repo', 'origin', 'main')
        
        # We expect two calls: one to set the remote URL with token (using sed command), one to push
        expected_calls = [
            call(['git', 'remote', 'set-url', 'origin', 
                  'https://x-access-token:test_token_12345@github.com/$(git config --get remote.origin.url | sed \'s#.*github.com/##\')'], 
                 cwd=f'{self.test_dir}/test-repo'),
            call(['git', 'push', '-u', 'origin', 'main'], 
                 cwd=f'{self.test_dir}/test-repo')
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch('mcp_github_app.git_ops.subprocess.run')
    def test_git_error_handling(self, mock_subprocess):
        """Test error handling in git operations."""
        # Mock subprocess to return an error
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = 'stdout output'
        mock_result.stderr = 'stderr output'
        mock_subprocess.return_value = mock_result
        
        with self.assertRaises(GitError) as context:
            # Call _run directly since it's the internal function that handles errors
            from mcp_github_app.git_ops import _run
            _run(['git', 'some', 'failing', 'command'])
        
        self.assertIn('git failed:', str(context.exception))
        self.assertIn('stdout output', str(context.exception))
        self.assertIn('stderr output', str(context.exception))


if __name__ == '__main__':
    unittest.main()