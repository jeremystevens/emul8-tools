"""
Console logging utility for ROM Manager.
Provides timestamped, formatted console output functionality.
"""

import datetime


class ConsoleLogger:
    """Utility class for managing console output with timestamps and formatting."""
    
    # Message type mapping with emojis
    MESSAGE_TYPES = {
        "info": "ℹ️",
        "success": "✅", 
        "warning": "⚠️",
        "error": "❌",
        "default": "📝"
    }
    
    @staticmethod
    def append_message(console_widget, message, message_type="info"):
        """
        Add a timestamped, formatted message to a console widget.
        
        Args:
            console_widget: CTkTextbox widget to append to
            message (str): Message text to append
            message_type (str): Type of message (info, success, warning, error, default)
        """
        # Enable editing temporarily
        console_widget.configure(state="normal")
        
        # Get timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Get emoji prefix for message type
        prefix = ConsoleLogger.MESSAGE_TYPES.get(message_type, "📝")
        
        # Format message with timestamp and emoji
        formatted_message = f"[{timestamp}] {prefix} {message}\n"
        console_widget.insert("end", formatted_message)
        
        # Auto-scroll to bottom to show latest message
        console_widget.see("end")
        
        # Disable editing to prevent user modification
        console_widget.configure(state="disabled")
    
    @staticmethod
    def clear_console(console_widget):
        """
        Clear all content from a console widget.
        
        Args:
            console_widget: CTkTextbox widget to clear
        """
        console_widget.configure(state="normal")
        console_widget.delete("1.0", "end")
        console_widget.configure(state="disabled")
    
    @staticmethod
    def add_separator(console_widget, length=50):
        """
        Add a separator line to the console.
        
        Args:
            console_widget: CTkTextbox widget to add separator to
            length (int): Length of the separator line
        """
        ConsoleLogger.append_message(
            console_widget, 
            "─" * length, 
            "default"
        )