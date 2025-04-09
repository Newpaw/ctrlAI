"""
CtrlAI - Configuration Manager Module

This module handles the application configuration, including loading and saving settings.
"""

from __future__ import annotations
import os
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class Config:
    """Data class representing the application configuration."""
    api_key: str = ""
    api_endpoint: str = "https://litellm.ai-sandbox.azure.to2cz.cz/v1/chat/completions"
    model: str = "gpt-4o"
    launch_hotkey: str = "ctrl+shift+t"
    first_run: bool = True
    logging_level: str = "INFO"
    system_prompt: str = "Jsi AI agent, který napomáhá s tvorbou emailů."


@dataclass
class ConfigManager:
    """Class to manage application configuration."""
    config_file: str = "config.json"
    config: Config = field(default_factory=Config)
    logger: logging.Logger = field(init=False)
    
    def __post_init__(self) -> None:
        """Initialize after instance creation."""
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> None:
        """
        Load configuration from file.
        If the file doesn't exist, create it with default values.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # Update config with loaded values
                    if isinstance(loaded_config, dict):
                        for key, value in loaded_config.items():
                            if hasattr(self.config, key):
                                setattr(self.config, key, value)
                    else:
                        self.logger.error("Invalid configuration format")
            else:
                # Create default config file
                self.save_config()
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
    
    def save_config(self) -> None:
        """Save the current configuration to file."""
        try:
            # Convert Config object to dictionary
            config_dict = {
                key: getattr(self.config, key) 
                for key in self.config.__annotations__
            }
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get_api_key(self) -> str:
        """Get the API key."""
        return self.config.api_key
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key.
        
        Args:
            api_key: The API key to set
        """
        self.config.api_key = api_key
        self.save_config()
    
    def get_api_endpoint(self) -> str:
        """Get the API endpoint URL."""
        return self.config.api_endpoint
    
    def set_api_endpoint(self, api_endpoint: str) -> None:
        """
        Set the API endpoint URL.
        
        Args:
            api_endpoint: The API endpoint URL to set
        """
        self.config.api_endpoint = api_endpoint
        self.save_config()
    
    def get_model(self) -> str:
        """Get the model name."""
        return self.config.model
    
    def set_model(self, model: str) -> None:
        """
        Set the model name.
        
        Args:
            model: The model name to set
        """
        self.config.model = model
        self.save_config()
    
    def get_launch_hotkey(self) -> str:
        """Get the launch hotkey combination."""
        return self.config.launch_hotkey
    
    def set_launch_hotkey(self, hotkey: str) -> None:
        """
        Set the launch hotkey combination.
        
        Args:
            hotkey: The hotkey combination to set (e.g., "alt+t")
        """
        self.config.launch_hotkey = hotkey
        self.save_config()
    
    def is_first_run(self) -> bool:
        """Check if this is the first time the application is run."""
        return self.config.first_run
    
    def set_first_run_completed(self) -> None:
        """Mark that the first run has been completed."""
        self.config.first_run = False
        self.save_config()
    
    def get_logging_level(self) -> str:
        """Get the logging level."""
        return self.config.logging_level
    
    def set_logging_level(self, level: str) -> None:
        """
        Set the logging level.
        
        Args:
            level: The logging level to set (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        """
        self.config.logging_level = level
        self.save_config()
    
    def get_system_prompt(self) -> str:
        """Get the system prompt."""
        return self.config.system_prompt
    
    def set_system_prompt(self, prompt: str) -> None:
        """
        Set the system prompt.
        
        Args:
            prompt: The system prompt to set
        """
        self.config.system_prompt = prompt
        self.save_config()