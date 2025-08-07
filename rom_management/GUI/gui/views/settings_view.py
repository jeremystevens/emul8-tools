"""
Settings view for ROM Manager.
Provides UI for application configuration and settings.
"""

import customtkinter as ctk
from config import Config
from gui.components.console_box import ConsoleBox


class SettingsView(ctk.CTkFrame):
    """View for application settings and configuration."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the settings view.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)  # Console expandable
        
        # Create UI elements
        self._create_directory_settings()
        self._create_appearance_settings()
        self._create_database_settings()
        self._create_action_buttons()
        self._create_console()
        
        # Store references to key widgets for external access
        self.setup_widget_references()
    
    def _create_directory_settings(self):
        """Create the directory settings section."""
        dirs_frame = ctk.CTkFrame(self, corner_radius=12)
        dirs_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        dirs_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            dirs_frame, 
            text="ROM Directories", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 15), sticky="w")
        
        # Default ROM directory
        ctk.CTkLabel(
            dirs_frame, 
            text="Default ROM Directory:"
        ).grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.default_rom_dir = ctk.CTkEntry(dirs_frame, height=35)
        self.default_rom_dir.insert(0, str(Config.ROM_DIR))
        self.default_rom_dir.grid(
            row=1, column=1, padx=(10, 10), pady=10, sticky="ew"
        )
        
        self.browse_rom_btn = ctk.CTkButton(
            dirs_frame, text="Browse", width=80
        )
        self.browse_rom_btn.grid(row=1, column=2, padx=20, pady=10)
        
        # Duplicates folder
        ctk.CTkLabel(
            dirs_frame, 
            text="Duplicates Folder:"
        ).grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.duplicates_dir = ctk.CTkEntry(dirs_frame, height=35)
        self.duplicates_dir.insert(0, str(Config.DUPLICATES_DIR))
        self.duplicates_dir.grid(
            row=2, column=1, padx=(10, 10), pady=(10, 20), sticky="ew"
        )
        
        self.browse_dup_btn = ctk.CTkButton(
            dirs_frame, text="Browse", width=80
        )
        self.browse_dup_btn.grid(row=2, column=2, padx=20, pady=(10, 20))
    
    def _create_appearance_settings(self):
        """Create the appearance settings section."""
        appearance_frame = ctk.CTkFrame(self, corner_radius=12)
        appearance_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            appearance_frame, 
            text="Appearance", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        ctk.CTkLabel(appearance_frame, text="Theme:").grid(
            row=1, column=0, padx=20, pady=10, sticky="w"
        )
        
        self.theme_combo = ctk.CTkComboBox(
            appearance_frame, 
            values=["Dark", "Light", "System"], 
            width=200
        )
        
        # Set from config with proper title case conversion
        current_theme = Config.THEME.title() if hasattr(Config, 'THEME') else "Dark"
        self.theme_combo.set(current_theme)
        self.theme_combo.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        ctk.CTkLabel(appearance_frame, text="Color Theme:").grid(
            row=2, column=0, padx=20, pady=(10, 20), sticky="w"
        )
        
        self.color_combo = ctk.CTkComboBox(
            appearance_frame, 
            values=["Blue", "Green", "Dark-blue"], 
            width=200
        )
        
        # Set from config with proper title case conversion
        if Config.COLOR_THEME == "dark-blue":
            current_color = "Dark-blue"
        else:
            current_color = Config.COLOR_THEME.title()
        self.color_combo.set(current_color)
        self.color_combo.grid(row=2, column=1, padx=20, pady=(10, 20), sticky="w")
    
    def _create_database_settings(self):
        """Create the database settings section."""
        db_frame = ctk.CTkFrame(self, corner_radius=12)
        db_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            db_frame, 
            text="Database", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        self.auto_backup_var = ctk.BooleanVar(value=True)
        self.auto_backup_cb = ctk.CTkCheckBox(
            db_frame, 
            text="Auto-backup database", 
            variable=self.auto_backup_var
        )
        self.auto_backup_cb.grid(row=1, column=0, padx=20, pady=5, sticky="w")
    
    def _create_action_buttons(self):
        """Create the action buttons section."""
        action_frame = ctk.CTkFrame(self, corner_radius=12)
        action_frame.grid(row=3, column=0, sticky="ew")
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.reset_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Reset to Defaults",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=12,
            fg_color="transparent",
            border_width=2,
            text_color=("gray70", "gray70")
        )
        self.reset_btn.grid(
            row=0, column=0, padx=(20, 10), pady=20, sticky="ew"
        )
        
        self.backup_btn = ctk.CTkButton(
            action_frame,
            text="💾 Backup Database",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=12,
            fg_color="transparent",
            border_width=2
        )
        self.backup_btn.grid(row=0, column=1, padx=10, pady=20, sticky="ew")
        
        self.save_btn = ctk.CTkButton(
            action_frame,
            text="💾 Save Settings",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12
        )
        self.save_btn.grid(row=0, column=2, padx=(10, 20), pady=20, sticky="ew")
    
    def _create_console(self):
        """Create the console output section."""
        self.console_box = ConsoleBox(
            self,
            title="⚙️ Settings Output", 
            height=150
        )
        self.console_box.grid(row=4, column=0, sticky="nsew", pady=(20, 0))
        
        # Add welcome message
        self.console_box.add_welcome_message(
            "🔧",
            "Settings Console",
            "Configuration management ready...\nUpdate paths and preferences as needed."
        )
    
    def setup_widget_references(self):
        """Setup references to key widgets for external access."""
        # Make console easily accessible
        self.console = self.console_box
    
    def get_rom_directory(self):
        """Get the ROM directory path."""
        return self.default_rom_dir.get()
    
    def set_rom_directory(self, path):
        """Set the ROM directory path."""
        self.default_rom_dir.delete(0, "end")
        self.default_rom_dir.insert(0, str(path))
    
    def get_duplicates_directory(self):
        """Get the duplicates directory path."""
        return self.duplicates_dir.get()
    
    def set_duplicates_directory(self, path):
        """Set the duplicates directory path."""
        self.duplicates_dir.delete(0, "end")
        self.duplicates_dir.insert(0, str(path))
    
    def get_theme(self):
        """Get the selected theme."""
        return self.theme_combo.get()
    
    def set_theme(self, theme):
        """Set the theme selection."""
        if theme in ["Dark", "Light", "System"]:
            self.theme_combo.set(theme)
    
    def get_color_theme(self):
        """Get the selected color theme."""
        return self.color_combo.get()
    
    def set_color_theme(self, color_theme):
        """Set the color theme selection."""
        if color_theme in ["Blue", "Green", "Dark-blue"]:
            self.color_combo.set(color_theme)
    
    def get_auto_backup(self):
        """Get the auto backup setting."""
        return self.auto_backup_var.get()
    
    def set_auto_backup(self, enabled):
        """Set the auto backup setting."""
        self.auto_backup_var.set(enabled)
    
    def get_all_settings(self):
        """
        Get all settings from the view.
        
        Returns:
            dict: Dictionary of all settings
        """
        return {
            "rom_directory": self.get_rom_directory(),
            "duplicates_directory": self.get_duplicates_directory(),
            "theme": self.get_theme(),
            "color_theme": self.get_color_theme(),
            "auto_backup": self.get_auto_backup()
        }
    
    def set_all_settings(self, settings):
        """
        Set all settings in the view.
        
        Args:
            settings (dict): Dictionary of settings to apply
        """
        if "rom_directory" in settings:
            self.set_rom_directory(settings["rom_directory"])
        if "duplicates_directory" in settings:
            self.set_duplicates_directory(settings["duplicates_directory"])
        if "theme" in settings:
            self.set_theme(settings["theme"])
        if "color_theme" in settings:
            self.set_color_theme(settings["color_theme"])
        if "auto_backup" in settings:
            self.set_auto_backup(settings["auto_backup"])
    
    def set_browse_rom_callback(self, callback):
        """Set the callback for the browse ROM directory button."""
        self.browse_rom_btn.configure(command=callback)
    
    def set_browse_dup_callback(self, callback):
        """Set the callback for the browse duplicates directory button."""
        self.browse_dup_btn.configure(command=callback)
    
    def set_theme_callback(self, callback):
        """Set the callback for theme changes."""
        self.theme_combo.configure(command=callback)
    
    def set_color_theme_callback(self, callback):
        """Set the callback for color theme changes."""
        self.color_combo.configure(command=callback)
    
    def set_reset_callback(self, callback):
        """Set the callback for the reset button."""
        self.reset_btn.configure(command=callback)
    
    def set_backup_callback(self, callback):
        """Set the callback for the backup button."""
        self.backup_btn.configure(command=callback)
    
    def set_save_callback(self, callback):
        """Set the callback for the save button."""
        self.save_btn.configure(command=callback)
    
    def set_buttons_enabled(self, enabled=True):
        """Enable or disable all action buttons."""
        state = "normal" if enabled else "disabled"
        self.reset_btn.configure(state=state)
        self.backup_btn.configure(state=state)
        self.save_btn.configure(state=state)