"""
Navigation controller for ROM Manager.
Manages view switching and coordinates between components.
"""

from gui.views.scanning_view import ScanningView
from gui.views.organizing_view import OrganizingView
from gui.views.renaming_view import RenamingView
from gui.views.dedup_view import DedupView
from gui.views.settings_view import SettingsView


class NavController:
    """Controller that manages navigation and view switching."""
    
    def __init__(self, main_window):
        """
        Initialize the navigation controller.
        
        Args:
            main_window: MainWindow instance to control
        """
        self.main_window = main_window
        self.current_view = None
        self.current_view_id = None
        
        # Map view IDs to view classes and titles
        self.view_config = {
            "scan": {
                "class": ScanningView,
                "title": "Scan & Index ROMs",
                "status": "Ready to scan ROMs"
            },
            "organize": {
                "class": OrganizingView,
                "title": "Organize ROMs", 
                "status": "Ready to organize ROMs"
            },
            "rename": {
                "class": RenamingView,
                "title": "Rename ROMs",
                "status": "Ready to rename ROMs"
            },
            "dedup": {
                "class": DedupView,
                "title": "Deduplicate ROMs",
                "status": "Ready to deduplicate ROMs"
            },
            "settings": {
                "class": SettingsView,
                "title": "Settings",
                "status": "Configure application settings"
            }
        }
        
        # Map view IDs to sidebar button indices
        self.view_to_button_index = {
            "scan": 0,
            "organize": 1, 
            "rename": 2,
            "dedup": 3,
            "settings": 4
        }
    
    def navigate_to(self, view_id):
        """
        Navigate to a specific view.
        
        Args:
            view_id (str): ID of the view to navigate to
        """
        print(f"NavController.navigate_to called with: {view_id}")
        
        if view_id not in self.view_config:
            print(f"Warning: Unknown view ID '{view_id}'")
            return
        
        # Don't recreate the same view
        if self.current_view_id == view_id:
            print(f"Already on view {view_id}, skipping")
            return
        
        print(f"Switching from {self.current_view_id} to {view_id}")
        
        # Clear current view
        self._clear_current_view()
        
        # Get view configuration
        config = self.view_config[view_id]
        
        # Update header and status
        self.main_window.header.set_title(config["title"])
        self.main_window.set_status(config["status"])
        
        # Update sidebar active button
        button_index = self.view_to_button_index[view_id]
        self.main_window.sidebar.set_active_button(button_index)
        
        # Create and display new view
        self._create_and_display_view(view_id, config)
        
        # Update current view tracking
        self.current_view_id = view_id
        print(f"Successfully switched to {view_id}")
    
    def _clear_current_view(self):
        """Clear the current view from the content frame."""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
    
    def _create_and_display_view(self, view_id, config):
        """
        Create and display a view.
        
        Args:
            view_id (str): ID of the view
            config (dict): View configuration
        """
        # Get the content frame from main window
        content_frame = self.main_window.get_content_frame()
        
        # Create view instance
        view_class = config["class"]
        self.current_view = view_class(content_frame)
        
        # Display view with proper layout
        self.current_view.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        
        # Setup view-specific callbacks
        self._setup_view_callbacks(view_id, self.current_view)
    
    def _setup_view_callbacks(self, view_id, view):
        """
        Setup callbacks for a specific view.
        
        Args:
            view_id (str): ID of the view
            view: View instance
        """
        # For now, we'll set up basic placeholder callbacks
        # These will be replaced with proper controller methods in step 5
        
        if view_id == "scan":
            # view.set_browse_callback(self._handle_browse_directory)
            # view.set_scan_callback(self._handle_start_scan)
            pass
        
        elif view_id == "organize":
            # view.set_preview_callback(self._handle_preview_organization)
            # view.set_organize_callback(self._handle_organize_roms)
            pass
        
        elif view_id == "rename":
            # view.set_preview_callback(self._handle_preview_renames)
            # view.set_rename_callback(self._handle_apply_renames)
            pass
        
        elif view_id == "dedup":
            # view.set_scan_callback(self._handle_scan_duplicates)
            # view.set_remove_callback(self._handle_remove_duplicates)
            pass
        
        elif view_id == "settings":
            # Import here to avoid circular imports
            from gui.rom_manager_gui import ROMManagerGUI
            
            # For settings, we need to connect to the theme methods
            # This is a temporary bridge until step 5
            if hasattr(self.main_window, '_rom_manager_gui'):
                rom_gui = self.main_window._rom_manager_gui
                view.set_theme_callback(rom_gui.change_appearance_mode_event)
                view.set_color_theme_callback(rom_gui.change_color_theme_event)
                view.set_save_callback(rom_gui.save_settings)
            
            # Placeholder for other settings callbacks
            # view.set_browse_rom_callback(self._handle_browse_rom_directory)
            # view.set_browse_dup_callback(self._handle_browse_dup_directory)
            # view.set_reset_callback(self._handle_reset_settings)
            # view.set_backup_callback(self._handle_backup_database)
    
    def get_current_view(self):
        """
        Get the current view instance.
        
        Returns:
            Current view instance or None
        """
        return self.current_view
    
    def get_current_view_id(self):
        """
        Get the current view ID.
        
        Returns:
            str: Current view ID or None
        """
        return self.current_view_id
    
    def refresh_current_view(self):
        """Refresh the current view by recreating it."""
        if self.current_view_id:
            current_id = self.current_view_id
            self.current_view_id = None  # Force recreation
            self.navigate_to(current_id)