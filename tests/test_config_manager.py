"""
Unit tests for the ConfigManager module.
"""

import unittest
from unittest.mock import patch, mock_open
import logging
from config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for the ConfigManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config_manager = ConfigManager()
        
        # Sample config data for testing
        self.sample_config = {
            "api_key": "test_api_key",
            "api_endpoint": "https://test-endpoint.com",
            "model": "test-model",
            "launch_hotkey": "alt+x",
            "first_run": False,
            "logging_level": "DEBUG",
            "system_prompt": "Test system prompt"
        }
        
        # Disable logging for tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Clean up after each test method."""
        # Re-enable logging
        logging.disable(logging.NOTSET)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_config_existing_file(self, mock_json_load, mock_file_open, mock_exists):
        """Test loading configuration from an existing file."""
        # Setup mocks
        mock_exists.return_value = True
        mock_json_load.return_value = self.sample_config
        
        # Call the method
        self.config_manager.load_config()
        
        # Verify file was opened for reading
        mock_file_open.assert_called_once_with(self.config_manager.config_file, "r", encoding="utf-8")
        
        # Verify json.load was called
        mock_json_load.assert_called_once_with(mock_file_open())
        
        # Verify config values were updated
        self.assertEqual(self.config_manager.config.api_key, "test_api_key")
        self.assertEqual(self.config_manager.config.api_endpoint, "https://test-endpoint.com")
        self.assertEqual(self.config_manager.config.model, "test-model")
        self.assertEqual(self.config_manager.config.launch_hotkey, "alt+x")
        self.assertFalse(self.config_manager.config.first_run)
        self.assertEqual(self.config_manager.config.logging_level, "DEBUG")
        self.assertEqual(self.config_manager.config.system_prompt, "Test system prompt")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_load_config_new_file(self, mock_json_dump, mock_file_open, mock_exists):
        """Test loading configuration when the file doesn't exist."""
        # Setup mocks
        mock_exists.return_value = False
        
        # Call the method
        self.config_manager.load_config()
        
        # Verify save_config was called (which creates a new file)
        mock_file_open.assert_called_once_with(self.config_manager.config_file, "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_config(self, mock_json_dump, mock_file_open):
        """Test saving configuration to file."""
        # Setup test data
        self.config_manager.config.api_key = "new_api_key"
        self.config_manager.config.model = "new-model"
        
        # Call the method
        self.config_manager.save_config()
        
        # Verify file was opened for writing
        mock_file_open.assert_called_once_with(self.config_manager.config_file, "w", encoding="utf-8")
        
        # Verify json.dump was called with the correct data
        expected_config = {
            "api_key": "new_api_key",
            "api_endpoint": "https://litellm.ai-sandbox.azure.to2cz.cz/v1/chat/completions",
            "model": "new-model",
            "launch_hotkey": "ctrl+shift+t",
            "first_run": True,
            "logging_level": "INFO",
            "system_prompt": "Jsi AI agent, který napomáhá s tvorbou emailů."
        }
        
        # Get the actual config that was passed to json.dump
        actual_config = mock_json_dump.call_args[0][0]
        
        # Verify each key-value pair
        for key, value in expected_config.items():
            self.assertEqual(actual_config[key], value)

    def test_get_api_key(self):
        """Test getting the API key."""
        self.config_manager.config.api_key = "test_key"
        self.assertEqual(self.config_manager.get_api_key(), "test_key")

    @patch('config_manager.ConfigManager.save_config')
    def test_set_api_key(self, mock_save_config):
        """Test setting the API key."""
        self.config_manager.set_api_key("new_key")
        self.assertEqual(self.config_manager.config.api_key, "new_key")
        mock_save_config.assert_called_once()

    def test_get_api_endpoint(self):
        """Test getting the API endpoint."""
        self.config_manager.config.api_endpoint = "https://test-endpoint.com"
        self.assertEqual(self.config_manager.get_api_endpoint(), "https://test-endpoint.com")

    @patch('config_manager.ConfigManager.save_config')
    def test_set_api_endpoint(self, mock_save_config):
        """Test setting the API endpoint."""
        self.config_manager.set_api_endpoint("https://new-endpoint.com")
        self.assertEqual(self.config_manager.config.api_endpoint, "https://new-endpoint.com")
        mock_save_config.assert_called_once()

    def test_get_model(self):
        """Test getting the model."""
        self.config_manager.config.model = "test-model"
        self.assertEqual(self.config_manager.get_model(), "test-model")

    @patch('config_manager.ConfigManager.save_config')
    def test_set_model(self, mock_save_config):
        """Test setting the model."""
        self.config_manager.set_model("new-model")
        self.assertEqual(self.config_manager.config.model, "new-model")
        mock_save_config.assert_called_once()

    def test_get_launch_hotkey(self):
        """Test getting the launch hotkey."""
        self.config_manager.config.launch_hotkey = "alt+x"
        self.assertEqual(self.config_manager.get_launch_hotkey(), "alt+x")

    @patch('config_manager.ConfigManager.save_config')
    def test_set_launch_hotkey(self, mock_save_config):
        """Test setting the launch hotkey."""
        self.config_manager.set_launch_hotkey("alt+y")
        self.assertEqual(self.config_manager.config.launch_hotkey, "alt+y")
        mock_save_config.assert_called_once()

    def test_is_first_run(self):
        """Test checking if it's the first run."""
        self.config_manager.config.first_run = True
        self.assertTrue(self.config_manager.is_first_run())
        
        self.config_manager.config.first_run = False
        self.assertFalse(self.config_manager.is_first_run())

    @patch('config_manager.ConfigManager.save_config')
    def test_set_first_run_completed(self, mock_save_config):
        """Test marking first run as completed."""
        self.config_manager.config.first_run = True
        self.config_manager.set_first_run_completed()
        self.assertFalse(self.config_manager.config.first_run)
        mock_save_config.assert_called_once()

    def test_get_logging_level(self):
        """Test getting the logging level."""
        self.config_manager.config.logging_level = "DEBUG"
        self.assertEqual(self.config_manager.get_logging_level(), "DEBUG")

    @patch('config_manager.ConfigManager.save_config')
    def test_set_logging_level(self, mock_save_config):
        """Test setting the logging level."""
        self.config_manager.set_logging_level("ERROR")
        self.assertEqual(self.config_manager.config.logging_level, "ERROR")
        mock_save_config.assert_called_once()

    def test_get_system_prompt(self):
        """Test getting the system prompt."""
        self.config_manager.config.system_prompt = "Test prompt"
        self.assertEqual(self.config_manager.get_system_prompt(), "Test prompt")

    @patch('config_manager.ConfigManager.save_config')
    def test_set_system_prompt(self, mock_save_config):
        """Test setting the system prompt."""
        self.config_manager.set_system_prompt("New prompt")
        self.assertEqual(self.config_manager.config.system_prompt, "New prompt")
        mock_save_config.assert_called_once()


if __name__ == '__main__':
    unittest.main()