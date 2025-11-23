"""
Window Tracker - Tracks active window and application context
"""
import threading
import time
from datetime import datetime
from typing import Callable, Dict, Any, Optional

try:
    import win32gui
    import win32process
    import psutil
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    print("Warning: Windows-specific modules not available. Window tracking disabled.")


class WindowTracker:
    """Tracks the currently active window and application"""
    
    def __init__(self, on_window_change_callback: Callable[[Dict[str, Any]], None], 
                 poll_interval: float = 0.5):
        """
        Initialize the window tracker
        
        Args:
            on_window_change_callback: Function to call when window changes
            poll_interval: How often to check for window changes (seconds)
        """
        self.on_window_change_callback = on_window_change_callback
        self.poll_interval = poll_interval
        self.is_running = False
        self.current_window = None
        self.monitor_thread = None
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently active window
        
        Returns:
            Dictionary with window info or None if unavailable
        """
        if not WINDOWS_AVAILABLE:
            return None
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process information
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            process_name = process.name()
            process_path = process.exe()
            
            return {
                'hwnd': hwnd,
                'title': window_title,
                'process_name': process_name,
                'process_path': process_path,
                'pid': pid,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error getting active window: {e}")
            return None
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread"""
        while self.is_running:
            try:
                window_info = self.get_active_window()
                
                if window_info:
                    # Check if window changed
                    if (self.current_window is None or 
                        window_info['hwnd'] != self.current_window.get('hwnd')):
                        
                        self.current_window = window_info
                        self.on_window_change_callback(window_info)
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                print(f"Error in window monitor loop: {e}")
                time.sleep(self.poll_interval)
    
    def start(self):
        """Start monitoring window changes"""
        if self.is_running:
            print("Window tracker already running")
            return
        
        if not WINDOWS_AVAILABLE:
            print("Cannot start window tracker: Windows modules not available")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Window tracking started")
    
    def stop(self):
        """Stop monitoring window changes"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        print("Window tracking stopped")
    
    def get_current_window(self) -> Optional[Dict[str, Any]]:
        """Get the most recently tracked window"""
        return self.current_window
