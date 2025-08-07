"""
Organizing view for ROM Manager.
Provides UI for ROM organization operations.
"""

import customtkinter as ctk
from gui.components.console_box import ConsoleBox


class OrganizingView(ctk.CTkFrame):
    """View for ROM organization functionality."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the organizing view.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Console expandable
        
        # Create UI elements
        self._create_organization_options()
        self._create_action_buttons()
        self._create_console()
        
        # Store references to key widgets for external access
        self.setup_widget_references()
    
    def _create_organization_options(self):
        """Create the organization options section."""
        options_frame = ctk.CTkFrame(self, corner_radius=12)
        options_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            options_frame, 
            text="Organization Method", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        # Create organization method variable
        self.org_method = ctk.StringVar(value="alphabetical")
        
        # Create radio buttons
        self.alphabetical_rb = ctk.CTkRadioButton(
            options_frame, 
            text="Alphabetical (A-Z)", 
            variable=self.org_method, 
            value="alphabetical"
        )
        self.alphabetical_rb.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.genre_rb = ctk.CTkRadioButton(
            options_frame, 
            text="By Genre", 
            variable=self.org_method, 
            value="genre"
        )
        self.genre_rb.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.console_rb = ctk.CTkRadioButton(
            options_frame, 
            text="By Console/Platform", 
            variable=self.org_method, 
            value="console"
        )
        self.console_rb.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="w")
    
    def _create_action_buttons(self):
        """Create the action buttons section."""
        action_frame = ctk.CTkFrame(self, corner_radius=12)
        action_frame.grid(row=1, column=0, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.preview_btn = ctk.CTkButton(
            action_frame,
            text="📋 Preview Changes",
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=12,
            fg_color="transparent",
            border_width=2
        )
        self.preview_btn.grid(
            row=0, column=0, padx=(20, 10), pady=20, sticky="ew"
        )
        
        self.organize_btn = ctk.CTkButton(
            action_frame,
            text="📁 Organize ROMs",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12
        )
        self.organize_btn.grid(
            row=0, column=1, padx=(10, 20), pady=20, sticky="ew"
        )
    
    def _create_console(self):
        """Create the console output section."""
        self.console_box = ConsoleBox(
            self,
            title="📁 Organization Output",
            height=200
        )
        self.console_box.grid(row=2, column=0, sticky="nsew", pady=(20, 0))
        
        # Add welcome message
        self.console_box.add_welcome_message(
            "📂",
            "ROM Organizer Console",
            "Ready to organize ROM collection...\nChoose organization method and preview changes first."
        )
    
    def setup_widget_references(self):
        """Setup references to key widgets for external access."""
        # Make console easily accessible
        self.console = self.console_box
    
    def get_organization_method(self):
        """Get the selected organization method."""
        return self.org_method.get()
    
    def set_organization_method(self, method):
        """Set the organization method."""
        if method in ["alphabetical", "genre", "console"]:
            self.org_method.set(method)
    
    def set_preview_button_enabled(self, enabled=True):
        """Enable or disable the preview button."""
        state = "normal" if enabled else "disabled"
        self.preview_btn.configure(state=state)
    
    def set_organize_button_enabled(self, enabled=True):
        """Enable or disable the organize button."""
        state = "normal" if enabled else "disabled"
        self.organize_btn.configure(state=state)
    
    def set_preview_callback(self, callback):
        """Set the callback for the preview button."""
        self.preview_btn.configure(command=callback)
    
    def set_organize_callback(self, callback):
        """Set the callback for the organize button."""
        self.organize_btn.configure(command=callback)