# 🚀 Shortcut Suggester

A Python-based productivity tool that monitors your computer usage and suggests keyboard shortcuts to help you work more efficiently.

## 🎯 What It Does

Shortcut Suggester runs in the background and:
- **Monitors** your keyboard and mouse actions
- **Detects** inefficient patterns (like repeated menu clicks)
- **Suggests** relevant keyboard shortcuts
- **Teaches** you application-specific shortcuts
- **Tracks** your progress over time

## ✨ Features

### Pattern Detection
- 🔄 **Repeated Actions**: Detects when you use Ctrl+C, Ctrl+F, or Ctrl+Z multiple times
- 🖱️ **Menu Navigation**: Identifies when you click through menus repeatedly
- ✂️ **Manual Selection**: Notices inefficient text selection methods
- 📊 **Smart Suggestions**: Context-aware tips based on your current application
- 🎯 **Dialog Navigation**: Detects inefficient dialog box interactions (with pywinauto)
- 🎨 **Ribbon/Toolbar Clicks**: Identifies Office ribbon usage patterns
- 📝 **Form Filling**: Detects mouse-heavy form navigation instead of Tab key

### Shortcut Database
- Pre-loaded shortcuts for popular applications:
  - 🌐 Google Chrome
  - 💻 Visual Studio Code
  - 📊 Microsoft Excel
  - 📝 Microsoft Word
  - 📁 Windows Explorer
  - And more!
- 🌍 Universal shortcuts that work everywhere
- 🔧 Customizable - add your own shortcuts

### User Interface
- 💡 Non-intrusive notifications
- 🎨 Color-coded by severity (low/medium/high)
- 📋 Detailed shortcut reference lists
- ⏱️ Auto-dismiss after configurable time

## 📋 Requirements

- **Python 3.7+**
- **Windows** (for window tracking features)
- Administrator privileges may be needed for system-wide monitoring

## 🛠️ Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Manual Installation (if needed)

```bash
pip install pynput pywin32 psutil pywinauto
```

**Note:** `pywinauto` enables advanced UI element detection for dialog boxes, ribbons, and form fields.

## 🚀 Quick Start

### Basic Usage

```bash
python main.py
```

The application will:
1. Start monitoring your keyboard and mouse
2. Track active window changes
3. Detect patterns in your actions
4. Show helpful suggestions when patterns are found

Press **Ctrl+C** to stop and view statistics.

## 📖 Usage Examples

### Running in Background

```python
from main import ShortcutSuggester

suggester = ShortcutSuggester()
suggester.start()
```

### Customizing Configuration

Edit `config.json` to customize:
- Notification duration and position
- Pattern detection thresholds
- Feature toggles
- Database location

```json
{
  "ui": {
    "notification_duration_ms": 7000,
    "notification_position": "bottom-right"
  }
}
```

### Adding Custom Shortcuts

```python
from shortcut_db import ShortcutDatabase

db = ShortcutDatabase()
db.add_custom_shortcut('myapp.exe', {
    'keys': 'Ctrl+Shift+X',
    'action': 'Special feature',
    'category': 'custom'
})
```

## 🏗️ Architecture

