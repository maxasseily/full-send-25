"""
Notification UI - Displays shortcut suggestions to the user
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, Callable
import threading


class NotificationUI:
    """Displays non-intrusive notifications with shortcut suggestions"""
    
    def __init__(self, duration: int = 5000, position: str = 'bottom-right'):
        """
        Initialize the notification UI
        
        Args:
            duration: How long to show notification (milliseconds)
            position: Where to show notification ('bottom-right', 'top-right', etc.)
        """
        self.duration = duration
        self.position = position
        self.current_window = None
        self.is_showing = False
    
    def show_suggestion(self, suggestion: Dict[str, Any], 
                       on_dismiss: Optional[Callable] = None,
                       on_learn_more: Optional[Callable] = None):
        """
        Show a shortcut suggestion notification
        
        Args:
            suggestion: Suggestion data with 'type', 'suggestion', 'severity'
            on_dismiss: Callback when notification is dismissed
            on_learn_more: Callback when user wants more info
        """
        if self.is_showing:
            return  # Don't show multiple notifications at once
        
        self.is_showing = True
        
        # Create in separate thread to avoid blocking
        threading.Thread(
            target=self._create_notification,
            args=(suggestion, on_dismiss, on_learn_more),
            daemon=True
        ).start()
    
    def _create_notification(self, suggestion: Dict[str, Any],
                            on_dismiss: Optional[Callable],
                            on_learn_more: Optional[Callable]):
        """Create and display the notification window"""
        
        # Create a new toplevel window
        window = tk.Tk()
        window.title("Shortcut Tip")
        window.attributes('-topmost', True)
        window.attributes('-alpha', 0.95)  # Slightly transparent
        
        # Remove window decorations but keep close button
        window.overrideredirect(False)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Determine severity color
        severity_colors = {
            'low': '#4CAF50',      # Green
            'medium': '#FF9800',   # Orange
            'high': '#F44336'      # Red
        }
        severity = suggestion.get('severity', 'low')
        color = severity_colors.get(severity, '#2196F3')  # Default blue
        
        # Main frame with colored border
        main_frame = tk.Frame(window, bg=color, padx=2, pady=2)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        content_frame = tk.Frame(main_frame, bg='white', padx=15, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon and title
        header_frame = tk.Frame(content_frame, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        icon_label = tk.Label(header_frame, text="💡", font=('Segoe UI', 16), bg='white')
        icon_label.pack(side=tk.LEFT, padx=(0, 8))
        
        title_label = tk.Label(
            header_frame, 
            text="Shortcut Tip", 
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg='#333'
        )
        title_label.pack(side=tk.LEFT)
        
        # Suggestion text
        suggestion_text = suggestion.get('suggestion', 'Consider using keyboard shortcuts')
        text_label = tk.Label(
            content_frame,
            text=suggestion_text,
            font=('Segoe UI', 10),
            bg='white',
            fg='#555',
            wraplength=300,
            justify=tk.LEFT
        )
        text_label.pack(fill=tk.X, pady=(0, 15))
        
        # Additional info if available
        if 'shortcut' in suggestion:
            shortcut_frame = tk.Frame(content_frame, bg='#f5f5f5', padx=10, pady=8)
            shortcut_frame.pack(fill=tk.X, pady=(0, 10))
            
            shortcut_label = tk.Label(
                shortcut_frame,
                text=f"Shortcut: {suggestion['shortcut']}",
                font=('Segoe UI', 10, 'bold'),
                bg='#f5f5f5',
                fg='#1976D2'
            )
            shortcut_label.pack()
        
        # Buttons frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill=tk.X)
        
        def close_window():
            self.is_showing = False
            if on_dismiss:
                on_dismiss()
            window.destroy()
        
        def learn_more_clicked():
            self.is_showing = False
            if on_learn_more:
                on_learn_more(suggestion)
            window.destroy()
        
        # Dismiss button
        dismiss_btn = tk.Button(
            button_frame,
            text="Got it",
            command=close_window,
            font=('Segoe UI', 9),
            bg='#f0f0f0',
            fg='#333',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        dismiss_btn.pack(side=tk.RIGHT)
        
        # Learn more button
        if on_learn_more:
            learn_btn = tk.Button(
                button_frame,
                text="Learn More",
                command=learn_more_clicked,
                font=('Segoe UI', 9),
                bg=color,
                fg='white',
                relief=tk.FLAT,
                padx=15,
                pady=5,
                cursor='hand2'
            )
            learn_btn.pack(side=tk.RIGHT, padx=(0, 8))
        
        # Position window
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        if self.position == 'bottom-right':
            x = screen_width - width - 20
            y = screen_height - height - 60
        elif self.position == 'top-right':
            x = screen_width - width - 20
            y = 20
        elif self.position == 'bottom-left':
            x = 20
            y = screen_height - height - 60
        else:  # top-left
            x = 20
            y = 20
        
        window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Auto-dismiss after duration
        window.after(self.duration, close_window)
        
        # Store reference
        self.current_window = window
        
        # Run the window
        window.mainloop()
    
    def show_shortcut_list(self, shortcuts: list, app_name: str = "Application"):
        """
        Show a list of available shortcuts for an application
        
        Args:
            shortcuts: List of shortcut dictionaries
            app_name: Name of the application
        """
        # Create a new window
        window = tk.Tk()
        window.title(f"{app_name} - Keyboard Shortcuts")
        window.geometry("500x400")
        
        # Header
        header_frame = tk.Frame(window, bg='#2196F3', padx=15, pady=10)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text=f"⌨️ {app_name} Shortcuts",
            font=('Segoe UI', 14, 'bold'),
            bg='#2196F3',
            fg='white'
        )
        title_label.pack()
        
        # Scrollable frame
        container = tk.Frame(window)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Group shortcuts by category
        categories = {}
        for shortcut in shortcuts:
            category = shortcut.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(shortcut)
        
        # Display shortcuts by category
        for category, cat_shortcuts in categories.items():
            # Category header
            cat_label = tk.Label(
                scrollable_frame,
                text=category.capitalize(),
                font=('Segoe UI', 11, 'bold'),
                fg='#1976D2',
                anchor='w'
            )
            cat_label.pack(fill=tk.X, pady=(10, 5))
            
            # Shortcuts in this category
            for shortcut in cat_shortcuts:
                shortcut_frame = tk.Frame(scrollable_frame, bg='#f5f5f5', padx=10, pady=5)
                shortcut_frame.pack(fill=tk.X, pady=2)
                
                keys_label = tk.Label(
                    shortcut_frame,
                    text=shortcut.get('keys', ''),
                    font=('Consolas', 10, 'bold'),
                    bg='#f5f5f5',
                    fg='#d32f2f',
                    width=20,
                    anchor='w'
                )
                keys_label.pack(side=tk.LEFT)
                
                action_label = tk.Label(
                    shortcut_frame,
                    text=shortcut.get('action', ''),
                    font=('Segoe UI', 9),
                    bg='#f5f5f5',
                    fg='#333',
                    anchor='w'
                )
                action_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        close_btn = tk.Button(
            window,
            text="Close",
            command=window.destroy,
            font=('Segoe UI', 10),
            bg='#2196F3',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        close_btn.pack(pady=10)
        
        window.mainloop()
