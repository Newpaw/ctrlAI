"""
CtrlAI - Main Module

This module serves as the entry point for the CtrlAI application.
"""

from __future__ import annotations
import threading
import logging
from key_listener import KeyListener
from ui_manager import UIManager
from litellm_client import LiteLLMClient
from config_manager import ConfigManager


def main() -> None:
    """Main function to initialize and run the application."""
    # Initialize logger
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = ConfigManager()
    config.load_config()
    
    # Configure logging
    logging_level = config.get_logging_level()
    
    # Use match statement to set the appropriate logging level
    match logging_level.upper():
        case "DEBUG":
            level = logging.DEBUG
        case "INFO":
            level = logging.INFO
        case "WARNING":
            level = logging.WARNING
        case "ERROR":
            level = logging.ERROR
        case "CRITICAL":
            level = logging.CRITICAL
        case _:
            level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger.info("Starting CtrlAI application...")
    
    # Initialize LiteLLM client
    litellm_client = LiteLLMClient(config.get_api_key(), config.get_api_endpoint())
    litellm_client.set_model(config.get_model())
    litellm_client.system_prompt = config.get_system_prompt()
    
    # Initialize UI manager
    ui_manager = UIManager(litellm_client)
    
    # Create the window first
    ui_manager.create_window()
    
    # Initialize key listener in a separate thread
    hotkey = config.get_launch_hotkey()
    logger.info(f"Setting up hotkey listener for: {hotkey}")
    key_listener = KeyListener(ui_manager.show_window, hotkey)
    key_listener_thread = threading.Thread(target=key_listener.start_listening, daemon=True)
    key_listener_thread.start()
    
    # If this is the first run, show the window immediately
    if config.is_first_run():
        logger.info("First run detected - showing window immediately")
        ui_manager.show_window()
        config.set_first_run_completed()
    else:
        logger.info(f"Press {hotkey} to show the CtrlAI window")
        # Hide the window until hotkey is pressed
        ui_manager.hide_window()
    
    # Start the UI main loop - this will block until the application exits
    logger.info("Starting UI main loop")
    ui_manager.start()
    
    logger.info("Application terminated")


if __name__ == "__main__":
    main()