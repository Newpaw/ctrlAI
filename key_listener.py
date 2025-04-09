"""
CtrlAI - Key Listener Module

This module handles keyboard event listening for launching the application.
"""

from __future__ import annotations
import keyboard
import threading
import time
import logging
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class KeyListener:
    """Class to handle keyboard event listening."""
    callback_function: Callable[[], None]
    launch_hotkey: str = "ctrl+shift+t"
    is_listening: bool = field(default=False, init=False)
    logger: logging.Logger = field(init=False)

    def __post_init__(self) -> None:
        """Initialize after instance creation."""
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"KeyListener initialized with hotkey: {self.launch_hotkey}")

    def start_listening(self) -> None:
        """Start listening for the key combination."""
        self.is_listening = True
        self.logger.info(f"Registering hotkey: {self.launch_hotkey}")

        try:
            # Register hotkey with direct callback
            keyboard.add_hotkey(self.launch_hotkey, self.on_hotkey_pressed)
            self.logger.info("Hotkey registered successfully.")
            
            # Keep thread alive while listening
            while self.is_listening:
                time.sleep(0.1)  # Sleep to reduce CPU usage
                
        except Exception as e:
            self.logger.error(f"Failed to register hotkey: {e}")

    def stop_listening(self) -> None:
        """Stop listening for the key combination."""
        self.is_listening = False
        try:
            keyboard.remove_hotkey(self.launch_hotkey)
            self.logger.info("Stopped listening and removed hotkey.")
        except Exception as e:
            self.logger.error(f"Error removing hotkey: {e}")

    def on_hotkey_pressed(self) -> None:
        """Handle the hotkey press event."""
        self.logger.info("Hotkey pressed!")
        # Call callback in a separate thread to avoid blocking keyboard
        threading.Thread(target=self.callback_function, daemon=True).start()