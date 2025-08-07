"""
Reusable console text box component for ROM Manager.
Provides a styled, consistent console widget across all views.
"""

import customtkinter as ctk
from utils.console_logger import ConsoleLogger


class ConsoleBox(ctk.CTkFrame):
    """
    A reusable console component that provides a styled textbox 
    with built-in logging capabilities.
    """
    
    def __init__(self, parent, title="Console Output", height=200, **kwargs):
        """
        Initialize the console box component.
        
        Args:
            parent: Parent widget
            title (str): Title displayed above the console
            height (int): Height of the console textbox
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(parent, corner_radius=12, **kwargs)
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create title label
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        # Create console textbox with modern styling
        self.console = ctk.CTkTextbox(
            self,
            height=height,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=("gray95", "gray10"),
            text_color=("gray20", "gray80"),
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        self.console.grid(row=1, column=0, padx=20, pady=(5, 20), sticky="nsew")
        
        # Set initial state to disabled to prevent user editing
        self.console.configure(state="disabled")
    
    def add_message(self, message, message_type="info"):
        """
        Add a timestamped message to the console.
        
        Args:
            message (str): Message to add
            message_type (str): Type of message (info, success, warning, error)
        """
        ConsoleLogger.append_message(self.console, message, message_type)
    
    def clear(self):
        """Clear all content from the console."""
        ConsoleLogger.clear_console(self.console)
    
    def add_separator(self, length=50):
        """Add a separator line to the console."""
        ConsoleLogger.add_separator(self.console, length)
    
    def add_welcome_message(self, emoji, title, description):
        """
        Add a standardized welcome message to the console.
        
        Args:
            emoji (str): Emoji for the title
            title (str): Title text
            description (str): Description text
        """
        self.console.configure(state="normal")
        self.console.insert("0.0", f"{emoji} {title}\n")
        self.console.insert("end", "─" * 50 + "\n")
        self.console.insert("end", f"{description}\n\n")
        self.console.configure(state="disabled")
    
    def get_textbox(self):
        """
        Get the underlying CTkTextbox widget for advanced operations.
        
        Returns:
            CTkTextbox: The console textbox widget
        """
        return self.console