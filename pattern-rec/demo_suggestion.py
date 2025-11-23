"""
Demo Script - Displays a shortcut suggestion after 4 seconds
Demonstrates the notification system without requiring user interaction
"""
import time
import tkinter as tk
from tkinter import ttk


def demo_suggestion():
    """Show a sample suggestion after 4 seconds"""
    print("🚀 Shortcut Suggester - Demo Mode")
    print("=" * 60)
    print("\nThis demo will show a suggestion in 4 seconds...")
    print("No user interaction required!\n")
    
    # Countdown
    for i in range(4, 0, -1):
        print(f"Showing suggestion in {i} seconds...", end='\r')
        time.sleep(1)
    
    print("\n\n💡 Displaying suggestion now...")
    
    # Create the main window
    window = tk.Tk()
    window.title("Shortcut Tip")
    window.attributes('-topmost', True)
    window.attributes('-alpha', 0.95)
    
    # Severity color
    color = '#FF9800'  # Orange for medium severity
    
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
    suggestion_text = 'Duplicate the current line or selection downward. Great for quickly copying code!'
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
    
    # Shortcut highlight
    shortcut_frame = tk.Frame(content_frame, bg='#f5f5f5', padx=10, pady=8)
    shortcut_frame.pack(fill=tk.X, pady=(0, 10))
    
    shortcut_label = tk.Label(
        shortcut_frame,
        text="Shortcut: Shift+Alt+Down",
        font=('Segoe UI', 10, 'bold'),
        bg='#f5f5f5',
        fg='#1976D2'
    )
    shortcut_label.pack()
    
    # Buttons frame
    button_frame = tk.Frame(content_frame, bg='white')
    button_frame.pack(fill=tk.X)
    
    def close_window():
        print("\n✅ User dismissed the suggestion")
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
    
    # Position window at bottom-right
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = screen_width - width - 20
    y = screen_height - height - 60
    
    window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Auto-dismiss after 10 seconds
    window.after(18000, close_window)
    
    print("\n" + "=" * 60)
    print("Demo running! The notification will auto-dismiss after 10 seconds.")
    print("=" * 60)
    
    # Run the window
    window.mainloop()


if __name__ == "__main__":
    demo_suggestion()
