"""
Scanning view for ROM Manager.
Provides UI for ROM scanning and indexing operations.
"""

import customtkinter as ctk
from gui.components.console_box import ConsoleBox


class ScanningView(ctk.CTkFrame):
    """View for ROM scanning and indexing functionality."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the scanning view.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Console expandable
        
        # Create UI elements
        self._create_directory_selection()
        self._create_scan_options()
        self._create_action_buttons()
        self._create_console()
        
        # Store references to key widgets for external access
        self.setup_widget_references()
    
    def _create_directory_selection(self):
        """Create the directory selection section."""
        dir_frame = ctk.CTkFrame(self, corner_radius=12)
        dir_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        dir_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            dir_frame, 
            text="ROM Directory:", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.dir_entry = ctk.CTkEntry(
            dir_frame, height=40, font=ctk.CTkFont(size=14)
        )
        self.dir_entry.grid(
            row=0, column=1, padx=(0, 10), pady=20, sticky="ew"
        )
        
        self.browse_btn = ctk.CTkButton(
            dir_frame, 
            text="Browse", 
            width=100, 
            height=40,
            corner_radius=8
        )
        self.browse_btn.grid(row=0, column=2, padx=20, pady=20)
    
    def _create_scan_options(self):
        """Create the scan options section."""
        options_frame = ctk.CTkFrame(self, corner_radius=12)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            options_frame, 
            text="Scan Options", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Create option variables
        self.recursive_var = ctk.BooleanVar(value=True)
        self.metadata_var = ctk.BooleanVar(value=True)
        self.generate_thumbnails_var = ctk.BooleanVar(value=False)
        
        # Create checkboxes
        self.recursive_cb = ctk.CTkCheckBox(
            options_frame, 
            text="Scan subdirectories recursively", 
            variable=self.recursive_var
        )
        self.recursive_cb.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.metadata_cb = ctk.CTkCheckBox(
            options_frame, 
            text="Extract metadata", 
            variable=self.metadata_var
        )
        self.metadata_cb.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.thumbnails_cb = ctk.CTkCheckBox(
            options_frame, 
            text="Generate thumbnails", 
            variable=self.generate_thumbnails_var
        )
        self.thumbnails_cb.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="w")
    
    def _create_action_buttons(self):
        """Create the action buttons section."""
        action_frame = ctk.CTkFrame(self, corner_radius=12)
        action_frame.grid(row=2, column=0, sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)
        
        self.scan_btn = ctk.CTkButton(
            action_frame,
            text="🔍 Start Scan",
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=12
        )
        self.scan_btn.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Progress bar (hidden by default)
        self.scan_progress = ctk.CTkProgressBar(action_frame)
        self.scan_progress.grid(
            row=1, column=0, padx=20, pady=(0, 20), sticky="ew"
        )
        self.scan_progress.grid_remove()  # Hide initially
    
    def _create_console(self):
        """Create the console output section."""
        self.console_box = ConsoleBox(
            self,
            title="📋 Scan Output",
            height=200
        )
        self.console_box.grid(row=3, column=0, sticky="nsew", pady=(20, 0))
        
        # Add welcome message
        self.console_box.add_welcome_message(
            "🚀",
            "ROM Scanner Console", 
            "Ready to scan ROM collection...\nSelect a directory and configure options to begin."
        )
    
    def setup_widget_references(self):
        """Setup references to key widgets for external access."""
        # Make console easily accessible
        self.console = self.console_box
    
    def get_directory_path(self):
        """Get the selected directory path."""
        return self.dir_entry.get()
    
    def set_directory_path(self, path):
        """Set the directory path."""
        self.dir_entry.delete(0, "end")
        self.dir_entry.insert(0, path)
    
    def get_scan_options(self):
        """
        Get the current scan options.
        
        Returns:
            dict: Dictionary of scan options
        """
        return {
            "recursive": self.recursive_var.get(),
            "metadata": self.metadata_var.get(),
            "thumbnails": self.generate_thumbnails_var.get()
        }
    
    def set_scan_options(self, options):
        """
        Set the scan options.
        
        Args:
            options (dict): Dictionary of scan options
        """
        if "recursive" in options:
            self.recursive_var.set(options["recursive"])
        if "metadata" in options:
            self.metadata_var.set(options["metadata"])
        if "thumbnails" in options:
            self.generate_thumbnails_var.set(options["thumbnails"])
    
    def show_progress(self, show=True):
        """Show or hide the progress bar."""
        if show:
            self.scan_progress.grid()
        else:
            self.scan_progress.grid_remove()
    
    def set_progress(self, value):
        """Set the progress bar value (0.0 to 1.0)."""
        self.scan_progress.set(value)
    
    def set_scan_button_enabled(self, enabled=True):
        """Enable or disable the scan button."""
        state = "normal" if enabled else "disabled"
        self.scan_btn.configure(state=state)
    
    def set_browse_callback(self, callback):
        """Set the callback for the browse button."""
        self.browse_btn.configure(command=callback)
    
    def set_scan_callback(self, callback):
        """Set the callback for the scan button."""
        self.scan_btn.configure(command=callback)