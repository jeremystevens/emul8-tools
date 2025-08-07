"""
Main window for ROM Manager.
Provides the main application shell using modular components.
"""

import customtkinter as ctk
from config import Config
from gui.components.sidebar import Sidebar
from gui.components.header import Header
from gui.components.status_bar import StatusBar


class MainWindow:
    """Main application window that combines all UI components."""
    
    def __init__(self):
        """Initialize the main window."""
        # Create root window
        self.root = ctk.CTk()
        self.root.title("ROM Collection Manager")
        
        # Load window size from config
        window_size = getattr(Config, 'WINDOW_SIZE', "1400x900")
        self.root.geometry(window_size)
        self.root.minsize(1200, 800)
        
        # Configure grid layout for main areas
        self.root.grid_columnconfigure(1, weight=1)  # Main content area
        self.root.grid_rowconfigure(0, weight=1)     # Content row
        
        # Navigation controller will be set later
        self.nav_controller = None
        
        # Create UI components
        self._create_components()
        
        # Setup initial state
        self._setup_initial_state()
    
    def set_nav_controller(self, nav_controller):
        """
        Set the navigation controller and setup navigation callback.
        
        Args:
            nav_controller: NavController instance
        """
        self.nav_controller = nav_controller
        # Now that we have a nav controller, setup the sidebar callback
        self._setup_navigation_callback()
        print(f"Nav controller set, callback setup: {self.sidebar.on_navigation is not None}")
    
    def _create_components(self):
        """Create and layout the main UI components."""
        # Create sidebar WITHOUT navigation callback initially
        self.sidebar = Sidebar(self.root)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        # Create header
        self.header = Header(self.root)
        self.header.grid(
            row=0, column=1, sticky="ew", padx=30, pady=(30, 0)
        )
        
        # Create main content area
        self.content_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.content_frame.grid(
            row=0, column=1, sticky="nsew", padx=30, pady=(100, 30)
        )
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Create status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=1, column=1, sticky="ew")
    
    def _setup_navigation_callback(self):
        """Setup the navigation callback after nav controller is set."""
        if self.sidebar:
            self.sidebar.set_navigation_callback(self._handle_navigation)
            print(f"Callback set to: {self._handle_navigation}")
    
    def _setup_initial_state(self):
        """Setup the initial application state."""
        self.set_status("Ready")
        self.header.set_title("ROM Collection Manager")
    
    def _handle_navigation(self, nav_id):
        """
        Handle navigation events from the sidebar.
        
        Args:
            nav_id (str): Navigation identifier (scan, organize, rename, dedup, settings)
        """
        print(f"MainWindow._handle_navigation called with: {nav_id}")
        if self.nav_controller:
            print(f"Calling nav_controller.navigate_to({nav_id})")
            self.nav_controller.navigate_to(nav_id)
        else:
            # Fallback if nav controller not set yet
            print(f"Navigation requested: {nav_id} (no controller)")
    
    def switch_view(self, view_name):
        """
        Switch to a different view via nav controller.
        
        Args:
            view_name (str): Name of the view to switch to
        """
        if self.nav_controller:
            self.nav_controller.navigate_to(view_name)
    
    def set_status(self, text):
        """
        Set the status bar text.
        
        Args:
            text (str): Status text to display
        """
        self.status_bar.set_status(text)
    
    def get_content_frame(self):
        """
        Get the main content frame for hosting views.
        
        Returns:
            CTkFrame: The main content frame
        """
        return self.content_frame
    
    def get_root(self):
        """
        Get the root window.
        
        Returns:
            CTk: The root window
        """
        return self.root
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()