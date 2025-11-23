"""
Shortcut Database - Manages application-specific keyboard shortcuts
"""
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


class ShortcutDatabase:
    """Manages a database of application shortcuts and tips"""
    
    def __init__(self, db_path: str = "shortcuts.json"):
        """
        Initialize the shortcut database
        
        Args:
            db_path: Path to the JSON database file
        """
        self.db_path = db_path
        self.shortcuts = self._load_database()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load shortcuts from JSON file or create default database"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading shortcuts database: {e}")
                return self._create_default_database()
        else:
            return self._create_default_database()
    
    def _create_default_database(self) -> Dict[str, Any]:
        """Create a default database with common shortcuts"""
        default_db = {
            "applications": {
                "chrome.exe": {
                    "name": "Google Chrome",
                    "shortcuts": [
                        {"keys": "Ctrl+T", "action": "New tab", "category": "navigation"},
                        {"keys": "Ctrl+W", "action": "Close tab", "category": "navigation"},
                        {"keys": "Ctrl+Shift+T", "action": "Reopen closed tab", "category": "navigation"},
                        {"keys": "Ctrl+L", "action": "Focus address bar", "category": "navigation"},
                        {"keys": "Ctrl+Shift+N", "action": "New incognito window", "category": "window"},
                        {"keys": "Ctrl+Tab", "action": "Next tab", "category": "navigation"},
                        {"keys": "Ctrl+Shift+Tab", "action": "Previous tab", "category": "navigation"},
                        {"keys": "F6", "action": "Switch focus between address bar and page", "category": "navigation"}
                    ]
                },
                "Code.exe": {
                    "name": "Visual Studio Code",
                    "shortcuts": [
                        {"keys": "Ctrl+P", "action": "Quick file open", "category": "navigation"},
                        {"keys": "Ctrl+Shift+P", "action": "Command palette", "category": "general"},
                        {"keys": "Ctrl+`", "action": "Toggle terminal", "category": "view"},
                        {"keys": "Ctrl+B", "action": "Toggle sidebar", "category": "view"},
                        {"keys": "Ctrl+/", "action": "Toggle comment", "category": "editing"},
                        {"keys": "Alt+Up/Down", "action": "Move line up/down", "category": "editing"},
                        {"keys": "Ctrl+D", "action": "Select next occurrence", "category": "editing"},
                        {"keys": "Ctrl+Shift+K", "action": "Delete line", "category": "editing"},
                        {"keys": "F12", "action": "Go to definition", "category": "navigation"}
                    ]
                },
                "EXCEL.EXE": {
                    "name": "Microsoft Excel",
                    "shortcuts": [
                        {"keys": "Ctrl+Arrow", "action": "Jump to edge of data region", "category": "navigation"},
                        {"keys": "Ctrl+Shift+L", "action": "Toggle filters", "category": "data"},
                        {"keys": "Alt+=", "action": "AutoSum", "category": "formula"},
                        {"keys": "Ctrl+1", "action": "Format cells dialog", "category": "formatting"},
                        {"keys": "F2", "action": "Edit active cell", "category": "editing"},
                        {"keys": "Ctrl+Space", "action": "Select entire column", "category": "selection"},
                        {"keys": "Shift+Space", "action": "Select entire row", "category": "selection"}
                    ]
                },
                "WINWORD.EXE": {
                    "name": "Microsoft Word",
                    "shortcuts": [
                        {"keys": "Ctrl+H", "action": "Find and replace", "category": "editing"},
                        {"keys": "Ctrl+Shift+C", "action": "Copy formatting", "category": "formatting"},
                        {"keys": "Ctrl+Shift+V", "action": "Paste formatting", "category": "formatting"},
                        {"keys": "Ctrl+E", "action": "Center align", "category": "formatting"},
                        {"keys": "Ctrl+L", "action": "Left align", "category": "formatting"},
                        {"keys": "Ctrl+R", "action": "Right align", "category": "formatting"},
                        {"keys": "Ctrl+]", "action": "Increase font size", "category": "formatting"},
                        {"keys": "Ctrl+[", "action": "Decrease font size", "category": "formatting"}
                    ]
                },
                "explorer.exe": {
                    "name": "Windows Explorer",
                    "shortcuts": [
                        {"keys": "Ctrl+N", "action": "New window", "category": "window"},
                        {"keys": "Ctrl+Shift+N", "action": "New folder", "category": "file"},
                        {"keys": "F2", "action": "Rename", "category": "file"},
                        {"keys": "Alt+Enter", "action": "Properties", "category": "file"},
                        {"keys": "Ctrl+Shift+E", "action": "Display all folders", "category": "navigation"},
                        {"keys": "Alt+Up", "action": "Go to parent folder", "category": "navigation"},
                        {"keys": "Backspace", "action": "Go back", "category": "navigation"}
                    ]
                }
            },
            "universal_shortcuts": [
                {"keys": "Ctrl+C", "action": "Copy", "category": "clipboard"},
                {"keys": "Ctrl+V", "action": "Paste", "category": "clipboard"},
                {"keys": "Ctrl+X", "action": "Cut", "category": "clipboard"},
                {"keys": "Ctrl+Z", "action": "Undo", "category": "editing"},
                {"keys": "Ctrl+Y", "action": "Redo", "category": "editing"},
                {"keys": "Ctrl+A", "action": "Select all", "category": "selection"},
                {"keys": "Ctrl+F", "action": "Find", "category": "search"},
                {"keys": "Ctrl+S", "action": "Save", "category": "file"},
                {"keys": "Alt+F4", "action": "Close window", "category": "window"},
                {"keys": "Win+V", "action": "Clipboard history", "category": "clipboard"}
            ]
        }
        
        # Save default database
        self.save_database(default_db)
        return default_db
    
    def save_database(self, data: Optional[Dict[str, Any]] = None):
        """Save shortcuts database to file"""
        data_to_save = data if data is not None else self.shortcuts
        
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, indent=2, fp=f)
        except Exception as e:
            print(f"Error saving shortcuts database: {e}")
    
    def get_shortcuts_for_app(self, process_name: str) -> List[Dict[str, str]]:
        """
        Get shortcuts for a specific application
        
        Args:
            process_name: Name of the process (e.g., 'chrome.exe')
            
        Returns:
            List of shortcut dictionaries
        """
        app_data = self.shortcuts.get('applications', {}).get(process_name, {})
        return app_data.get('shortcuts', [])
    
    def get_universal_shortcuts(self) -> List[Dict[str, str]]:
        """Get universal shortcuts that work in most applications"""
        return self.shortcuts.get('universal_shortcuts', [])
    
    def search_shortcuts(self, query: str, process_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for shortcuts by action or keys
        
        Args:
            query: Search query
            process_name: Optional process name to limit search
            
        Returns:
            List of matching shortcuts with app context
        """
        results = []
        query_lower = query.lower()
        
        # Search app-specific shortcuts
        apps_to_search = {}
        if process_name:
            app_data = self.shortcuts.get('applications', {}).get(process_name)
            if app_data:
                apps_to_search[process_name] = app_data
        else:
            apps_to_search = self.shortcuts.get('applications', {})
        
        for app_name, app_data in apps_to_search.items():
            for shortcut in app_data.get('shortcuts', []):
                if (query_lower in shortcut.get('action', '').lower() or
                    query_lower in shortcut.get('keys', '').lower()):
                    results.append({
                        **shortcut,
                        'app': app_data.get('name', app_name),
                        'process': app_name
                    })
        
        # Search universal shortcuts
        for shortcut in self.shortcuts.get('universal_shortcuts', []):
            if (query_lower in shortcut.get('action', '').lower() or
                query_lower in shortcut.get('keys', '').lower()):
                results.append({
                    **shortcut,
                    'app': 'Universal',
                    'process': None
                })
        
        return results
    
    def get_random_tip(self, process_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a random shortcut tip
        
        Args:
            process_name: Optional process name to get app-specific tip
            
        Returns:
            Random shortcut or None
        """
        import random
        
        shortcuts = []
        
        if process_name:
            shortcuts = self.get_shortcuts_for_app(process_name)
        
        # Add some universal shortcuts too
        universal = self.get_universal_shortcuts()
        shortcuts.extend(universal[:5])  # Add a few universal ones
        
        if shortcuts:
            return random.choice(shortcuts)
        
        return None
    
    def add_custom_shortcut(self, process_name: str, shortcut: Dict[str, str]):
        """
        Add a custom shortcut for an application
        
        Args:
            process_name: Name of the process
            shortcut: Shortcut dictionary with 'keys', 'action', 'category'
        """
        if 'applications' not in self.shortcuts:
            self.shortcuts['applications'] = {}
        
        if process_name not in self.shortcuts['applications']:
            self.shortcuts['applications'][process_name] = {
                'name': process_name,
                'shortcuts': []
            }
        
        self.shortcuts['applications'][process_name]['shortcuts'].append(shortcut)
        self.save_database()
