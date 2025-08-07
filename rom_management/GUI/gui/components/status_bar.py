"""
Status bar component for ROM Manager.
Displays application status and provides status updates.
"""

import customtkinter as ctk


class StatusBar(ctk.CTkFrame):
    """Status bar component that displays application status information."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the status bar component.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(
            parent, 
            height=40, 
            corner_radius=0,
            **kwargs
        )
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        
        # Create status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=8, sticky="w")
    
    def set_status(self, text):
        """
        Set the status bar text.
        
        Args:
            text (str): Status text to display
        """
        self.status_label.configure(text=text)
    
    def get_status(self):
        """
        Get the current status text.
        
        Returns:
            str: Current status text
        """
        return self.status_label.cget("text")
    
    def set_status_color(self, color):
        """
        Set the status text color.
        
        Args:
            color (str or tuple): Color for the status text
        """
        self.status_label.configure(text_color=color)
    
    def clear_status(self):
        """Clear the status text."""
        self.set_status("Ready")