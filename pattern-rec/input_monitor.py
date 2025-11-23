"""
Input Monitor - Tracks keyboard and mouse events
"""
from pynput import keyboard, mouse
from datetime import datetime
from typing import Callable, Dict, Any
import threading


class InputMonitor:
    """Monitors keyboard and mouse input events"""
    
    def __init__(self, on_event_callback: Callable[[Dict[str, Any]], None]):
        """
        Initialize the input monitor
        
        Args:
            on_event_callback: Function to call when an event occurs
        """
        self.on_event_callback = on_event_callback
        self.keyboard_listener = None
        self.mouse_listener = None
        self.is_running = False
        self.current_modifiers = set()
        
    def on_key_press(self, key):
        """Handle keyboard press events"""
        try:
            # Track modifiers
            if key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                self.current_modifiers.add('ctrl')
            elif key in [keyboard.Key.alt_l, keyboard.Key.alt_r]:
                self.current_modifiers.add('alt')
            elif key in [keyboard.Key.shift_l, keyboard.Key.shift_r]:
                self.current_modifiers.add('shift')
            elif key == keyboard.Key.cmd:
                self.current_modifiers.add('win')
            
            # Build key string
            key_str = self._get_key_string(key)
            
            event = {
                'type': 'keypress',
                'key': key_str,
                'modifiers': list(self.current_modifiers),
                'timestamp': datetime.now()
            }
            self.on_event_callback(event)
            
        except Exception as e:
            print(f"Error in key press handler: {e}")
    
    def on_key_release(self, key):
        """Handle keyboard release events"""
        try:
            # Remove modifiers
            if key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                self.current_modifiers.discard('ctrl')
            elif key in [keyboard.Key.alt_l, keyboard.Key.alt_r]:
                self.current_modifiers.discard('alt')
            elif key in [keyboard.Key.shift_l, keyboard.Key.shift_r]:
                self.current_modifiers.discard('shift')
            elif key == keyboard.Key.cmd:
                self.current_modifiers.discard('win')
                
        except Exception as e:
            print(f"Error in key release handler: {e}")
    
    def on_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if pressed:  # Only track press, not release
            try:
                event = {
                    'type': 'click',
                    'position': (x, y),
                    'button': str(button).replace('Button.', ''),
                    'timestamp': datetime.now()
                }
                self.on_event_callback(event)
            except Exception as e:
                print(f"Error in click handler: {e}")
    
    def _get_key_string(self, key) -> str:
        """Convert key object to readable string"""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char
            else:
                # Special keys
                key_name = str(key).replace('Key.', '')
                return key_name
        except:
            return str(key)
    
    def start(self):
        """Start monitoring input events"""
        if self.is_running:
            print("Monitor already running")
            return
        
        self.is_running = True
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click
        )
        self.mouse_listener.start()
        
        print("Input monitoring started")
    
    def stop(self):
        """Stop monitoring input events"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        print("Input monitoring stopped")
