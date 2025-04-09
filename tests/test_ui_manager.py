"""
Unit tests for the UIManager module.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import tkinter as tk
import logging
from ui_manager import UIManager
from litellm_client import LiteLLMClient
from config_manager import ConfigManager


class TestUIManager(unittest.TestCase):
    """Test cases for the UIManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock LiteLLMClient
        self.mock_litellm_client = MagicMock(spec=LiteLLMClient)
        self.mock_litellm_client.system_prompt = "Test system prompt"
        
        # Create UIManager with mock client
        self.ui_manager = UIManager(self.mock_litellm_client)
        
        # Disable logging for tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Clean up after each test method."""
        # Re-enable logging
        logging.disable(logging.NOTSET)
        
        # Destroy the root window if it exists
        if self.ui_manager.root and self.ui_manager.root.winfo_exists():
            self.ui_manager.root.destroy()

    @patch('tkinter.Tk')
    def test_create_window(self, mock_tk):
        """Test creating the application window."""
        # Mock the Tk instance
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Mock Text widgets
        mock_text = MagicMock()
        with patch('tkinter.Text', return_value=mock_text):
            # Call create_window
            self.ui_manager.create_window()
            
            # Verify Tk was created
            mock_tk.assert_called_once()
            
            # Verify window title and geometry were set
            mock_root.title.assert_called_with("CtrlAI")
            mock_root.geometry.assert_called_with("800x600")
            
            # Verify grid configuration
            mock_root.columnconfigure.assert_called_with(0, weight=1)
            self.assertEqual(mock_root.rowconfigure.call_count, 6)
            
            # Verify Text widgets were created
            self.assertEqual(self.ui_manager.input_text, mock_text)
            self.assertEqual(self.ui_manager.output_text, mock_text)
            self.assertEqual(self.ui_manager.system_prompt_text, mock_text)
            
            # Verify system prompt was inserted
            mock_text.insert.assert_any_call(tk.END, self.mock_litellm_client.system_prompt)

    @patch('tkinter.Tk')
    def test_show_window_new(self, mock_tk):
        """Test showing a new window."""
        # Mock the Tk instance
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Set root to None to simulate no existing window
        self.ui_manager.root = None
        
        # Mock create_window to set self.root
        def mock_create_window():
            self.ui_manager.root = mock_root
            
        # Patch create_window
        with patch.object(self.ui_manager, 'create_window', side_effect=mock_create_window):
            # Call show_window
            self.ui_manager.show_window()
            
            # Verify window was shown
            mock_root.deiconify.assert_called_once()
            mock_root.lift.assert_called_once()
            mock_root.focus_force.assert_called_once()

    def test_show_window_existing(self):
        """Test showing an existing window."""
        # Create a mock root that exists
        mock_root = MagicMock()
        mock_root.winfo_exists.return_value = True
        self.ui_manager.root = mock_root
        
        # Call show_window
        self.ui_manager.show_window()
        
        # Verify window was shown
        mock_root.deiconify.assert_called_once()
        mock_root.lift.assert_called_once()
        mock_root.focus_force.assert_called_once()

    def test_hide_window(self):
        """Test hiding the window."""
        # Create a mock root
        mock_root = MagicMock()
        self.ui_manager.root = mock_root
        
        # Call hide_window
        self.ui_manager.hide_window()
        
        # Verify window was hidden
        mock_root.withdraw.assert_called_once()

    @patch('pyperclip.paste')
    def test_paste_from_clipboard(self, mock_paste):
        """Test pasting from clipboard."""
        # Mock clipboard content
        mock_paste.return_value = "Test clipboard content"
        
        # Mock input text widget
        mock_input_text = MagicMock()
        self.ui_manager.input_text = mock_input_text
        
        # Call paste_from_clipboard
        self.ui_manager.paste_from_clipboard()
        
        # Verify text was cleared and inserted
        mock_input_text.delete.assert_called_once_with(1.0, tk.END)
        mock_input_text.insert.assert_called_once_with(tk.END, "Test clipboard content")

    @patch('pyperclip.paste')
    def test_paste_from_clipboard_empty(self, mock_paste):
        """Test pasting from clipboard when it's empty."""
        # Mock empty clipboard
        mock_paste.return_value = ""
        
        # Mock input text widget
        mock_input_text = MagicMock()
        self.ui_manager.input_text = mock_input_text
        
        # Call paste_from_clipboard
        self.ui_manager.paste_from_clipboard()
        
        # Verify no text operations were performed
        mock_input_text.delete.assert_not_called()
        mock_input_text.insert.assert_not_called()

    @patch('pyperclip.paste')
    def test_paste_from_clipboard_exception(self, mock_paste):
        """Test pasting from clipboard when an exception occurs."""
        # Mock paste to raise an exception
        mock_paste.side_effect = Exception("Test exception")
        
        # Mock input text widget
        mock_input_text = MagicMock()
        self.ui_manager.input_text = mock_input_text
        
        # Call paste_from_clipboard
        self.ui_manager.paste_from_clipboard()
        
        # Verify no text operations were performed
        mock_input_text.delete.assert_not_called()
        mock_input_text.insert.assert_not_called()

    def test_clear_input(self):
        """Test clearing the input text area."""
        # Mock input text widget
        mock_input_text = MagicMock()
        self.ui_manager.input_text = mock_input_text
        
        # Call clear_input
        self.ui_manager.clear_input()
        
        # Verify text was cleared
        mock_input_text.delete.assert_called_once_with(1.0, tk.END)

    def test_clear_output(self):
        """Test clearing the output text area."""
        # Mock output text widget
        mock_output_text = MagicMock()
        self.ui_manager.output_text = mock_output_text
        
        # Call clear_output
        self.ui_manager.clear_output()
        
        # Verify text was cleared
        mock_output_text.delete.assert_called_once_with(1.0, tk.END)

    def test_send_to_litellm(self):
        """Test sending text to LiteLLM."""
        # Mock text widgets
        mock_input_text = MagicMock()
        mock_input_text.get.return_value = "Test input"
        self.ui_manager.input_text = mock_input_text
        
        mock_output_text = MagicMock()
        self.ui_manager.output_text = mock_output_text
        
        # Mock root for update_idletasks
        mock_root = MagicMock()
        self.ui_manager.root = mock_root
        
        # Mock LiteLLM client response
        self.mock_litellm_client.send_request.return_value = "Test response"
        
        # Call send_to_litellm
        self.ui_manager.send_to_litellm()
        
        # Verify input was retrieved
        mock_input_text.get.assert_called_once_with(1.0, tk.END)
        
        # Verify output was updated with loading message and then response
        self.assertEqual(mock_output_text.delete.call_count, 2)
        mock_output_text.insert.assert_any_call(tk.END, "Processing request...")
        mock_output_text.insert.assert_any_call(tk.END, "Test response")
        
        # Verify LiteLLM client was called
        self.mock_litellm_client.send_request.assert_called_once_with("Test input")

    def test_send_to_litellm_empty_input(self):
        """Test sending empty text to LiteLLM."""
        # Mock text widgets
        mock_input_text = MagicMock()
        mock_input_text.get.return_value = "  "  # Empty or whitespace
        self.ui_manager.input_text = mock_input_text
        
        mock_output_text = MagicMock()
        self.ui_manager.output_text = mock_output_text
        
        # Call send_to_litellm
        self.ui_manager.send_to_litellm()
        
        # Verify input was retrieved
        mock_input_text.get.assert_called_once_with(1.0, tk.END)
        
        # Verify no other actions were taken
        mock_output_text.delete.assert_not_called()
        mock_output_text.insert.assert_not_called()
        self.mock_litellm_client.send_request.assert_not_called()

    def test_send_to_litellm_error_response(self):
        """Test sending text to LiteLLM when an error response is returned."""
        # Mock text widgets
        mock_input_text = MagicMock()
        mock_input_text.get.return_value = "Test input"
        self.ui_manager.input_text = mock_input_text
        
        mock_output_text = MagicMock()
        self.ui_manager.output_text = mock_output_text
        
        # Mock root for update_idletasks
        mock_root = MagicMock()
        self.ui_manager.root = mock_root
        
        # Mock LiteLLM client error response
        self.mock_litellm_client.send_request.return_value = "Error: Test error"
        
        # Call send_to_litellm
        self.ui_manager.send_to_litellm()
        
        # Verify error response was displayed
        mock_output_text.insert.assert_any_call(tk.END, "Error: Test error")

    @patch('pyperclip.copy')
    def test_copy_response(self, mock_copy):
        """Test copying the response to clipboard."""
        # Mock output text widget
        mock_output_text = MagicMock()
        mock_output_text.get.return_value = "Test response"
        self.ui_manager.output_text = mock_output_text
        
        # Mock root for title updates
        mock_root = MagicMock()
        self.ui_manager.root = mock_root
        
        # Call copy_response
        self.ui_manager.copy_response()
        
        # Verify text was copied
        mock_output_text.get.assert_called_once_with(1.0, tk.END)
        mock_copy.assert_called_once_with("Test response")
        
        # Verify title was updated
        mock_root.title.assert_any_call("Copied to clipboard!")
        self.assertEqual(mock_root.after.call_count, 1)

    @patch('pyperclip.copy')
    def test_copy_response_empty(self, mock_copy):
        """Test copying empty response to clipboard."""
        # Mock output text widget
        mock_output_text = MagicMock()
        mock_output_text.get.return_value = "  "  # Empty or whitespace
        self.ui_manager.output_text = mock_output_text
        
        # Call copy_response
        self.ui_manager.copy_response()
        
        # Verify no copy was performed
        mock_copy.assert_not_called()

    @patch('config_manager.ConfigManager')
    def test_save_system_prompt(self, mock_config_manager_class):
        """Test saving the system prompt."""
        # Mock system prompt text widget
        mock_system_prompt_text = MagicMock()
        mock_system_prompt_text.get.return_value = "New system prompt"
        self.ui_manager.system_prompt_text = mock_system_prompt_text
        
        # Mock root for title updates
        mock_root = MagicMock()
        self.ui_manager.root = mock_root
        
        # Mock ConfigManager instance and methods
        mock_config_manager = MagicMock()
        mock_config_manager_class.return_value = mock_config_manager
        
        # Call save_system_prompt
        with patch('ui_manager.ConfigManager', return_value=mock_config_manager):
            self.ui_manager.save_system_prompt()
        
        # Verify system prompt was updated in client
        self.assertEqual(self.mock_litellm_client.system_prompt, "New system prompt")
        
        # Verify ConfigManager was used to save the prompt
        mock_config_manager.load_config.assert_called_once()
        mock_config_manager.set_system_prompt.assert_called_once_with("New system prompt")
        
        # Verify title was updated
        mock_root.title.assert_any_call("System prompt saved!")
        self.assertEqual(mock_root.after.call_count, 1)

    @patch('config_manager.ConfigManager')
    def test_reset_system_prompt(self, mock_config_manager_class):
        """Test resetting the system prompt to default."""
        # Mock system prompt text widget
        mock_system_prompt_text = MagicMock()
        self.ui_manager.system_prompt_text = mock_system_prompt_text
        
        # Mock root for title updates
        mock_root = MagicMock()
        self.ui_manager.root = mock_root
        
        # Mock ConfigManager instance and methods
        mock_config_manager = MagicMock()
        mock_config_manager_class.return_value = mock_config_manager
        
        # Call reset_system_prompt
        with patch('ui_manager.ConfigManager', return_value=mock_config_manager):
            self.ui_manager.reset_system_prompt()
        
        # Verify system prompt was reset in text widget
        mock_system_prompt_text.delete.assert_called_once_with(1.0, tk.END)
        mock_system_prompt_text.insert.assert_called_once_with(tk.END, "Jsi AI agent, který napomáhá s tvorbou emailů.")
        
        # Verify system prompt was reset in client
        self.assertEqual(self.mock_litellm_client.system_prompt, "Jsi AI agent, který napomáhá s tvorbou emailů.")
        
        # Verify ConfigManager was used to save the default prompt
        mock_config_manager.load_config.assert_called_once()
        mock_config_manager.set_system_prompt.assert_called_once_with("Jsi AI agent, který napomáhá s tvorbou emailů.")
        
        # Verify title was updated
        mock_root.title.assert_any_call("System prompt reset!")
        self.assertEqual(mock_root.after.call_count, 1)


if __name__ == '__main__':
    unittest.main()