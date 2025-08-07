"""
Renaming view for ROM Manager.
Provides UI for ROM renaming operations.
"""

import customtkinter as ctk
from gui.components.console_box import ConsoleBox


class RenamingView(ctk.CTkFrame):
    """View for ROM renaming functionality."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the renaming view.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Console expandable
        
        # Create UI elements
        self._create_naming_conventions()
        self._create_action_buttons()
        self._create_console()
        
        # Store references to key widgets for external access
        self.setup_widget_references()
    
    def _create_naming_conventions(self):
        """Create the naming conventions section."""
        conventions_frame = ctk.CTkFrame(self, corner_radius=12)
        conventions_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            conventions_frame, 
            text="Naming Convention", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        # Create naming convention variable
        self.naming_convention = ctk.StringVar(value="no_tags")
        
        # Create radio buttons for naming conventions
        conventions = [
            ("Remove region/language tags", "no_tags"),
            ("Standard format: Game Name (Region)", "standard"),
            ("Custom format", "custom")
        ]
        
        self.convention_buttons = []
        for i, (text, value) in enumerate(conventions):
            rb = ctk.CTkRadioButton(
                conventions_frame, 
                text=text, 
                variable=self.naming_convention, 
                value=value
            )
            rb.grid(row=i+1, column=0, padx=20, pady=5, sticky="w")
            self.convention_buttons.append(rb)
        
        # Custom format entry
        self.custom_format_entry = ctk.CTkEntry(
            conventions_frame, 
            placeholder_text="e.g., {name} [{region}] ({year})",
            height=35
        )
        self.custom_format_entry.grid(
            row=4, column=0, padx=40, pady=(5, 20), sticky="ew"
        )
    
    def _create_action_buttons(self):
        """Create the action buttons section."""
        action_frame = ctk.CTkFrame(self, corner_radius=12)
        action_frame.grid(row=1, column=0, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.preview_btn = ctk.CTkButton(
            action_frame,
            text="👀 Preview Renames",
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=12,
            fg_color="transparent",
            border_width=2
        )
        self.preview_btn.grid(
            row=0, column=0, padx=(20, 10), pady=20, sticky="ew"
        )
        
        self.rename_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Apply Renames",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12
        )
        self.rename_btn.grid(
            row=0, column=1, padx=(10, 20), pady=20, sticky="ew"
        )
    
    def _create_console(self):
        """Create the console output section."""
        self.console_box = ConsoleBox(
            self,
            title="✏️ Rename Output",
            height=200
        )
        self.console_box.grid(row=2, column=0, sticky="nsew", pady=(20, 0))
        
        # Add welcome message
        self.console_box.add_welcome_message(
            "🏷️",
            "ROM Renamer Console",
            "Ready to rename ROM files...\nSelect naming convention and preview changes."
        )
    
    def setup_widget_references(self):
        """Setup references to key widgets for external access."""
        # Make console easily accessible
        self.console = self.console_box
    
    def get_naming_convention(self):
        """Get the selected naming convention."""
        return self.naming_convention.get()
    
    def set_naming_convention(self, convention):
        """Set the naming convention."""
        if convention in ["no_tags", "standard", "custom"]:
            self.naming_convention.set(convention)
    
    def get_custom_format(self):
        """Get the custom format string."""
        return self.custom_format_entry.get()
    
    def set_custom_format(self, format_string):
        """Set the custom format string."""
        self.custom_format_entry.delete(0, "end")
        self.custom_format_entry.insert(0, format_string)
    
    def get_naming_settings(self):
        """
        Get all naming settings.
        
        Returns:
            dict: Dictionary of naming settings
        """
        return {
            "convention": self.get_naming_convention(),
            "custom_format": self.get_custom_format()
        }
    
    def set_naming_settings(self, settings):
        """
        Set naming settings.
        
        Args:
            settings (dict): Dictionary of naming settings
        """
        if "convention" in settings:
            self.set_naming_convention(settings["convention"])
        if "custom_format" in settings:
            self.set_custom_format(settings["custom_format"])
    
    def set_preview_button_enabled(self, enabled=True):
        """Enable or disable the preview button."""
        state = "normal" if enabled else "disabled"
        self.preview_btn.configure(state=state)
    
    def set_rename_button_enabled(self, enabled=True):
        """Enable or disable the rename button."""
        state = "normal" if enabled else "disabled"
        self.rename_btn.configure(state=state)
    
    def set_preview_callback(self, callback):
        """Set the callback for the preview button."""
        self.preview_btn.configure(command=callback)
    
    def set_rename_callback(self, callback):
        """Set the callback for the rename button."""
        self.rename_btn.configure(command=callback)