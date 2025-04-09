"""
Unit tests for the KeyListener module.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import threading
import time
import keyboard
import logging
from key_listener import KeyListener


class TestKeyListener(unittest.TestCase):
    """Test cases for the KeyListener class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_callback = MagicMock()
        self.test_hotkey = "ctrl+shift+t"
        self.key_listener = KeyListener(self.mock_callback, self.test_hotkey)
        
        # Disable logging for tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Clean up after each test method."""
        # Stop the key listener if it's running
        if self.key_listener.is_listening:
            self.key_listener.stop_listening()
        
        # Re-enable logging
        logging.disable(logging.NOTSET)

    @patch('keyboard.add_hotkey')
    @patch('time.sleep')
    def test_start_listening(self, mock_sleep, mock_add_hotkey):
        """Test that start_listening registers the hotkey correctly."""
        # Make sleep raise an exception to exit the while loop immediately
        mock_sleep.side_effect = Exception("Exit loop")
        
        try:
            # Call start_listening directly
            self.key_listener.start_listening()
        except Exception:
            # Expected exception to exit the loop
            pass
        
        # Verify that is_listening was set to True
        self.assertTrue(self.key_listener.is_listening)
        
        # Verify that add_hotkey was called with the correct arguments
        mock_add_hotkey.assert_called_once_with(self.test_hotkey, self.key_listener.on_hotkey_pressed)

    @patch('keyboard.remove_hotkey')
    def test_stop_listening(self, mock_remove_hotkey):
        """Test that stop_listening removes the hotkey correctly."""
        # Set is_listening to True to simulate a running listener
        self.key_listener.is_listening = True
        
        # Call stop_listening
        self.key_listener.stop_listening()
        
        # Verify that remove_hotkey was called with the correct arguments
        mock_remove_hotkey.assert_called_once_with(self.test_hotkey)
        
        # Verify that is_listening was set to False
        self.assertFalse(self.key_listener.is_listening)

    @patch('threading.Thread')
    def test_on_hotkey_pressed(self, mock_thread):
        """Test that on_hotkey_pressed starts a new thread with the callback function."""
        # Call on_hotkey_pressed
        self.key_listener.on_hotkey_pressed()
        
        # Verify that Thread was created with the correct arguments
        mock_thread.assert_called_once_with(target=self.mock_callback, daemon=True)
        
        # Verify that the thread was started
        mock_thread.return_value.start.assert_called_once()

    @patch('keyboard.add_hotkey')
    def test_exception_handling_in_start_listening(self, mock_add_hotkey):
        """Test that exceptions in start_listening are handled correctly."""
        # Make add_hotkey raise an exception
        mock_add_hotkey.side_effect = Exception("Test exception")
        
        # Create a threading event to signal when the thread should exit
        stop_event = threading.Event()
        
        # Mock the sleep function to exit the loop after a short time
        with patch('time.sleep', side_effect=lambda x: stop_event.set() if x == 0.1 else None):
            # Start listening in a separate thread
            thread = threading.Thread(target=self.key_listener.start_listening)
            thread.daemon = True
            thread.start()
            
            # Wait for the thread to exit or timeout
            stop_event.wait(timeout=1.0)
            
            # Stop listening
            self.key_listener.stop_listening()
            thread.join(timeout=1.0)
            
            # Verify that add_hotkey was called
            mock_add_hotkey.assert_called_once_with(self.test_hotkey, self.key_listener.on_hotkey_pressed)

    @patch('keyboard.remove_hotkey')
    def test_exception_handling_in_stop_listening(self, mock_remove_hotkey):
        """Test that exceptions in stop_listening are handled correctly."""
        # Set is_listening to True to simulate a running listener
        self.key_listener.is_listening = True
        
        # Make remove_hotkey raise an exception
        mock_remove_hotkey.side_effect = Exception("Test exception")
        
        # Call stop_listening
        self.key_listener.stop_listening()
        
        # Verify that remove_hotkey was called
        mock_remove_hotkey.assert_called_once_with(self.test_hotkey)
        
        # Verify that is_listening was set to False despite the exception
        self.assertFalse(self.key_listener.is_listening)


if __name__ == '__main__':
    unittest.main()