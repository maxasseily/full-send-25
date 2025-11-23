# Makatum - AI Text Assistant

A Windows application similar to Grammarly that provides ChatGPT assistance for selected text via a global hotkey.

## Features

- 🔥 **Global Hotkey**: Press `Ctrl+Shift+Space` to activate from any application
- 📝 **Auto Text Capture**: Automatically captures selected/highlighted text
- 🤖 **ChatGPT Integration**: Powered by OpenAI's GPT models
- ⚡ **Quick Actions**: 
  - Improve Writing
  - Fix Grammar
  - Make Shorter
  - Custom Prompt
- 📋 **Easy Copy/Replace**: Copy response or replace original text with one click
- 🎯 **Always On Top**: Popup stays visible while working

## Installation

### 1. Prerequisites
- Python 3.8 or higher
- Windows OS
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### 2. Setup

```powershell
# Clone or navigate to the project directory
cd c:\Users\grimm\Documents\Projects\makatum

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env

# Edit .env and add your OpenAI API key
notepad .env
```

### 3. Configure API Key

Open `.env` file and replace `your_api_key_here` with your actual OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Usage

### Running the Application

```powershell
python main.py
```

The application will run in the background and display:
```
Makatum AI Text Assistant is running...
Press ctrl+shift+space to activate popup
Press Ctrl+C to exit
```

### How to Use

1. **Select text** in any application (browser, Word, Notepad, etc.)
2. **Press `Ctrl+Shift+Space`** to open the popup
3. The selected text will appear in the popup automatically
4. **Choose an action**:
   - **Improve Writing**: Enhance clarity and flow
   - **Fix Grammar**: Correct spelling and grammar errors
   - **Make Shorter**: Condense while keeping key points
   - **Custom Prompt**: Enter your own instruction
5. **Use the response**:
   - **Copy Response**: Copy to clipboard
   - **Replace Original**: Replace selected text with AI response

### Customizing the Hotkey

Edit `main.py` and change the hotkey in the `__init__` method:

```python
self.hotkey = "ctrl+shift+space"  # Change to your preferred combination
```

Available modifiers: `ctrl`, `shift`, `alt`, `win`

## Running on Startup (Optional)

To run Makatum automatically when Windows starts:

1. Press `Win+R` and type `shell:startup`
2. Create a shortcut to `main.py` or create a batch file:

```batch
@echo off
cd c:\Users\grimm\Documents\Projects\makatum
python main.py
```

Save as `start_makatum.bat` in the startup folder.

## Building an Executable (Optional)

To create a standalone `.exe` file:

```powershell
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name Makatum main.py
```

The executable will be in the `dist` folder.

## Troubleshooting

### "No text selected" message
- Make sure text is actually selected/highlighted before pressing the hotkey
- The app uses `Ctrl+C` to capture text, so ensure clipboard access works

### API Key errors
- Verify your `.env` file has the correct API key
- Check that you have API credits available in your OpenAI account

### Hotkey not working
- Run the script as Administrator if hotkey doesn't register
- Check if another application is using the same hotkey combination
- Try a different hotkey combination

### Window doesn't appear
- Check if the window is behind other windows
- Try closing and restarting the application

## Requirements

- `keyboard`: Global hotkey detection
- `pyperclip`: Clipboard operations
- `openai`: ChatGPT API integration
- `python-dotenv`: Environment variable management
- `tkinter`: GUI (included with Python)

## License

MIT License - Feel free to modify and distribute

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- The `.gitignore` file is configured to exclude `.env` files
- API keys should be treated as passwords

## Acknowledgments

- Inspired by Grammarly's text assistance functionality
- Powered by OpenAI's GPT models
