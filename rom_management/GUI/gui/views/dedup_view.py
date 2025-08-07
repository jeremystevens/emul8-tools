"""
Deduplication view for ROM Manager.
Provides UI for ROM deduplication operations.
"""

import customtkinter as ctk
from gui.components.console_box import ConsoleBox


class DedupView(ctk.CTkFrame):
    """View for ROM deduplication functionality."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the deduplication view.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Console expandable
        
        # Create UI elements
        self._create_detection_methods()
        self._create_handling_options()
        self._create_action_buttons()
        self._create_console()
        
        # Store references to key widgets for external access
        self.setup_widget_references()
    
    def _create_detection_methods(self):
        """Create the detection methods section."""
        method_frame = ctk.CTkFrame(self, corner_radius=12)
        method_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            method_frame, 
            text="Detection Method", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        # Create detection method variable
        self.detection_method = ctk.StringVar(value="hash")
        
        # Create radio buttons for detection methods
        methods = [
            ("File hash (MD5/SHA1) - Most accurate", "hash"),
            ("File size and name comparison", "size_name"),
            ("Name similarity only", "name_only")
        ]
        
        self.method_buttons = []
        for i, (text, value) in enumerate(methods):
            rb = ctk.CTkRadioButton(
                method_frame, 
                text=text, 
                variable=self.detection_method, 
                value=value
            )
            rb.grid(row=i+1, column=0, padx=20, pady=5, sticky="w")
            self.method_buttons.append(rb)
    
    def _create_handling_options(self):
        """Create the duplicate handling options section."""
        options_frame = ctk.CTkFrame(self, corner_radius=12)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            options_frame, 
            text="Duplicate Handling", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        # Create handling option variables
        self.move_to_folder_var = ctk.BooleanVar(value=True)
        self.keep_best_version_var = ctk.BooleanVar(value=True)
        
        # Create checkboxes
        self.move_folder_cb = ctk.CTkCheckBox(
            options_frame, 
            text="Move duplicates to separate folder", 
            variable=self.move_to_folder_var
        )
        self.move_folder_cb.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.keep_best_cb = ctk.CTkCheckBox(
            options_frame, 
            text="Keep best version (prefer no-intro/redump)", 
            variable=self.keep_best_version_var
        )
        self.keep_best_cb.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="w")
    
    def _create_action_buttons(self):
        """Create the action buttons section."""
        action_frame = ctk.CTkFrame(self, corner_radius=12)
        action_frame.grid(row=2, column=0, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.scan_dupes_btn = ctk.CTkButton(
            action_frame,
            text="🔍 Scan for Duplicates",
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=12,
            fg_color="transparent",
            border_width=2
        )
        self.scan_dupes_btn.grid(
            row=0, column=0, padx=(20, 10), pady=20, sticky="ew"
        )
        
        self.remove_dupes_btn = ctk.CTkButton(
            action_frame,
            text="🗂️ Remove Duplicates",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12
        )
        self.remove_dupes_btn.grid(
            row=0, column=1, padx=(10, 20), pady=20, sticky="ew"
        )
    
    def _create_console(self):
        """Create the console output section."""
        self.console_box = ConsoleBox(
            self,
            title="🔍 Deduplication Output",
            height=200
        )
        self.console_box.grid(row=3, column=0, sticky="nsew", pady=(20, 0))
        
        # Add welcome message
        self.console_box.add_welcome_message(
            "🗂️",
            "Duplicate Finder Console",
            "Ready to find duplicate ROMs...\nConfigure detection method and scan for duplicates."
        )
    
    def setup_widget_references(self):
        """Setup references to key widgets for external access."""
        # Make console easily accessible
        self.console = self.console_box
    
    def get_detection_method(self):
        """Get the selected detection method."""
        return self.detection_method.get()
    
    def set_detection_method(self, method):
        """Set the detection method."""
        if method in ["hash", "size_name", "name_only"]:
            self.detection_method.set(method)
    
    def get_handling_options(self):
        """
        Get the duplicate handling options.
        
        Returns:
            dict: Dictionary of handling options
        """
        return {
            "move_to_folder": self.move_to_folder_var.get(),
            "keep_best_version": self.keep_best_version_var.get()
        }
    
    def set_handling_options(self, options):
        """
        Set the duplicate handling options.
        
        Args:
            options (dict): Dictionary of handling options
        """
        if "move_to_folder" in options:
            self.move_to_folder_var.set(options["move_to_folder"])
        if "keep_best_version" in options:
            self.keep_best_version_var.set(options["keep_best_version"])
    
    def get_dedup_settings(self):
        """
        Get all deduplication settings.
        
        Returns:
            dict: Dictionary of deduplication settings
        """
        return {
            "detection_method": self.get_detection_method(),
            **self.get_handling_options()
        }
    
    def set_dedup_settings(self, settings):
        """
        Set deduplication settings.
        
        Args:
            settings (dict): Dictionary of deduplication settings
        """
        if "detection_method" in settings:
            self.set_detection_method(settings["detection_method"])
        
        handling_opts = {k: v for k, v in settings.items() 
                        if k in ["move_to_folder", "keep_best_version"]}
        if handling_opts:
            self.set_handling_options(handling_opts)
    
    def set_scan_button_enabled(self, enabled=True):
        """Enable or disable the scan duplicates button."""
        state = "normal" if enabled else "disabled"
        self.scan_dupes_btn.configure(state=state)
    
    def set_remove_button_enabled(self, enabled=True):
        """Enable or disable the remove duplicates button."""
        state = "normal" if enabled else "disabled"
        self.remove_dupes_btn.configure(state=state)
    
    def set_scan_callback(self, callback):
        """Set the callback for the scan duplicates button."""
        self.scan_dupes_btn.configure(command=callback)
    
    def set_remove_callback(self, callback):
        """Set the callback for the remove duplicates button."""
        self.remove_dupes_btn.configure(command=callback)