"""
Unit tests for the LiteLLMClient module.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import requests
from litellm_client import LiteLLMClient


class TestLiteLLMClient(unittest.TestCase):
    """Test cases for the LiteLLMClient class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key"
        self.api_endpoint = "https://test-endpoint.com"
        self.model = "test-model"
        self.system_prompt = "Test system prompt"
        self.client = LiteLLMClient(self.api_key, self.api_endpoint, self.model, self.system_prompt)

    def test_initialization(self):
        """Test that the client initializes with the correct values."""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.api_endpoint, self.api_endpoint)
        self.assertEqual(self.client.model, self.model)
        self.assertEqual(self.client.system_prompt, self.system_prompt)

    def test_set_model(self):
        """Test setting the model."""
        new_model = "new-model"
        self.client.set_model(new_model)
        self.assertEqual(self.client.model, new_model)

    def test_set_api_key(self):
        """Test setting the API key."""
        new_api_key = "new_api_key"
        self.client.set_api_key(new_api_key)
        self.assertEqual(self.client.api_key, new_api_key)

    def test_set_api_endpoint(self):
        """Test setting the API endpoint."""
        new_endpoint = "https://new-endpoint.com"
        self.client.set_api_endpoint(new_endpoint)
        self.assertEqual(self.client.api_endpoint, new_endpoint)

    def test_send_request_missing_credentials(self):
        """Test sending a request with missing API key or endpoint."""
        # Test with missing API key
        client = LiteLLMClient("", self.api_endpoint)
        response = client.send_request("Test prompt")
        self.assertTrue(response.startswith("Error: API key or endpoint not configured"))
        
        # Test with missing endpoint
        client = LiteLLMClient(self.api_key, "")
        response = client.send_request("Test prompt")
        self.assertTrue(response.startswith("Error: API key or endpoint not configured"))

    @patch('requests.post')
    def test_send_request_successful(self, mock_post):
        """Test sending a request that succeeds."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response content"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Send the request
        response = self.client.send_request("Test prompt")
        
        # Verify the response
        self.assertEqual(response, "Test response content")
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        
        # Check URL
        self.assertEqual(args[0], self.api_endpoint)
        
        # Check headers
        self.assertEqual(kwargs['headers']['Authorization'], f"Bearer {self.api_key}")
        self.assertEqual(kwargs['headers']['Content-Type'], "application/json")
        
        # Check data
        data = json.loads(kwargs['data'])
        self.assertEqual(data['model'], self.model)
        self.assertEqual(len(data['messages']), 2)  # System prompt + user prompt
        self.assertEqual(data['messages'][0]['role'], "system")
        self.assertEqual(data['messages'][0]['content'], self.system_prompt)
        self.assertEqual(data['messages'][1]['role'], "user")
        self.assertEqual(data['messages'][1]['content'], "Test prompt")

    @patch('requests.post')
    def test_send_request_no_system_prompt(self, mock_post):
        """Test sending a request without a system prompt."""
        # Create client without system prompt
        client = LiteLLMClient(self.api_key, self.api_endpoint, self.model, "")
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response content"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Send the request
        response = client.send_request("Test prompt")
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        
        # Check data - should only have user message, no system message
        data = json.loads(kwargs['data'])
        self.assertEqual(len(data['messages']), 1)  # Only user prompt
        self.assertEqual(data['messages'][0]['role'], "user")
        self.assertEqual(data['messages'][0]['content'], "Test prompt")

    @patch('requests.post')
    def test_send_request_authentication_error(self, mock_post):
        """Test sending a request that fails due to authentication error."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        # Send the request
        response = self.client.send_request("Test prompt")
        
        # Verify the response
        self.assertEqual(response, "Error: Authentication failed. Please check your API key.")

    @patch('requests.post')
    def test_send_request_rate_limit_error(self, mock_post):
        """Test sending a request that fails due to rate limiting."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        mock_post.return_value = mock_response
        
        # Send the request
        response = self.client.send_request("Test prompt")
        
        # Verify the response
        self.assertEqual(response, "Error: Rate limit exceeded. Please try again later.")

    @patch('requests.post')
    def test_send_request_other_error(self, mock_post):
        """Test sending a request that fails with another error code."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        # Send the request
        response = self.client.send_request("Test prompt")
        
        # Verify the response
        self.assertTrue(response.startswith("Error: API returned status code 500"))
        self.assertIn("Internal Server Error", response)

    @patch('requests.post')
    def test_send_request_connection_error(self, mock_post):
        """Test sending a request that fails due to connection error."""
        # Mock the post method to raise an exception
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Send the request
        response = self.client.send_request("Test prompt")
        
        # Verify the response
        self.assertTrue(response.startswith("Error: Failed to connect to LiteLLM API"))
        self.assertIn("Connection error", response)

    @patch('requests.post')
    def test_send_request_json_decode_error(self, mock_post):
        """Test sending a request that returns invalid JSON."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response
        
        # Send the request
        response = self.client.send_request("Test prompt")
        
        # Verify the response
        self.assertEqual(response, "Error: Failed to parse API response")

    @patch('requests.post')
    def test_send_request_missing_content(self, mock_post):
        """Test sending a request that returns a response without content."""
        # Mock the response with missing content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {}  # No content field
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Send the request
        response = self.client.send_request("Test prompt")
        
        # Verify the response
        self.assertEqual(response, "No response content")


if __name__ == '__main__':
    unittest.main()