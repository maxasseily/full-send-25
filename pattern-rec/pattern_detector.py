"""
Pattern Detector - Analyzes user actions to detect inefficient patterns
Enhanced with pywinauto for UI element detection
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import deque
import threading

try:
    from pywinauto import Desktop, Application
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    print("Warning: pywinauto not available. Advanced UI detection disabled.")


class PatternDetector:
    """Detects patterns in user actions that could be optimized with shortcuts"""
    
    def __init__(self, history_size: int = 100):
        """
        Initialize the pattern detector
        
        Args:
            history_size: Number of recent actions to keep in memory
        """
        self.action_history = deque(maxlen=history_size)
        self.patterns_detected = []
        self.ui_cache = {}  # Cache UI element information
        self.last_ui_check = None
        self.pywinauto_enabled = PYWINAUTO_AVAILABLE
        
    def add_action(self, action: Dict[str, Any], window_info: Optional[Dict[str, Any]] = None):
        """
        Add an action to the history
        
        Args:
            action: Action event (keypress or click)
            window_info: Current window information
        """
        action_with_context = {
            **action,
            'window': window_info
        }
        self.action_history.append(action_with_context)
    
    def detect_patterns(self) -> List[Dict[str, Any]]:
        """
        Analyze recent actions and detect inefficient patterns
        
        Returns:
            List of detected patterns with suggestions
        """
        detected = []
        
        # Pattern 1: Repeated copy actions (Ctrl+C multiple times)
        repeated_copy = self._detect_repeated_shortcut('ctrl', 'c', 3, 10)
        if repeated_copy:
            detected.append(repeated_copy)
        
        # Pattern 2: Multiple menu clicks (could use keyboard)
        menu_clicks = self._detect_menu_clicks(3, 20)
        if menu_clicks:
            detected.append(menu_clicks)
        
        # Pattern 3: Repeated Find (Ctrl+F)
        repeated_find = self._detect_repeated_shortcut('ctrl', 'f', 2, 30)
        if repeated_find:
            detected.append(repeated_find)
        
        # Pattern 4: Manual selection without Shift
        manual_selection = self._detect_manual_selection()
        if manual_selection:
            detected.append(manual_selection)
        
        # Pattern 5: Undo spam (Ctrl+Z repeatedly)
        undo_spam = self._detect_repeated_shortcut('ctrl', 'z', 4, 15)
        if undo_spam:
            detected.append(undo_spam)
        
        # Pattern 6: Dialog box interactions (pywinauto)
        if self.pywinauto_enabled:
            dialog_pattern = self._detect_dialog_navigation()
            if dialog_pattern:
                detected.append(dialog_pattern)
            
            # Pattern 7: Ribbon/Toolbar clicks
            ribbon_pattern = self._detect_ribbon_usage()
            if ribbon_pattern:
                detected.append(ribbon_pattern)
            
            # Pattern 8: Form filling inefficiencies
            form_pattern = self._detect_form_filling()
            if form_pattern:
                detected.append(form_pattern)
        
        return detected
    
    def _detect_repeated_shortcut(self, modifier: str, key: str, 
                                   min_count: int, within_seconds: int) -> Optional[Dict[str, Any]]:
        """Detect if a shortcut is being used repeatedly"""
        if len(self.action_history) < min_count:
            return None
        
        cutoff_time = datetime.now() - timedelta(seconds=within_seconds)
        
        matching_actions = [
            action for action in self.action_history
            if (action['type'] == 'keypress' and
                modifier in action.get('modifiers', []) and
                action.get('key', '').lower() == key.lower() and
                action['timestamp'] > cutoff_time)
        ]
        
        if len(matching_actions) >= min_count:
            return {
                'type': 'repeated_shortcut',
                'shortcut': f'{modifier.capitalize()}+{key.upper()}',
                'count': len(matching_actions),
                'suggestion': self._get_shortcut_suggestion(modifier, key),
                'severity': 'low',
                'timestamp': datetime.now()
            }
        
        return None
    
    def _detect_menu_clicks(self, min_count: int, within_seconds: int) -> Optional[Dict[str, Any]]:
        """Detect multiple menu bar clicks"""
        if len(self.action_history) < min_count:
            return None
        
        cutoff_time = datetime.now() - timedelta(seconds=within_seconds)
        
        # Look for clicks in the top portion of screen (likely menu bar)
        menu_clicks = [
            action for action in self.action_history
            if (action['type'] == 'click' and
                action.get('position', (0, 0))[1] < 100 and  # Top 100 pixels
                action['timestamp'] > cutoff_time)
        ]
        
        if len(menu_clicks) >= min_count:
            window = menu_clicks[-1].get('window')
            app_name = window.get('process_name', 'this app') if window else 'this app'
            
            return {
                'type': 'menu_navigation',
                'count': len(menu_clicks),
                'suggestion': f'Consider learning keyboard shortcuts for {app_name}',
                'severity': 'medium',
                'timestamp': datetime.now()
            }
        
        return None
    
    def _detect_manual_selection(self) -> Optional[Dict[str, Any]]:
        """Detect manual text selection without using keyboard shortcuts"""
        if len(self.action_history) < 5:
            return None
        
        recent = list(self.action_history)[-10:]
        
        # Look for click-drag pattern (multiple clicks close together)
        click_count = sum(1 for a in recent if a['type'] == 'click')
        
        if click_count >= 3:
            # Check if no Shift key was used
            has_shift_select = any(
                a['type'] == 'keypress' and 'shift' in a.get('modifiers', [])
                for a in recent
            )
            
            if not has_shift_select:
                return {
                    'type': 'manual_selection',
                    'suggestion': 'Use Shift+Arrow keys or Shift+Click for faster text selection',
                    'severity': 'low',
                    'timestamp': datetime.now()
                }
        
        return None
    
    def _get_shortcut_suggestion(self, modifier: str, key: str) -> str:
        """Get a helpful suggestion for a repeated shortcut"""
        shortcut = f'{modifier}+{key}'.lower()
        
        suggestions = {
            'ctrl+c': 'Frequent copying detected. Consider using clipboard managers like Ditto or Windows Clipboard History (Win+V)',
            'ctrl+f': 'Use F3 to find next occurrence without reopening Find dialog',
            'ctrl+z': 'Multiple undo detected. Consider Ctrl+Y to redo, or review changes before undoing',
            'ctrl+s': 'Great! You\'re saving frequently. Many apps also have auto-save features.',
        }
        
        return suggestions.get(shortcut, f'You use {modifier.upper()}+{key.upper()} frequently')
    
    def _get_ui_element_at_position(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Get UI element information at screen position using pywinauto"""
        if not self.pywinauto_enabled:
            return None
        
        try:
            # Use Desktop to find element at coordinates
            desktop = Desktop(backend='uia')
            element = desktop.from_point(x, y)
            
            if element:
                return {
                    'control_type': element.element_info.control_type,
                    'class_name': element.element_info.class_name,
                    'name': element.element_info.name,
                    'automation_id': element.element_info.automation_id,
                    'is_enabled': element.element_info.enabled,
                    'rect': element.element_info.rectangle,
                }
        except Exception as e:
            # Silently fail for performance
            pass
        
        return None
    
    def _detect_dialog_navigation(self) -> Optional[Dict[str, Any]]:
        """Detect inefficient dialog box navigation (clicking through dialogs)"""
        if len(self.action_history) < 3:
            return None
        
        cutoff_time = datetime.now() - timedelta(seconds=15)
        recent_clicks = [
            action for action in self.action_history
            if (action['type'] == 'click' and
                action['timestamp'] > cutoff_time)
        ]
        
        if len(recent_clicks) < 3:
            return None
        
        # Check if clicks were on buttons (likely OK/Cancel/Next)
        button_clicks = 0
        for click in recent_clicks:
            pos = click.get('position')
            if pos:
                element = self._get_ui_element_at_position(pos[0], pos[1])
                if element and 'button' in element.get('control_type', '').lower():
                    button_clicks += 1
        
        if button_clicks >= 3:
            return {
                'type': 'dialog_navigation',
                'count': button_clicks,
                'suggestion': 'Use Tab to navigate between dialog fields, Enter to accept, and Esc to cancel',
                'severity': 'medium',
                'timestamp': datetime.now()
            }
        
        return None
    
    def _detect_ribbon_usage(self) -> Optional[Dict[str, Any]]:
        """Detect frequent ribbon/toolbar usage in Office apps"""
        if len(self.action_history) < 4:
            return None
        
        cutoff_time = datetime.now() - timedelta(seconds=30)
        recent_clicks = [
            action for action in self.action_history
            if (action['type'] == 'click' and
                action['timestamp'] > cutoff_time)
        ]
        
        if len(recent_clicks) < 4:
            return None
        
        # Check if clicks are in top area (ribbon area) and on tabs/buttons
        ribbon_clicks = 0
        for click in recent_clicks:
            pos = click.get('position')
            if pos and pos[1] < 200:  # Top 200 pixels
                element = self._get_ui_element_at_position(pos[0], pos[1])
                if element:
                    control_type = element.get('control_type', '').lower()
                    if any(t in control_type for t in ['tab', 'button', 'menuitem']):
                        ribbon_clicks += 1
        
        if ribbon_clicks >= 4:
            window = recent_clicks[-1].get('window')
            app_name = window.get('process_name', 'this app') if window else 'this app'
            
            return {
                'type': 'ribbon_navigation',
                'count': ribbon_clicks,
                'suggestion': f'Learn keyboard shortcuts for common {app_name} ribbon actions. Press Alt to see shortcut keys.',
                'severity': 'high',
                'timestamp': datetime.now()
            }
        
        return None
    
    def _detect_form_filling(self) -> Optional[Dict[str, Any]]:
        """Detect inefficient form filling (mouse between fields instead of Tab)"""
        if len(self.action_history) < 6:
            return None
        
        cutoff_time = datetime.now() - timedelta(seconds=20)
        recent_actions = [
            action for action in self.action_history
            if action['timestamp'] > cutoff_time
        ]
        
        # Look for pattern: click -> type -> click -> type
        pattern_score = 0
        edit_field_clicks = 0
        
        for i in range(len(recent_actions) - 1):
            curr = recent_actions[i]
            next_action = recent_actions[i + 1]
            
            if curr['type'] == 'click' and next_action['type'] == 'keypress':
                # Check if click was on an edit field
                pos = curr.get('position')
                if pos:
                    element = self._get_ui_element_at_position(pos[0], pos[1])
                    if element:
                        control_type = element.get('control_type', '').lower()
                        if 'edit' in control_type or 'text' in control_type:
                            edit_field_clicks += 1
                            pattern_score += 1
        
        # Check if Tab key was used
        tab_usage = sum(
            1 for a in recent_actions
            if a['type'] == 'keypress' and a.get('key', '').lower() == 'tab'
        )
        
        if edit_field_clicks >= 3 and tab_usage == 0:
            return {
                'type': 'form_navigation',
                'count': edit_field_clicks,
                'suggestion': 'Use Tab to move between form fields instead of clicking. Shift+Tab to go back.',
                'severity': 'medium',
                'timestamp': datetime.now()
            }
        
        return None
    
    def get_ui_element_info(self, x: int, y: int) -> Dict[str, Any]:
        """Public method to get UI element info for debugging/logging"""
        element = self._get_ui_element_at_position(x, y)
        if element:
            return element
        return {'error': 'No element found or pywinauto not available'}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected patterns"""
        if not self.action_history:
            return {'total_actions': 0}
        
        total_actions = len(self.action_history)
        keypresses = sum(1 for a in self.action_history if a['type'] == 'keypress')
        clicks = sum(1 for a in self.action_history if a['type'] == 'click')
        
        # Count shortcut usage
        shortcuts_used = sum(
            1 for a in self.action_history 
            if a['type'] == 'keypress' and a.get('modifiers')
        )
        
        return {
            'total_actions': total_actions,
            'keypresses': keypresses,
            'clicks': clicks,
            'shortcuts_used': shortcuts_used,
            'shortcut_ratio': shortcuts_used / total_actions if total_actions > 0 else 0,
            'pywinauto_enabled': self.pywinauto_enabled
        }
