"""Tests for the auth module of mcp-github-app-auth."""
import os
import unittest
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta

from mcp_github_app.auth import get_installation_token


class TestAuth(unittest.TestCase):
    """Test the authentication functions."""
    
    def setUp(self):
        """Set up test environment variables."""
        self.original_github_app_id = os.environ.get('GITHUB_APP_ID')
        self.original_github_private_key = os.environ.get('GITHUB_PRIVATE_KEY')
        self.original_github_installation_id = os.environ.get('GITHUB_INSTALLATION_ID')
        
        os.environ['GITHUB_APP_ID'] = '123456'
        # Using a mock private key - in real tests this would be a proper key
        os.environ['GITHUB_PRIVATE_KEY'] = '''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0fN9uU4DLiE9YF1LlQ2K5J3tVgIhV8z844Zq94p7X9Z9Z9Z9
Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9
-----END RSA PRIVATE KEY-----'''
        os.environ['GITHUB_INSTALLATION_ID'] = '789012'

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

    @patch('mcp_github_app.auth.jwt.encode')
    @patch('mcp_github_app.auth.requests.post')
    def test_get_installation_token(self, mock_post, mock_jwt_encode):
        """Test getting an installation token."""
        # Mock JWT encoding to return a test token
        mock_jwt_encode.return_value = 'test_jwt_token'
        
        # Mock the response from GitHub API
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'token': 'test_token_12345',
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        mock_post.return_value = mock_response

        # Call the function
        token, expires_at = get_installation_token()

        # Assertions
        self.assertEqual(token, 'test_token_12345')
        self.assertIsNotNone(expires_at)
        
        # Verify that the API was called correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn('https://api.github.com/app/installations/789012/access_tokens', args[0])
        self.assertIn('Authorization', kwargs['headers'])
        self.assertTrue(kwargs['headers']['Authorization'].startswith('Bearer '))
        
        # Verify JWT encoding was called
        mock_jwt_encode.assert_called()

    @patch('mcp_github_app.auth.jwt.encode')
    @patch('mcp_github_app.auth.requests.post')
    def test_get_installation_token_caching(self, mock_post, mock_jwt_encode):
        """Test that tokens are cached and reused until expiration."""
        # Import and reset the cache to start fresh
        from mcp_github_app.auth import _GHS_CACHE
        _GHS_CACHE["token"] = None
        _GHS_CACHE["exp"] = 0
        
        # Mock JWT encoding to return a test token
        mock_jwt_encode.return_value = 'test_jwt_token'
        
        # Mock the response from GitHub API
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'token': 'cached_token_12345',
            'expires_at': (datetime.now() + timedelta(minutes=30)).isoformat()
        }
        mock_post.return_value = mock_response

        # Call the function twice
        token1, _ = get_installation_token()
        token2, _ = get_installation_token()

        # Both calls should return the same token (cached)
        self.assertEqual(token1, token2)
        self.assertEqual(token1, 'cached_token_12345')
        
        # Verify that the API was only called once (due to caching)
        mock_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()