```
pattern-rec/
├── main.py                  # Main application entry point
├── input_monitor.py         # Keyboard/mouse event tracking
├── window_tracker.py        # Active window detection
├── pattern_detector.py      # Pattern analysis engine (with pywinauto)
├── shortcut_db.py          # Shortcut database manager
├── notification_ui.py       # Notification display system
├── config.json             # Configuration settings
├── shortcuts.json          # Shortcut database (auto-generated)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎓 How It Works

### 1. Input Monitoring
The `InputMonitor` class uses `pynput` to listen for:
- Keyboard presses (including modifier keys)
- Mouse clicks
- Key combinations

### 2. Window Tracking
The `WindowTracker` polls the active window every 500ms using `pywin32`:
- Gets window title
- Identifies process name
- Tracks application context

### 3. Pattern Detection (Enhanced with pywinauto)
The `PatternDetector` analyzes action sequences:
- Maintains a rolling history of 100 actions
- Detects repeated shortcuts
- Identifies inefficient workflows
- **UI Element Analysis**: Uses pywinauto to detect clicks on buttons, menus, and form fields
- **Dialog Detection**: Recognizes when users click through dialog boxes
- **Ribbon Analysis**: Identifies Office ribbon/toolbar usage patterns
- **Form Navigation**: Detects mouse-heavy form filling
- Suggests better alternatives

### 4. Smart Suggestions
When a pattern is detected:
- Checks cooldown period (default: 30 seconds)
- Retrieves relevant shortcuts from database
- Displays non-intrusive notification
- Offers "Learn More" for detailed shortcuts

## 📊 Statistics

View your productivity metrics:
```
📊 STATISTICS
==================================================
Runtime: 0:15:23
Actions tracked: 342
Patterns detected: 8
Suggestions shown: 5

Keyboard/Mouse breakdown:
  Keypresses: 287
  Clicks: 55
  Shortcuts used: 42
  Shortcut ratio: 14.62%
  Pywinauto enabled: True
==================================================
```

## 🔧 Configuration Options

### Detection Sensitivity

Adjust in `config.json`:

```json
{
  "detection": {
    "patterns": {
      "repeated_copy": {
        "enabled": true,
        "min_count": 3,
        "within_seconds": 10
      }
    }
  }
}
```

### UI Customization

```json
{
  "ui": {
    "notification_position": "bottom-right",  // or top-right, bottom-left, top-left
    "notification_duration_ms": 7000,
    "show_tips_on_app_switch": false
  }
}
```

## 🚀 Advanced Features

### Learning Mode
Uncomment in `main.py` to show random tips on app switch:

```python
def on_window_change(self, window_info):
    # ...
    self.show_random_tip()  # Enable this
```

### Custom Patterns
Add your own pattern detection in `pattern_detector.py`:

```python
def _detect_custom_pattern(self):
    # Your pattern logic here
    pass
```

## 📦 Distribution

### Create Executable with PyInstaller

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

### Using Auto-Py-To-Exe (GUI)

```bash
pip install auto-py-to-exe
auto-py-to-exe
```

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install --upgrade -r requirements.txt
```

### Window tracking not working
- Ensure `pywin32` is installed: `pip install pywin32`
- Run as administrator if needed

### Notifications not appearing
- Check if Python has GUI permissions
- Verify `tkinter` is installed (usually built-in)

## 🤝 Contributing

Ideas for contributions:
- Add support for macOS/Linux
- Machine learning for personalized suggestions
- Cloud sync for shortcuts database
- Integration with popular productivity apps
- Voice commands for learning shortcuts

## 📝 License

This is a learning/prototype project. Feel free to use and modify!

## 🎯 Future Enhancements

- [ ] ML-based pattern prediction
- [ ] Cloud backup of learned patterns
- [ ] Team sharing of custom shortcuts
- [ ] Gamification (streak tracking, achievements)
- [ ] Voice announcements (optional)
- [ ] Browser extension integration
- [ ] Mobile companion app

## 💡 Tips for Best Results

1. **Run continuously** - The more data, the better the suggestions
2. **Don't ignore suggestions** - Try the shortcuts it recommends
3. **Review statistics** - Track your improvement over time
4. **Customize the database** - Add shortcuts for your specific apps
5. **Adjust sensitivity** - Tune detection thresholds to your workflow

## 🙏 Acknowledgments

Built with:
- **pynput** - Cross-platform input monitoring
- **pywin32** - Windows API integration
- **psutil** - Process utilities
- **tkinter** - GUI framework

## 📧 Support

For issues or questions, create an issue in the repository or check the code comments for inline documentation.

---

**Happy shortcutting! ⌨️🚀**
