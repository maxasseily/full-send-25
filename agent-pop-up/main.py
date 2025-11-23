"""
Makatum - AI Text Assistant
A Windows application that provides Claude AI assistance for selected text via hotkey.
Modern glassy UI design.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
import keyboard
import pyperclip
import threading
import os
import time
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Detect Windows theme
def get_windows_theme():
    """Detect Windows dark/light mode"""
    try:
        import winreg
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        winreg.CloseKey(key)
        return "light" if value == 1 else "dark"
    except:
        return "dark"  # Default to dark if detection fails

# Set appearance mode based on Windows system settings
ctk.set_appearance_mode(get_windows_theme())
ctk.set_default_color_theme("blue")

class ChatGPTPopup:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.withdraw()  # Hide the main window
        self.window = None
        self.selected_text = ""
        self.client = None
        self.hotkey = "ctrl+y"  # Default hotkey
        self.is_creating_window = False
        self.current_category = None
        self.sidebar_collapsed = True  # Start collapsed by default
        self.current_tab_frame = None
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        
        # Pre-create the window for instant popup
        self.create_popup()
        self.window.withdraw()  # Hide it initially
        
        # Register hotkey
        keyboard.add_hotkey(self.hotkey, self.trigger_popup)
        
        # Check for pending actions periodically
        self.pending_text = None
        self.check_pending()
        
    def get_selected_text(self):
        """Capture selected text from clipboard"""
        try:
            # Save current clipboard content
            old_clipboard = ""
            try:
                old_clipboard = pyperclip.paste()
            except:
                pass
            
            # Clear clipboard to ensure we get fresh content
            pyperclip.copy("")
            
            # Brief wait for clipboard to clear and keys to be released
            time.sleep(0.1)
            
            # Simulate Ctrl+C using keyboard library with explicit press/release
            keyboard.press('ctrl')
            time.sleep(0.02)
            keyboard.press('c')
            time.sleep(0.02)
            keyboard.release('c')
            keyboard.release('ctrl')
            
            # Wait for clipboard to update
            time.sleep(0.15)
            
            # Get the copied text
            selected_text = pyperclip.paste()
            
            print(f"Debug - Old clipboard: '{old_clipboard[:50] if old_clipboard else 'empty'}'")
            print(f"Debug - New clipboard: '{selected_text[:50] if selected_text else 'empty'}'")
            
            # If nothing was copied, restore old clipboard
            if not selected_text:
                pyperclip.copy(old_clipboard)
                print("Debug - No text was selected")
                return ""
            
            # If clipboard didn't change, it might mean nothing was selected
            if selected_text == old_clipboard:
                print("Debug - Clipboard unchanged, using current clipboard content")
                # Return it anyway in case user wants to work with clipboard text
                return selected_text
            
            return selected_text
        except Exception as e:
            print(f"Error getting selected text: {e}")
            return ""
    
    def check_pending(self):
        """Check if there's pending text to display"""
        if self.pending_text is not None:
            self.selected_text = self.pending_text
            self.pending_text = None
            
            if self.window is None or not self.window.winfo_exists():
                self.create_popup()
            else:
                self.update_popup()
        
        # Schedule next check
        self.root.after(100, self.check_pending)
    
    def trigger_popup(self):
        """Triggered when hotkey is pressed"""
        # Prevent multiple simultaneous triggers
        if self.is_creating_window:
            return
        
        self.is_creating_window = True
        
        # Run text capture in a separate thread8
        def capture_text():
            try:
                # Brief delay to allow the hotkey to be released
                time.sleep(0.15)
                #collapse all function in vs code
                print("Debug - Attempting to capture selected text...")
                
                # Get selected text
                captured = self.get_selected_text()
                
                print(f"Debug - Captured text length: {len(captured)}")
                
                # Update the existing window
                self.selected_text = captured
                
                # Update UI on main thread
                def update_ui():
                    # Clear previous content
                    self.response_display.delete("1.0", "end")
                    
                    # Position window at mouse cursor
                    self.position_window()
                    
                    # Show the pre-created window
                    self.window.deiconify()
                    self.window.lift()
                    self.window.focus_force()
                    
                    # Categorize the text first
                    if captured.strip():
                        self.categorize_and_update(captured)
                    else:
                        self.update_popup()
                
                if self.window and self.window.winfo_exists():
                    self.window.after(0, update_ui)
                    
            finally:
                self.is_creating_window = False
        
        thread = threading.Thread(target=capture_text, daemon=True)
        thread.start()
    
    def position_window(self):
        """Position window below mouse cursor"""
        width = 600
        height = 450
        
        # Get mouse position and place window below it
        x = self.window.winfo_pointerx() - width // 2
        y = self.window.winfo_pointery() + 400  # 10px below cursor
        
        # Keep window on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = max(10, min(x, screen_width - width - 10))
        y = max(10, min(y, screen_height - height - 10))
        
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_popup(self):
        """Create the popup window (called once at startup)"""
        self.window = ctk.CTkToplevel(self.root)
        self.window.title("Makatum - AI Text Assistant")
        
        # Make it frameless and modern
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        
        # Set initial size
        self.window.geometry('600x450+100+100')
        
        # Configure window with blur effect simulation
        self.window.configure(fg_color=("#E8EEF3", "#1a1a1a"))
        
        # Setup UI immediately
        self.setup_ui()
        
        # Enable window dragging
        self.enable_window_drag()
        
        # Handle window close to hide instead of destroy
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
    
    def enable_window_drag(self):
        """Enable dragging the frameless window"""
        self.drag_data = {"x": 0, "y": 0}
        
        def start_drag(event):
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
        
        def do_drag(event):
            x = self.window.winfo_x() + (event.x - self.drag_data["x"])
            y = self.window.winfo_y() + (event.y - self.drag_data["y"])
            self.window.geometry(f"+{x}+{y}")
        
        # Bind to entire window for dragging
        self.window.bind("<Button-1>", start_drag)
        self.window.bind("<B1-Motion>", do_drag)
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup the UI components with modern glassy design"""
        
        # Main container with rounded corners
        main_container = ctk.CTkFrame(
            self.window,
            corner_radius=20,
            fg_color=("white", "#1e1e1e"),
            bg_color="transparent"
        )
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Content area
        content_frame = ctk.CTkFrame(
            main_container,
            fg_color="transparent"
        )
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Minimal close button in top-right corner (created last to be on top)
        self.close_btn = ctk.CTkButton(
            main_container,
            text="×",
            width=20,
            height=20,
            corner_radius=10,
            fg_color="transparent",
            hover_color=("#e81123", "#e81123"),
            text_color=("gray50", "gray60"),
            font=ctk.CTkFont(size=14),
            command=self.close_window,
            border_width=0
        )
        self.close_btn.place(relx=1.0, rely=0.0, x=-5, y=5, anchor="ne")
        self.close_btn.lift()  # Bring to front
        
        # Left sidebar with action buttons (overlays content when expanded)
        self.sidebar = ctk.CTkFrame(
            content_frame,
            width=60,
            corner_radius=20,
            fg_color=("gray90", "#2b2b2b"),
            height=250
        )
        self.sidebar.pack(side=tk.LEFT, padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Category buttons container (no header, just buttons)
        self.category_buttons_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.category_buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Category buttons with icons and full text
        self.category_buttons = {}
        self.categories = [
            ("💻", "Code", "code"),
            ("📧", "E-Mail", "email"),
            ("📝", "Text", "general_text"),
            ("❓", "Frage", "question"),
            ("✨", "Kreativ", "creative")
        ]
        
        for icon, label, category in self.categories:
            btn = ctk.CTkButton(
                self.category_buttons_frame,
                text=icon,  # Start with icon only
                command=lambda c=category: self.switch_category(c),
                corner_radius=10,
                height=45,
                width=50,
                fg_color="transparent",
                hover_color=("gray80", "#3a3a3a"),
                text_color=("gray10", "gray90"),
                anchor="center",
                font=ctk.CTkFont(size=24)
            )
            btn.pack(padx=5, pady=5)
            self.category_buttons[category] = btn
        
        # Right content area
        right_frame = ctk.CTkFrame(
            content_frame,
            corner_radius=15,
            fg_color=("gray95", "#252525")
        )
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tabs container for specialized actions
        self.tabs_container = ctk.CTkFrame(
            right_frame,
            fg_color="transparent"
        )
        self.tabs_container.pack(fill=tk.X, padx=20, pady=(20, 15))
        
        # Response section
        response_label = ctk.CTkLabel(
            right_frame,
            text="AI Response:",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w"
        )
        response_label.pack(padx=20, pady=(0, 5), fill=tk.X)
        
        # Response display
        self.response_display = ctk.CTkTextbox(
            right_frame,
            height=150,
            corner_radius=10,
            fg_color=("white", "#1e1e1e"),
            font=ctk.CTkFont(family="Consolas", size=13),
            wrap="word"
        )
        self.response_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        # Bottom action buttons
        bottom_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        bottom_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        copy_btn = ctk.CTkButton(
            bottom_frame,
            text="📋 Copy",
            command=self.copy_response,
            corner_radius=8,
            height=35,
            width=120,
            fg_color=("#0078d4", "#0078d4"),
            hover_color=("#106ebe", "#106ebe"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        replace_btn = ctk.CTkButton(
            bottom_frame,
            text="⇄ Replace",
            command=self.replace_text,
            corner_radius=8,
            height=35,
            width=120,
            fg_color=("#0078d4", "#0078d4"),
            hover_color=("#106ebe", "#106ebe"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        replace_btn.pack(side=tk.LEFT)
    
    def categorize_text(self, text):
        """Categorize text using Claude Haiku for fast classification"""
        if not self.client or not text.strip():
            return "general_text"
        
        # get the first 300 and last 300 characters to provide context
        
        text_snippet = text[:300] + "\n...\n" + text[-300:] if len(text) > 600 else text
        
        try:
            # Use fast Haiku model for quick categorization
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1000,
                temperature=0.2,
                system="You are a text classifier. Respond with ONLY ONE WORD from these categories: code, email, general_text, question, creative. No explanation.",
                messages=[
                    {"role": "user", "content": f"Categorize this text:\n\n{text_snippet}"}
                ]
            )
            print(text_snippet)
            
            print(f"Debug - Categorization response: '{response.content[0].text.strip()}'")
            
            category = response.content[0].text.strip().lower()
            valid_categories = ["code", "email", "general_text", "question", "creative"]
            
            if category in valid_categories:
                print(f"Debug - Text categorized as: {category}")
                return category
            else:
                print(f"Debug - Invalid category '{category}', defaulting to general_text")
                return "general_text"
                
        except Exception as e:
            print(f"Error categorizing text: {e}")
            return "general_text"
    
    def categorize_and_update(self, text):
        """Categorize text and update UI accordingly"""
        # Show loading in response area
        self.response_display.delete("1.0", "end")
        self.response_display.insert("1.0", "Analyzing text...")
        self.window.update()
        
        # Categorize in background thread to keep UI responsive
        def categorize():
            category = self.categorize_text(text)
            self.window.after(0, lambda: self.apply_category(category))
        
        threading.Thread(target=categorize, daemon=True).start()
    
    def apply_category(self, category):
        """Apply the category and update the UI"""
        self.current_category = category
        print(f"Category applied: {category}")
        self.update_popup()
        self.load_category_tab(category)
        
        # Highlight the active category button
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(
                    fg_color=("#0078d4", "#0078d4"), 
                    text_color="white",
                    hover_color=("#106ebe", "#106ebe")
                )
            else:
                btn.configure(
                    fg_color="transparent", 
                    text_color=("gray10", "gray90"),
                    hover_color=("gray80", "#3a3a3a")
                )
    
    def update_popup(self):
        """Update popup with new selected text"""
        if self.window and self.window.winfo_exists():
            self.response_display.delete("1.0", "end")
            
            # Bring window to front
            self.window.lift()
            self.window.focus_force()
    
    def switch_category(self, category):
        """Manually switch to a different category"""
        self.apply_category(category)
    
    def load_category_tab(self, category):
        """Load specialized actions for the given category"""
        # Clear existing tab content
        if self.current_tab_frame:
            self.current_tab_frame.destroy()
        
        # Create new tab frame
        self.current_tab_frame = ctk.CTkFrame(
            self.tabs_container,
            fg_color="transparent"
        )
        self.current_tab_frame.pack(fill=tk.X)
        
        # Define actions for each category
        category_actions = {
            "code": [
                ("💡 Explain", "Explain what this code does in simple terms:\n\n"),
                ("✨ Improve", "Improve this code for better performance and readability:\n\n"),
                ("📋 Add Docstring", "Add comprehensive docstrings to this code:\n\n"),
                ("🔧 Fix Errors", "Find and fix any errors or bugs in this code:\n\n"),
                ("🧪 Generate Tests", "Generate unit tests for this code:\n\n")
            ],
            "email": [
                ("✉️ Write Email", "Write a professional email based on this:\n\n"),
                ("↩️ Reply", "Write a professional reply to this email:\n\n"),
                ("📝 Summarize", "Summarize this email concisely:\n\n"),
                ("🔄 Rewrite", "Rewrite this email more professionally:\n\n"),
                ("🌍 Translate", "Translate this email to English:\n\n")
            ],
            "general_text": [
                ("🔄 Improve", "Improve this text while maintaining its meaning:\n\n"),
                ("✅ Fix Grammar", "Fix grammar and spelling errors:\n\n"),
                ("📉 Shorten", "Make this text more concise:\n\n"),
                ("📈 Expand", "Expand this text with more details:\n\n"),
                ("🎯 Simplify", "Simplify this text for easier understanding:\n\n")
            ],
            "question": [
                ("💬 Answer", "Answer this question comprehensively:\n\n"),
                ("🔍 Research", "Provide detailed information about:\n\n"),
                ("📚 Explain", "Explain this topic in detail:\n\n"),
                ("💡 Examples", "Provide examples for:\n\n"),
                ("🎓 ELI5", "Explain like I'm 5:\n\n")
            ],
            "creative": [
                ("✍️ Continue", "Continue writing this story:\n\n"),
                ("🎨 Enhance", "Make this more creative and engaging:\n\n"),
                ("🔄 Rewrite", "Rewrite this in a different style:\n\n"),
                ("💭 Brainstorm", "Brainstorm ideas based on:\n\n"),
                ("📖 Story", "Create a story from this:\n\n")
            ]
        }
        
        actions = category_actions.get(category, category_actions["general_text"])
        
        # Create action buttons in a grid
        for i, (label, prompt_prefix) in enumerate(actions):
            btn = ctk.CTkButton(
                self.current_tab_frame,
                text=label,
                command=lambda p=prompt_prefix: self.process_with_prompt(p),
                corner_radius=10,
                height=40,
                fg_color=("#0078d4", "#0078d4"),
                hover_color=("#106ebe", "#106ebe"),
                font=ctk.CTkFont(size=14, weight="bold")
            )
            # Place buttons in a row
            btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    def process_with_prompt(self, prompt_prefix):
        """Process text with a predefined prompt"""
        if not self.client:
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", 
                "Error: Anthropic API key not found. Please set ANTHROPIC_API_KEY in .env file.")
            return
        
        if not self.selected_text.strip():
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", "No text selected. Please select text and try again.")
            return
        
        # Show loading message
        self.response_display.delete("1.0", "end")
        self.response_display.insert("1.0", "Processing...")
        self.window.update()
        
        # Process in background thread
        def process():
            try:
                # Call Claude API
                response = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=2000,
                    temperature=0.7,
                    system="You are a helpful assistant. Provide clear, high-quality responses. Only return the actual result without extra commentary.",
                    messages=[
                        {"role": "user", "content": f"{prompt_prefix}{self.selected_text}"}
                    ]
                )
                
                result = response.content[0].text
                
                # Display response
                self.window.after(0, lambda: self.display_result(result))
                
            except Exception as e:
                self.window.after(0, lambda: self.display_result(f"Error: {str(e)}"))
        
        threading.Thread(target=process, daemon=True).start()
    
    def display_result(self, result):
        """Display the result in the response area"""
        self.response_display.delete("1.0", "end")
        self.response_display.insert("1.0", result)
    
    def process_text(self, action):
        """Process text with Claude based on action"""
        if not self.client:
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", 
                "Error: Anthropic API key not found. Please set ANTHROPIC_API_KEY in .env file.")
            return
        
        if not self.selected_text.strip():
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", "No text selected. Please select text and try again.")
            return
        
        # Show loading message
        self.response_display.delete("1.0", "end")
        self.response_display.insert("1.0", "Processing...")
        self.window.update()
        
        # Define prompts for different actions
        prompts = {
            "improve": f"Improve the following text while maintaining its meaning and tone:\n\n{self.selected_text}",
            "grammar": f"Fix grammar and spelling errors in the following text:\n\n{self.selected_text}",
            "shorten": f"Make the following text more concise while keeping the key points:\n\n{self.selected_text}"
        }
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                temperature=0.7,
                system="You are a helpful writing assistant. Provide clear, concise improvements to text. Only return the actual answer without extra commentary. Only return the one best version.",
                messages=[
                    {"role": "user", "content": prompts.get(action, self.selected_text)}
                ]
            )
            
            result = response.content[0].text
            
            # Display response
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", result)
            
        except Exception as e:
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", f"Error: {str(e)}")
    
    def show_custom_prompt(self):
        """Show dialog for custom prompt"""
        prompt_window = ctk.CTkToplevel(self.window)
        prompt_window.title("Custom Prompt")
        prompt_window.overrideredirect(True)
        prompt_window.attributes('-topmost', True)
        
        width = 500
        height = 300
        x = self.window.winfo_x() + (self.window.winfo_width() - width) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - height) // 2
        prompt_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Main container
        container = ctk.CTkFrame(
            prompt_window,
            corner_radius=20,
            fg_color=("white", "#1e1e1e")
        )
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header = ctk.CTkFrame(
            container,
            corner_radius=15,
            fg_color=("gray85", "#2b2b2b"),
            height=50
        )
        header.pack(fill=tk.X, padx=15, pady=(15, 10))
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="✨ Custom Instruction",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        ).pack(side=tk.LEFT, padx=15)
        
        ctk.CTkButton(
            header,
            text="✕",
            width=35,
            height=35,
            corner_radius=17,
            fg_color=("gray75", "#3a3a3a"),
            hover_color=("#e81123", "#e81123"),
            font=ctk.CTkFont(size=18),
            command=prompt_window.destroy
        ).pack(side=tk.RIGHT, padx=10)
        
        # Content
        content = ctk.CTkFrame(container, fg_color="transparent")
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            content,
            text="Enter your instruction:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(pady=(5, 10), fill=tk.X)
        
        prompt_entry = ctk.CTkTextbox(
            content,
            height=120,
            corner_radius=10,
            fg_color=("white", "#252525"),
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        prompt_entry.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        prompt_entry.focus()
        
        def submit_custom():
            custom_instruction = prompt_entry.get("1.0", "end-1c").strip()
            if custom_instruction:
                prompt_window.destroy()
                self.process_custom_text(custom_instruction)
        
        ctk.CTkButton(
            content,
            text="✓ Submit",
            command=submit_custom,
            corner_radius=10,
            height=40,
            fg_color=("#0078d4", "#0078d4"),
            hover_color=("#106ebe", "#106ebe"),
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack()
    
    def process_custom_text(self, instruction):
        """Process text with custom instruction"""
        if not self.client:
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", 
                "Error: Anthropic API key not found. Please set ANTHROPIC_API_KEY in .env file.")
            return
        
        if not self.selected_text.strip():
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", "No text selected. Please select text and try again.")
            return
        
        # Show loading message
        self.response_display.delete("1.0", "end")
        self.response_display.insert("1.0", "Processing...")
        self.window.update()
        
        try:
            # Call Claude API with custom instruction
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                temperature=0.7,
                system="You are a helpful writing assistant.",
                messages=[
                    {"role": "user", "content": f"{instruction}\n\nText:\n{self.selected_text}"}
                ]
            )
            
            result = response.content[0].text
            
            # Display response
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", result)
            
        except Exception as e:
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", f"Error: {str(e)}")
    
    def copy_response(self):
        """Copy response to clipboard"""
        response = self.response_display.get("1.0", "end-1c").strip()
        if response:
            pyperclip.copy(response)
            # Show brief feedback
            original_text = self.response_display.get("1.0", "end-1c")
            self.response_display.delete("1.0", "end")
            self.response_display.insert("1.0", "✓ Copied to clipboard!\n\n" + original_text)
            self.window.after(1500, lambda: self.response_display.delete("1.0", "1.end"))
    
    def replace_text(self):
        """Replace original text with response"""
        response = self.response_display.get("1.0", "end-1c").strip()
        if response:
            pyperclip.copy(response)
            # Close window
            self.close_window()
            # Small delay then paste
            time.sleep(0.3)
            keyboard.press_and_release('ctrl+v')
    
    def close_window(self):
        """Hide the popup window"""
        if self.window:
            self.window.withdraw()
    
    def run(self):
        """Run the application"""
        print(f"Makatum AI Text Assistant is running...")
        print(f"Press {self.hotkey} to activate popup")
        print("Close the console window to exit")
        
        # Run tkinter main loop
        self.root.mainloop()

if __name__ == "__main__":
    app = ChatGPTPopup()
    app.run()
