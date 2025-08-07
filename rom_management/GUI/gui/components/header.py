"""
Header component for ROM Manager.
Displays the current view title and provides a consistent header area.
"""

import customtkinter as ctk


class Header(ctk.CTkFrame):
    """Header component that displays the current view title."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the header component.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(
            parent, 
            height=80, 
            corner_radius=0, 
            fg_color="transparent",
            **kwargs
        )
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        
        # Create title label
        self.title_label = ctk.CTkLabel(
            self,
            text="ROM Collection Manager",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.title_label.grid(row=0, column=0, sticky="w", pady=10)
    
    def set_title(self, title):
        """
        Set the header title text.
        
        Args:
            title (str): Title text to display
        """
        self.title_label.configure(text=title)
    
    def get_title(self):
        """
        Get the current header title text.
        
        Returns:
            str: Current title text
        """
        return self.title_label.cget("text")