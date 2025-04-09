"""
CtrlAI - LiteLLM Client Module

This module handles the interaction with the LiteLLM API.
"""

from __future__ import annotations
import requests
import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union


@dataclass
class LiteLLMClient:
    """Class to interact with the LiteLLM API."""
    
    api_key: str
    api_endpoint: str
    model: str = "gpt-3.5-turbo"  # Default model
    system_prompt: str = "Jsi AI agent, který napomáhá s tvorbou emailů."
    
    def send_request(self, prompt: str) -> str:
        """
        Send a request to the LiteLLM API.
        
        Args:
            prompt: The text prompt to send to the API
            
        Returns:
            The response text from the API
        """
        if not self.api_key or not self.api_endpoint:
            return "Error: API key or endpoint not configured. Please check settings."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Include system prompt in the messages
        messages = []
        
        # Add system message if system prompt is provided
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                        self.api_endpoint,
                        headers=headers,
                        data=json.dumps(data),
                        timeout=30,
                        verify=False
                    )
            
            # Use pattern matching to handle different response scenarios
            match response.status_code:
                case 200:
                    try:
                        response_json = response.json()
                        # Extract content using pattern matching
                        if choices := response_json.get("choices", []):
                            if message := choices[0].get("message", {}):
                                if content := message.get("content"):
                                    return content
                        return "No response content"
                    except json.JSONDecodeError:
                        return "Error: Failed to parse API response"
                case 401:
                    return "Error: Authentication failed. Please check your API key."
                case 429:
                    return "Error: Rate limit exceeded. Please try again later."
                case _:
                    return f"Error: API returned status code {response.status_code}\n{response.text}"
        
        except requests.exceptions.RequestException as e:
            return f"Error: Failed to connect to LiteLLM API: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def set_model(self, model: str) -> None:
        """
        Set the model to use for requests.
        
        Args:
            model: The model name (e.g., "gpt-3.5-turbo", "gpt-4")
        """
        self.model = model
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key.
        
        Args:
            api_key: New API key
        """
        self.api_key = api_key
    
    def set_api_endpoint(self, api_endpoint: str) -> None:
        """
        Set the API endpoint.
        
        Args:
            api_endpoint: New API endpoint URL
        """
        self.api_endpoint = api_endpoint