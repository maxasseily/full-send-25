"""
Shortcut Suggester - Main Application
Monitors user actions and suggests keyboard shortcuts to improve productivity
"""
import time
import signal
import sys
from datetime import datetime
from typing import Dict, Any

from input_monitor import InputMonitor
from window_tracker import WindowTracker
from pattern_detector import PatternDetector
from shortcut_db import ShortcutDatabase
from notification_ui import NotificationUI


class ShortcutSuggester:
    """Main application that coordinates all components"""
    
    def __init__(self):
        """Initialize the shortcut suggester"""
        print("🚀 Initializing Shortcut Suggester...")
        
        # Initialize components
        self.pattern_detector = PatternDetector(history_size=100)
        self.shortcut_db = ShortcutDatabase()
        self.notification_ui = NotificationUI(duration=7000, position='bottom-right')
        
        # Current application context
        self.current_app = None
        self.last_suggestion_time = None
        self.suggestion_cooldown = 30  # seconds between suggestions
        
        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'actions_tracked': 0,
            'patterns_detected': 0,
            'suggestions_shown': 0
        }
        
        # Initialize monitors with callbacks
        self.input_monitor = InputMonitor(on_event_callback=self.on_input_event)
        self.window_tracker = WindowTracker(
            on_window_change_callback=self.on_window_change,
            poll_interval=0.5
        )
        
        print("✅ Initialization complete")
    
    def on_input_event(self, event: Dict[str, Any]):
        """
        Handle input events (keyboard/mouse)
        
        Args:
            event: Event data from InputMonitor
        """
        # Add window context
        window_info = self.window_tracker.get_current_window()
        
        # Track the action
        self.pattern_detector.add_action(event, window_info)
        self.stats['actions_tracked'] += 1
        
        # Detect patterns every 10 actions
        if self.stats['actions_tracked'] % 10 == 0:
            self.check_for_patterns()
    
    def on_window_change(self, window_info: Dict[str, Any]):
        """
        Handle window change events
        
        Args:
            window_info: Window data from WindowTracker
        """
        process_name = window_info.get('process_name', 'Unknown')
        window_title = window_info.get('title', 'Untitled')
        
        print(f"\n📱 Switched to: {process_name} - {window_title[:50]}")
        
        self.current_app = process_name
        
        # Optionally show a random tip for the new application
        # Uncomment to enable tips on app switch
        # self.show_random_tip()
    
    def check_for_patterns(self):
        """Check for inefficient patterns and show suggestions"""
        patterns = self.pattern_detector.detect_patterns()
        
        if patterns:
            self.stats['patterns_detected'] += len(patterns)
            
            # Show the most recent pattern
            pattern = patterns[0]
            self.show_suggestion(pattern)
    
    def show_suggestion(self, suggestion: Dict[str, Any]):
        """
        Display a suggestion to the user
        
        Args:
            suggestion: Suggestion data from PatternDetector
        """
        # Check cooldown
        if self.last_suggestion_time:
            elapsed = (datetime.now() - self.last_suggestion_time).total_seconds()
            if elapsed < self.suggestion_cooldown:
                return  # Too soon
        
        print(f"\n💡 Pattern detected: {suggestion['type']}")
        print(f"   Suggestion: {suggestion['suggestion']}")
        
        # Show notification
        self.notification_ui.show_suggestion(
            suggestion,
            on_dismiss=self.on_suggestion_dismissed,
            on_learn_more=self.on_learn_more
        )
        
        self.last_suggestion_time = datetime.now()
        self.stats['suggestions_shown'] += 1
    
    def show_random_tip(self):
        """Show a random shortcut tip for the current application"""
        if not self.current_app:
            return
        
        tip = self.shortcut_db.get_random_tip(self.current_app)
        
        if tip:
            suggestion = {
                'type': 'tip',
                'shortcut': tip.get('keys', ''),
                'suggestion': f"{tip.get('action', 'Try this shortcut')}",
                'severity': 'low'
            }
            self.show_suggestion(suggestion)
    
    def on_suggestion_dismissed(self):
        """Handle when user dismisses a suggestion"""
        print("   User dismissed suggestion")
    
    def on_learn_more(self, suggestion: Dict[str, Any]):
        """
        Handle when user wants to learn more
        
        Args:
            suggestion: The suggestion they want to learn about
        """
        print("   User wants to learn more")
        
        # Show shortcuts for current app
        if self.current_app:
            shortcuts = self.shortcut_db.get_shortcuts_for_app(self.current_app)
            
            if shortcuts:
                app_data = self.shortcut_db.shortcuts.get('applications', {}).get(self.current_app, {})
                app_name = app_data.get('name', self.current_app)
                
                self.notification_ui.show_shortcut_list(shortcuts, app_name)
            else:
                # Show universal shortcuts
                shortcuts = self.shortcut_db.get_universal_shortcuts()
                self.notification_ui.show_shortcut_list(shortcuts, "Universal Shortcuts")
    
    def print_statistics(self):
        """Print current statistics"""
        runtime = datetime.now() - self.stats['start_time']
        
        print("\n" + "="*50)
        print("📊 STATISTICS")
        print("="*50)
        print(f"Runtime: {runtime}")
        print(f"Actions tracked: {self.stats['actions_tracked']}")
        print(f"Patterns detected: {self.stats['patterns_detected']}")
        print(f"Suggestions shown: {self.stats['suggestions_shown']}")
        
        # Pattern detector statistics
        pattern_stats = self.pattern_detector.get_statistics()
        print(f"\nKeyboard/Mouse breakdown:")
        print(f"  Keypresses: {pattern_stats.get('keypresses', 0)}")
        print(f"  Clicks: {pattern_stats.get('clicks', 0)}")
        print(f"  Shortcuts used: {pattern_stats.get('shortcuts_used', 0)}")
        print(f"  Shortcut ratio: {pattern_stats.get('shortcut_ratio', 0):.2%}")
        print("="*50 + "\n")
    
    def start(self):
        """Start the shortcut suggester"""
        print("\n" + "="*50)
        print("🎯 SHORTCUT SUGGESTER")
        print("="*50)
        print("Monitoring your actions to suggest helpful shortcuts")
        print("Press Ctrl+C to stop and view statistics")
        print("="*50 + "\n")
        
        # Start monitoring
        self.input_monitor.start()
        self.window_tracker.start()
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
                
                # Print periodic statistics every 60 seconds
                if self.stats['actions_tracked'] > 0 and self.stats['actions_tracked'] % 100 == 0:
                    self.print_statistics()
                    
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping...")
            self.stop()
    
    def stop(self):
        """Stop the shortcut suggester"""
        self.input_monitor.stop()
        self.window_tracker.stop()
        
        # Show final statistics
        self.print_statistics()
        
        print("👋 Thanks for using Shortcut Suggester!")
        print("   Keep learning those shortcuts! 🚀\n")


def main():
    """Main entry point"""
    suggester = ShortcutSuggester()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\n⏹️  Stopping...")
        suggester.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the application
    suggester.start()


if __name__ == "__main__":
    main()
