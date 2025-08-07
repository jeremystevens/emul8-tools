"""
Sidebar navigation component for ROM Manager.
Provides navigation buttons and emits navigation events.
"""

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    """Sidebar component with navigation buttons and branding."""
    
    def __init__(self, parent, on_navigation=None, **kwargs):
        """
        Initialize the sidebar component.
        
        Args:
            parent: Parent widget
            on_navigation: Callback function for navigation events (can be set later)
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(parent, width=280, corner_radius=0, **kwargs)
        
        # Store navigation callback (can be None initially)
        self.on_navigation = on_navigation
        
        # Configure grid layout
        self.grid_rowconfigure(7, weight=1)  # Empty space for spacing
        
        # Create UI elements
        self._create_logo()
        self._create_navigation_buttons()
        self._create_version_label()
        
        # Track active button index
        self.active_button_index = 0
        self._update_button_states()
    
    def _create_logo(self):
        """Create the logo/title section."""
        self.logo_label = ctk.CTkLabel(
            self, 
            text="ROM Manager", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("#1f6aa5", "#4a9eff")
        )
        self.logo_label.grid(row=0, column=0, padx=30, pady=(30, 40))
    
    def _create_navigation_buttons(self):
        """Create the navigation buttons."""
        # Navigation button configuration
        nav_buttons_config = [
            ("🔍", "Scan ROMs", "scan"),
            ("📁", "Organize", "organize"),
            ("✏️", "Rename", "rename"),
            ("🗂️", "Deduplicate", "dedup"),
            ("⚙️", "Settings", "settings")
        ]
        
        self.nav_buttons = []
        for i, (icon, text, nav_id) in enumerate(nav_buttons_config):
            btn = ctk.CTkButton(
                self,
                text=f"{icon}  {text}",
                font=ctk.CTkFont(size=16, weight="normal"),
                height=50,
                anchor="w",
                command=lambda nav_id=nav_id, index=i: self._handle_navigation(nav_id, index),
                corner_radius=12,
                hover_color=("#2b2b2b", "#404040"),
                text_color=("gray70", "gray90"),
                fg_color="transparent"
            )
            btn.grid(row=i+1, column=0, padx=20, pady=8, sticky="ew")
            self.nav_buttons.append(btn)
    
    def _create_version_label(self):
        """Create the version information label."""
        version_label = ctk.CTkLabel(
            self,
            text="v1.0.0",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        )
        version_label.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="s")
    
    def _handle_navigation(self, nav_id, button_index):
        """
        Handle navigation button clicks.
        
        Args:
            nav_id (str): Navigation identifier
            button_index (int): Index of the clicked button
        """
        print(f"Sidebar._handle_navigation called with {nav_id}, callback is: {self.on_navigation}")
        
        # Update active button
        self.set_active_button(button_index)
        
        # Emit navigation event if callback is provided
        if self.on_navigation:
            print(f"Calling callback: {self.on_navigation}")
            self.on_navigation(nav_id)
        else:
            print(f"Navigation requested: {nav_id} (no callback set)")
    
    def set_navigation_callback(self, callback):
        """
        Set or update the navigation callback.
        
        Args:
            callback: Function to call when navigation is requested
        """
        self.on_navigation = callback
        print(f"Sidebar callback set to: {callback}")
    
    def set_active_button(self, button_index):
        """
        Set the active navigation button.
        
        Args:
            button_index (int): Index of the button to make active
        """
        self.active_button_index = button_index
        self._update_button_states()
    
    def _update_button_states(self):
        """Update the visual state of navigation buttons."""
        for i, btn in enumerate(self.nav_buttons):
            if i == self.active_button_index:
                btn.configure(
                    fg_color=("#1f6aa5", "#4a9eff"), 
                    text_color="white"
                )
            else:
                btn.configure(
                    fg_color="transparent", 
                    text_color=("gray70", "gray90")
                )
    
    def get_active_button_index(self):
        """
        Get the currently active button index.
        
        Returns:
            int: Index of the active button
        """
        return self.active_button_index