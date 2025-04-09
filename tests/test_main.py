"""
Unit tests for the main module.
"""

import unittest
from unittest.mock import patch, MagicMock
import logging
import threading
from main import main


class TestMain(unittest.TestCase):
    """Test cases for the main module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Disable logging for tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Clean up after each test method."""
        # Re-enable logging
        logging.disable(logging.NOTSET)

    @patch('main.ConfigManager')
    @patch('main.LiteLLMClient')
    @patch('main.UIManager')
    @patch('main.KeyListener')
    @patch('threading.Thread')
    @patch('logging.basicConfig')
    def test_main_first_run(self, mock_logging_config, mock_thread, mock_key_listener, 
                           mock_ui_manager, mock_litellm_client, mock_config_manager):
        """Test the main function when it's the first run."""
        # Mock ConfigManager
        mock_config = MagicMock()
        mock_config.get_logging_level.return_value = "INFO"
        mock_config.get_api_key.return_value = "test_api_key"
        mock_config.get_api_endpoint.return_value = "https://test-endpoint.com"
        mock_config.get_model.return_value = "test-model"
        mock_config.get_system_prompt.return_value = "Test system prompt"
        mock_config.get_launch_hotkey.return_value = "ctrl+shift+t"
        mock_config.is_first_run.return_value = True
        mock_config_manager.return_value = mock_config
        
        # Mock LiteLLMClient
        mock_client = MagicMock()
        mock_litellm_client.return_value = mock_client
        
        # Mock UIManager
        mock_ui = MagicMock()
        mock_ui_manager.return_value = mock_ui
        
        # Mock KeyListener
        mock_listener = MagicMock()
        mock_key_listener.return_value = mock_listener
        
        # Call main
        main()
            
        # Verify logging was configured
        mock_logging_config.assert_called_once()
        
        # Verify ConfigManager was initialized and used
        mock_config_manager.assert_called_once()
        mock_config.load_config.assert_called_once()
        mock_config.get_logging_level.assert_called_once()
        mock_config.get_api_key.assert_called_once()
        mock_config.get_api_endpoint.assert_called_once()
        mock_config.get_model.assert_called_once()
        mock_config.get_system_prompt.assert_called_once()
        mock_config.get_launch_hotkey.assert_called_once()
        mock_config.is_first_run.assert_called_once()
        mock_config.set_first_run_completed.assert_called_once()
        
        # Verify LiteLLMClient was initialized and configured
        mock_litellm_client.assert_called_once_with("test_api_key", "https://test-endpoint.com")
        mock_client.set_model.assert_called_once_with("test-model")
        self.assertEqual(mock_client.system_prompt, "Test system prompt")
        
        # Verify UIManager was initialized and used
        mock_ui_manager.assert_called_once_with(mock_client)
        mock_ui.create_window.assert_called_once()
        mock_ui.show_window.assert_called_once()
        mock_ui.start.assert_called_once()
        
        # Verify KeyListener was initialized and started
        mock_key_listener.assert_called_once_with(mock_ui.show_window, "ctrl+shift+t")
        mock_thread.assert_called_once_with(target=mock_listener.start_listening, daemon=True)
        mock_thread.return_value.start.assert_called_once()

    @patch('main.ConfigManager')
    @patch('main.LiteLLMClient')
    @patch('main.UIManager')
    @patch('main.KeyListener')
    @patch('threading.Thread')
    @patch('logging.basicConfig')
    def test_main_not_first_run(self, mock_logging_config, mock_thread, mock_key_listener, 
                               mock_ui_manager, mock_litellm_client, mock_config_manager):
        """Test the main function when it's not the first run."""
        # Mock ConfigManager
        mock_config = MagicMock()
        mock_config.get_logging_level.return_value = "INFO"
        mock_config.get_api_key.return_value = "test_api_key"
        mock_config.get_api_endpoint.return_value = "https://test-endpoint.com"
        mock_config.get_model.return_value = "test-model"
        mock_config.get_system_prompt.return_value = "Test system prompt"
        mock_config.get_launch_hotkey.return_value = "ctrl+shift+t"
        mock_config.is_first_run.return_value = False
        mock_config_manager.return_value = mock_config
        
        # Mock LiteLLMClient
        mock_client = MagicMock()
        mock_litellm_client.return_value = mock_client
        
        # Mock UIManager
        mock_ui = MagicMock()
        mock_ui_manager.return_value = mock_ui
        
        # Mock KeyListener
        mock_listener = MagicMock()
        mock_key_listener.return_value = mock_listener
        
        # Call main
        main()
        
        # Verify logging was configured
        mock_logging_config.assert_called_once()
        
        # Verify ConfigManager was initialized and used
        mock_config_manager.assert_called_once()
        mock_config.load_config.assert_called_once()
        
        # Verify UIManager was initialized and used
        mock_ui_manager.assert_called_once_with(mock_client)
        mock_ui.create_window.assert_called_once()
        mock_ui.hide_window.assert_called_once()  # Window should be hidden initially
        mock_ui.show_window.assert_not_called()  # Window should not be shown
        mock_ui.start.assert_called_once()
        
        # Verify KeyListener was initialized and started
        mock_key_listener.assert_called_once_with(mock_ui.show_window, "ctrl+shift+t")
        mock_thread.assert_called_once_with(target=mock_listener.start_listening, daemon=True)
        mock_thread.return_value.start.assert_called_once()

    @patch('logging.basicConfig')
    def test_main_logging_levels(self, mock_logging_config):
        """Test the main function with different logging levels."""
        # Test cases for different logging levels
        test_cases = [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
            ("INVALID", logging.INFO)  # Default to INFO for invalid levels
        ]
        
        for level_str, expected_level in test_cases:
            with self.subTest(level=level_str):
                # Reset mocks
                mock_logging_config.reset_mock()
                
                # Mock ConfigManager
                mock_config = MagicMock()
                mock_config.get_logging_level.return_value = level_str
                
                # Patch all dependencies
                with patch('main.ConfigManager', return_value=mock_config), \
                     patch('main.LiteLLMClient'), \
                     patch('main.UIManager'), \
                     patch('main.KeyListener'), \
                     patch('threading.Thread'):
                    
                    # Call main
                    main()
                    
                    # Verify logging was configured with the correct level
                    mock_logging_config.assert_called_once()
                    args, kwargs = mock_logging_config.call_args
                    self.assertEqual(kwargs['level'], expected_level)


if __name__ == '__main__':
    unittest.main()