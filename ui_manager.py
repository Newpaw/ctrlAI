"""
CtrlAI - UI Manager Module

This module handles the graphical user interface of the application.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import pyperclip
import logging
import os
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from litellm_client import LiteLLMClient
from config_manager import ConfigManager


@dataclass
class UIManager:
    """Class to manage the application's user interface."""
    
    litellm_client: LiteLLMClient
    root: Optional[tk.Tk] = field(default=None, init=False)
    input_text: Optional[tk.Text] = field(default=None, init=False)
    system_prompt_text: Optional[tk.Text] = field(default=None, init=False)
    output_text: Optional[tk.Text] = field(default=None, init=False)
    logger: logging.Logger = field(init=False)
    
    def __post_init__(self) -> None:
        """Initialize after instance creation."""
        self.logger = logging.getLogger(__name__)
    
    def show_window(self) -> None:
        """Show the application window."""
        self.logger.info("Opening GUI Window...")
        
        # If window is already open, just bring it to front
        if self.root and self.root.winfo_exists():
            self.root.deiconify()  # Unhide the window
            self.root.lift()  # Bring to front
            self.root.focus_force()  # Force focus
            return
        
        # Create a new window if needed
        if not self.root or not self.root.winfo_exists():
            self.create_window()
        
        # Make sure the window is visible
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def create_window(self) -> None:
        """Create the application window and its components."""
        self.logger.info("Creating new window...")
        self.root = tk.Tk()
        self.root.title("CtrlAI")
        self.root.geometry("800x600")
        
        # Configure the grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # System prompt row (small)
        self.root.rowconfigure(1, weight=0)  # System prompt buttons
        self.root.rowconfigure(2, weight=1)  # Input text (larger)
        self.root.rowconfigure(3, weight=0)  # Input buttons
        self.root.rowconfigure(4, weight=1)  # Output text (larger)
        self.root.rowconfigure(5, weight=0)  # Output buttons
        
        # Create frames
        system_prompt_frame = ttk.LabelFrame(self.root, text="System Prompt")
        system_prompt_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        system_button_frame = ttk.Frame(self.root)
        system_button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        input_frame = ttk.LabelFrame(self.root, text="Input Text")
        input_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        button_frame1 = ttk.Frame(self.root)
        button_frame1.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        output_frame = ttk.LabelFrame(self.root, text="LiteLLM Response")
        output_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        
        button_frame2 = ttk.Frame(self.root)
        button_frame2.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        
        # Configure frame grid
        system_prompt_frame.columnconfigure(0, weight=1)
        system_prompt_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Create text widgets
        # System prompt text widget
        self.system_prompt_text = tk.Text(system_prompt_frame, wrap=tk.WORD, height=3)
        self.system_prompt_text.grid(row=0, column=0, sticky="nsew")
        self.system_prompt_text.insert(tk.END, self.litellm_client.system_prompt)
        
        system_prompt_scrollbar = ttk.Scrollbar(system_prompt_frame, orient="vertical", command=self.system_prompt_text.yview)
        system_prompt_scrollbar.grid(row=0, column=1, sticky="ns")
        self.system_prompt_text.config(yscrollcommand=system_prompt_scrollbar.set)
        
        # Input text widget
        self.input_text = tk.Text(input_frame, wrap=tk.WORD)
        self.input_text.grid(row=0, column=0, sticky="nsew")
        
        input_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.input_text.yview)
        input_scrollbar.grid(row=0, column=1, sticky="ns")
        self.input_text.config(yscrollcommand=input_scrollbar.set)
        
        # Output text widget
        self.output_text = tk.Text(output_frame, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        
        output_scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        output_scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.config(yscrollcommand=output_scrollbar.set)
        
        # Create buttons
        # System prompt buttons
        save_system_prompt_button = ttk.Button(system_button_frame, text="Save System Prompt", command=self.save_system_prompt)
        save_system_prompt_button.pack(side=tk.LEFT, padx=5)
        
        reset_system_prompt_button = ttk.Button(system_button_frame, text="Reset to Default", command=self.reset_system_prompt)
        reset_system_prompt_button.pack(side=tk.RIGHT, padx=5)
        paste_button = ttk.Button(button_frame1, text="Paste from Clipboard", command=self.paste_from_clipboard)
        paste_button.pack(side=tk.LEFT, padx=5)
        
        clear_input_button = ttk.Button(button_frame1, text="Clear Input", command=self.clear_input)
        clear_input_button.pack(side=tk.LEFT, padx=5)
        
        send_button = ttk.Button(button_frame1, text="Send to LiteLLM", command=self.send_to_litellm)
        send_button.pack(side=tk.RIGHT, padx=5)
        
        copy_button = ttk.Button(button_frame2, text="Copy Response", command=self.copy_response)
        copy_button.pack(side=tk.LEFT, padx=5)
        
        clear_output_button = ttk.Button(button_frame2, text="Clear Response", command=self.clear_output)
        clear_output_button.pack(side=tk.LEFT, padx=5)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-v>", lambda e: self.paste_from_clipboard())
        self.root.bind("<Control-Return>", lambda e: self.send_to_litellm())
        
        # Special handling for Copy to avoid conflicts with system clipboard
        self.output_text.bind("<Control-c>", lambda e: self.copy_response())
        
        # Handle window close - hide instead of destroy
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # Try to get clipboard content on startup
        self.paste_from_clipboard()
    
    def start(self) -> None:
        """Start the UI main loop."""
        if self.root:
            self.logger.info("Entering tkinter mainloop")
            self.root.mainloop()
            self.logger.info("Exited tkinter mainloop")
    
    def hide_window(self) -> None:
        """Hide the window instead of closing it."""
        self.logger.info("Hiding window")
        if self.root:
            self.root.withdraw()
    
    def paste_from_clipboard(self) -> None:
        """Paste text from clipboard to input area."""
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text and self.input_text:
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(tk.END, clipboard_text)
        except Exception as e:
            self.logger.error(f"Error pasting from clipboard: {e}")
    
    def clear_input(self) -> None:
        """Clear the input text area."""
        if self.input_text:
            self.input_text.delete(1.0, tk.END)
    
    def clear_output(self) -> None:
        """Clear the output text area."""
        if self.output_text:
            self.output_text.delete(1.0, tk.END)
    
    def send_to_litellm(self) -> None:
        """Send the input text to LiteLLM and display the response."""
        if not all([self.input_text, self.output_text]):
            return
            
        input_content = self.input_text.get(1.0, tk.END).strip()
        if not input_content:
            return
            
        # Show loading indicator
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Processing request...")
        self.root.update_idletasks()
        
        # Send to LiteLLM
        try:
            response = self.litellm_client.send_request(input_content)
            
            # Use pattern matching to handle different response types
            match response:
                case str() if response.startswith("Error:"):
                    self.logger.error(f"LiteLLM API error: {response}")
                case _:
                    self.logger.info("Successfully received response from LiteLLM")
            
            # Display response
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, response)
        except Exception as e:
            self.logger.error(f"Exception during LiteLLM request: {e}")
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error: {str(e)}")
    
    def copy_response(self) -> None:
        """Copy the response text to clipboard."""
        if not self.output_text:
            return
            
        output_content = self.output_text.get(1.0, tk.END).strip()
        if output_content:
            pyperclip.copy(output_content)
            # Show feedback that content was copied
            current_title = self.root.title()
            self.root.title("Copied to clipboard!")
            self.root.after(1000, lambda: self.root.title(current_title))
    
    def save_system_prompt(self) -> None:
        """Save the system prompt from the text widget to the LiteLLM client and config."""
        if not self.system_prompt_text:
            return
            
        new_prompt = self.system_prompt_text.get(1.0, tk.END).strip()
        if new_prompt:
            # Update the client
            self.litellm_client.system_prompt = new_prompt
            
            # Update the configuration file
            try:
                config_manager = ConfigManager()
                config_manager.load_config()
                config_manager.set_system_prompt(new_prompt)
                self.logger.info("System prompt updated and saved to configuration")
            except Exception as e:
                self.logger.error(f"Error saving system prompt to configuration: {e}")
            
            # Show feedback
            current_title = self.root.title()
            self.root.title("System prompt saved!")
            self.root.after(1000, lambda: self.root.title(current_title))
    
    def reset_system_prompt(self) -> None:
        """Reset the system prompt to the default value."""
        if not self.system_prompt_text:
            return
            
        # Default system prompt
        default_prompt = "Jsi AI agent, který napomáhá s tvorbou emailů."
        
        # Update the text widget
        self.system_prompt_text.delete(1.0, tk.END)
        self.system_prompt_text.insert(tk.END, default_prompt)
        
        # Update the client
        self.litellm_client.system_prompt = default_prompt
        
        # Update the configuration file
        try:
            config_manager = ConfigManager()
            config_manager.load_config()
            config_manager.set_system_prompt(default_prompt)
            self.logger.info("System prompt reset to default and saved to configuration")
        except Exception as e:
            self.logger.error(f"Error resetting system prompt in configuration: {e}")
        
        # Show feedback
        current_title = self.root.title()
        self.root.title("System prompt reset!")
        self.root.after(1000, lambda: self.root.title(current_title))