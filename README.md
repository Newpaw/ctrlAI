# CtrlAI

A Windows application designed to launch upon pressing specific key combinations (e.g., ctrl+shift+t). The application captures text inputs through commands like Ctrl+c, allowing users to edit the text before sending it to LiteLLM for processing. Once a response is received, the application displays the output, providing users with further editing capabilities and the option to copy the final text.

## Features

- Launch with a keyboard shortcut (default: ctrl+shift+t)
- Capture text from clipboard
- Edit text before sending to LiteLLM
- View and edit LiteLLM responses
- Copy responses to clipboard

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ctrlAI.git
   cd ctrlAI
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python main.py
   ```

## Configuration

On first run, the application will create a `config.json` file with default settings. You'll need to add your LiteLLM API key to this file or through the application settings.

### Default Configuration

```json
{
    "api_key": "",
    "api_endpoint": "https://api.litellm.ai/v1/chat/completions",
    "model": "gpt-3.5-turbo",
    "launch_hotkey": "ctrl+shift+t",
    "first_run": true
}
```

## Usage

1. Press Alt+t to launch the application
2. Copy text with Ctrl+c before launching, or use the "Paste from Clipboard" button
3. Edit the text as needed
4. Click "Send to LiteLLM" to process the text
5. View and edit the response
6. Click "Copy Response" to copy the response to clipboard

## Project Structure

- `main.py`: Main application entry point
- `key_listener.py`: Handles keyboard shortcuts and hotkeys
- `ui_manager.py`: Manages the graphical user interface
- `litellm_client.py`: Handles communication with the LiteLLM API
- `config_manager.py`: Manages application configuration
- `requirements.txt`: Lists required Python packages
- `config.json`: Stores application settings (created on first run)

## Requirements

- Python 3.7+
- Windows operating system
- Internet connection for LiteLLM API access
- LiteLLM API key

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.