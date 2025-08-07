import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import subprocess
import datetime
from pathlib import Path
from PIL import Image
from config import Config


class ROMManagerGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("ROM Collection Manager")
        
        # Load window size from config
        window_size = getattr(Config, 'WINDOW_SIZE', "1400x900")
        self.root.geometry(window_size)
        self.root.minsize(1200, 800)
        
        # Configure grid layout
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Initialize variables
        self.current_frame = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
        
        # Show scanning frame by default
        self.show_scanning_frame()
    
    def create_sidebar(self):
        """Create the modern sidebar navigation"""
        # Sidebar frame
        self.sidebar_frame = ctk.CTkFrame(
            self.root, width=280, corner_radius=0
        )
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)  # Empty space
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="ROM Manager", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("#1f6aa5", "#4a9eff")
        )
        self.logo_label.grid(row=0, column=0, padx=30, pady=(30, 40))
        
        # Navigation buttons with icons and modern styling
        nav_buttons = [
            ("🔍", "Scan ROMs", self.show_scanning_frame),
            ("📁", "Organize", self.show_organizing_frame),
            ("✏️", "Rename", self.show_renaming_frame),
            ("🗂️", "Deduplicate", self.show_deduplication_frame),
            ("⚙️", "Settings", self.show_settings_frame)
        ]
        
        self.nav_buttons = []
        for i, (icon, text, command) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=f"{icon}  {text}",
                font=ctk.CTkFont(size=16, weight="normal"),
                height=50,
                anchor="w",
                command=command,
                corner_radius=12,
                hover_color=("#2b2b2b", "#404040"),
                text_color=("gray70", "gray90"),
                fg_color="transparent"
            )
            btn.grid(row=i+1, column=0, padx=20, pady=8, sticky="ew")
            self.nav_buttons.append(btn)
        
        # Version info at bottom
        version_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        )
        version_label.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="s")
    
    def create_main_content(self):
        """Create the main content area"""
        self.main_frame = ctk.CTkFrame(
            self.root, corner_radius=0, fg_color="transparent"
        )
        self.main_frame.grid(
            row=0, column=1, sticky="nsew", padx=0, pady=0
        )
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Header frame
        self.header_frame = ctk.CTkFrame(
            self.main_frame, height=80, corner_radius=0, fg_color="transparent"
        )
        self.header_frame.grid(
            row=0, column=0, sticky="ew", padx=30, pady=(30, 0)
        )
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Content frame (this will hold different sections)
        self.content_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.content_frame.grid(
            row=1, column=0, sticky="nsew", padx=30, pady=30
        )
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
    
    def create_status_bar(self):
        """Create a modern status bar"""
        self.status_frame = ctk.CTkFrame(
            self.root, height=40, corner_radius=0
        )
        self.status_frame.grid(row=1, column=1, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=8, sticky="w")
    
    def clear_content_frame(self):
        """Clear the current content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_nav_buttons(self, active_index):
        """Update navigation button states"""
        for i, btn in enumerate(self.nav_buttons):
            if i == active_index:
                btn.configure(
                    fg_color=("#1f6aa5", "#4a9eff"), text_color="white"
                )
            else:
                btn.configure(
                    fg_color="transparent", 
                    text_color=("gray70", "gray90")
                )
    
    def show_scanning_frame(self):
        """Show the ROM scanning interface"""
        self.clear_content_frame()
        self.update_nav_buttons(0)
        
        # Clear and update header
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        
        header_label = ctk.CTkLabel(
            self.header_frame,
            text="Scan & Index ROMs",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("gray10", "gray90")
        )
        header_label.grid(row=0, column=0, sticky="w", pady=10)
        
        # Main scanning interface
        scan_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        scan_frame.grid(
            row=0, column=0, sticky="nsew", padx=40, pady=40
        )
        scan_frame.grid_columnconfigure(0, weight=1)
        scan_frame.grid_rowconfigure(3, weight=1)  # Console expandable
        
        # Directory selection
        dir_frame = ctk.CTkFrame(scan_frame, corner_radius=12)
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
        
        browse_btn = ctk.CTkButton(
            dir_frame, 
            text="Browse", 
            width=100, 
            height=40,
            corner_radius=8
        )
        browse_btn.grid(row=0, column=2, padx=20, pady=20)
        
        # Scan options
        options_frame = ctk.CTkFrame(scan_frame, corner_radius=12)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            options_frame, 
            text="Scan Options", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Checkboxes for scan options
        self.recursive_var = ctk.BooleanVar(value=True)
        self.metadata_var = ctk.BooleanVar(value=True)
        self.generate_thumbnails_var = ctk.BooleanVar(value=False)
        
        ctk.CTkCheckBox(
            options_frame, 
            text="Scan subdirectories recursively", 
            variable=self.recursive_var
        ).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        ctk.CTkCheckBox(
            options_frame, 
            text="Extract metadata", 
            variable=self.metadata_var
        ).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        ctk.CTkCheckBox(
            options_frame, 
            text="Generate thumbnails", 
            variable=self.generate_thumbnails_var
        ).grid(row=3, column=0, padx=20, pady=(5, 20), sticky="w")
        
        # Scan button and progress
        action_frame = ctk.CTkFrame(scan_frame, corner_radius=12)
        action_frame.grid(row=2, column=0, sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)
        
        scan_btn = ctk.CTkButton(
            action_frame,
            text="🔍 Start Scan",
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=12
        )
        scan_btn.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Progress bar (hidden by default)
        self.scan_progress = ctk.CTkProgressBar(action_frame)
        self.scan_progress.grid(
            row=1, column=0, padx=20, pady=(0, 20), sticky="ew"
        )
        self.scan_progress.grid_remove()  # Hide initially
        
        # Console output area
        console_frame = ctk.CTkFrame(scan_frame, corner_radius=12)
        console_frame.grid(row=3, column=0, sticky="nsew", pady=(20, 0))
        console_frame.grid_columnconfigure(0, weight=1)
        console_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            console_frame, 
            text="📋 Scan Output", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.scan_console = ctk.CTkTextbox(
            console_frame,
            height=200,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=("gray95", "gray10"),
            text_color=("gray20", "gray80"),
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        self.scan_console.grid(
            row=1, column=0, padx=20, pady=(5, 20), sticky="nsew"
        )
        
        # Add welcome message
        self.scan_console.insert("0.0", "🚀 ROM Scanner Console\n")
        self.scan_console.insert("end", "─" * 50 + "\n")
        self.scan_console.insert("end", "Ready to scan ROM collection...\n")
        self.scan_console.insert(
            "end", "Select a directory and configure options to begin.\n\n"
        )
        self.scan_console.configure(state="disabled")
        
        self.status_label.configure(text="Ready to scan ROMs")
    
    def show_organizing_frame(self):
        """Show the ROM organizing interface"""
        self.clear_content_frame()
        self.update_nav_buttons(1)
        
        # Clear and update header
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        
        header_label = ctk.CTkLabel(
            self.header_frame,
            text="Organize ROMs",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("gray10", "gray90")
        )
        header_label.grid(row=0, column=0, sticky="w", pady=10)
        
        # Organizing interface
        org_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        org_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        org_frame.grid_columnconfigure(0, weight=1)
        org_frame.grid_rowconfigure(2, weight=1)  # Console expandable
        
        # Organization options
        options_frame = ctk.CTkFrame(org_frame, corner_radius=12)
        options_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            options_frame, 
            text="Organization Method", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        self.org_method = ctk.StringVar(value="alphabetical")
        
        ctk.CTkRadioButton(
            options_frame, 
            text="Alphabetical (A-Z)", 
            variable=self.org_method, 
            value="alphabetical"
        ).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        ctk.CTkRadioButton(
            options_frame, 
            text="By Genre", 
            variable=self.org_method, 
            value="genre"
        ).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        ctk.CTkRadioButton(
            options_frame, 
            text="By Console/Platform", 
            variable=self.org_method, 
            value="console"
        ).grid(row=3, column=0, padx=20, pady=(5, 20), sticky="w")
        
        # Action buttons
        action_frame = ctk.CTkFrame(org_frame, corner_radius=12)
        action_frame.grid(row=1, column=0, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        preview_btn = ctk.CTkButton(
            action_frame,
            text="📋 Preview Changes",
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=12,
            fg_color="transparent",
            border_width=2
        )
        preview_btn.grid(
            row=0, column=0, padx=(20, 10), pady=20, sticky="ew"
        )
        
        organize_btn = ctk.CTkButton(
            action_frame,
            text="📁 Organize ROMs",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12
        )
        organize_btn.grid(
            row=0, column=1, padx=(10, 20), pady=20, sticky="ew"
        )
        
        # Console output area
        console_frame = ctk.CTkFrame(org_frame, corner_radius=12)
        console_frame.grid(row=2, column=0, sticky="nsew", pady=(20, 0))
        console_frame.grid_columnconfigure(0, weight=1)
        console_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            console_frame, 
            text="📁 Organization Output", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.org_console = ctk.CTkTextbox(
            console_frame,
            height=200,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=("gray95", "gray10"),
            text_color=("gray20", "gray80"),
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        self.org_console.grid(
            row=1, column=0, padx=20, pady=(5, 20), sticky="nsew"
        )
        
        # Add welcome message
        self.org_console.insert("0.0", "📂 ROM Organizer Console\n")
        self.org_console.insert("end", "─" * 50 + "\n")
        self.org_console.insert("end", "Ready to organize ROM collection...\n")
        self.org_console.insert(
            "end", "Choose organization method and preview changes first.\n\n"
        )
        self.org_console.configure(state="disabled")
        
        self.status_label.configure(text="Ready to organize ROMs")
    
    def show_renaming_frame(self):
        """Show the ROM renaming interface"""
        self.clear_content_frame()
        self.update_nav_buttons(2)
        
        # Clear and update header
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        
        header_label = ctk.CTkLabel(
            self.header_frame,
            text="Rename ROMs",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("gray10", "gray90")
        )
        header_label.grid(row=0, column=0, sticky="w", pady=10)
        
        # Renaming interface
        rename_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        rename_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        rename_frame.grid_columnconfigure(0, weight=1)
        rename_frame.grid_rowconfigure(2, weight=1)  # Console expandable
        
        # Naming conventions
        conventions_frame = ctk.CTkFrame(rename_frame, corner_radius=12)
        conventions_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            conventions_frame, 
            text="Naming Convention", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        self.naming_convention = ctk.StringVar(value="no_tags")
        
        conventions = [
            ("Remove region/language tags", "no_tags"),
            ("Standard format: Game Name (Region)", "standard"),
            ("Custom format", "custom")
        ]
        
        for i, (text, value) in enumerate(conventions):
            ctk.CTkRadioButton(
                conventions_frame, 
                text=text, 
                variable=self.naming_convention, 
                value=value
            ).grid(row=i+1, column=0, padx=20, pady=5, sticky="w")
        
        # Custom format entry
        self.custom_format_entry = ctk.CTkEntry(
            conventions_frame, 
            placeholder_text="e.g., {name} [{region}] ({year})",
            height=35
        )
        self.custom_format_entry.grid(
            row=4, column=0, padx=40, pady=(5, 20), sticky="ew"
        )
        
        # Preview and action
        action_frame = ctk.CTkFrame(rename_frame, corner_radius=12)
        action_frame.grid(row=1, column=0, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        preview_btn = ctk.CTkButton(
            action_frame,
            text="👀 Preview Renames",
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=12,
            fg_color="transparent",
            border_width=2
        )
        preview_btn.grid(
            row=0, column=0, padx=(20, 10), pady=20, sticky="ew"
        )
        
        rename_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Apply Renames",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12
        )
        rename_btn.grid(
            row=0, column=1, padx=(10, 20), pady=20, sticky="ew"
        )
        
        # Console output area
        console_frame = ctk.CTkFrame(rename_frame, corner_radius=12)
        console_frame.grid(row=2, column=0, sticky="nsew", pady=(20, 0))
        console_frame.grid_columnconfigure(0, weight=1)
        console_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            console_frame, 
            text="✏️ Rename Output", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.rename_console = ctk.CTkTextbox(
            console_frame,
            height=200,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=("gray95", "gray10"),
            text_color=("gray20", "gray80"),
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        self.rename_console.grid(
            row=1, column=0, padx=20, pady=(5, 20), sticky="nsew"
        )
        
        # Add welcome message
        self.rename_console.insert("0.0", "🏷️ ROM Renamer Console\n")
        self.rename_console.insert("end", "─" * 50 + "\n")
        self.rename_console.insert("end", "Ready to rename ROM files...\n")
        self.rename_console.insert(
            "end", "Select naming convention and preview changes.\n\n"
        )
        self.rename_console.configure(state="disabled")
        
        self.status_label.configure(text="Ready to rename ROMs")
    
    def show_deduplication_frame(self):
        """Show the ROM deduplication interface"""
        self.clear_content_frame()
        self.update_nav_buttons(3)
        
        # Clear and update header
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        
        header_label = ctk.CTkLabel(
            self.header_frame,
            text="Deduplicate ROMs",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("gray10", "gray90")
        )
        header_label.grid(row=0, column=0, sticky="w", pady=10)
        
        # Deduplication interface
        dedup_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        dedup_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        dedup_frame.grid_columnconfigure(0, weight=1)
        dedup_frame.grid_rowconfigure(3, weight=1)  # Console expandable
        
        # Detection method
        method_frame = ctk.CTkFrame(dedup_frame, corner_radius=12)
        method_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            method_frame, 
            text="Detection Method", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        self.detection_method = ctk.StringVar(value="hash")
        
        methods = [
            ("File hash (MD5/SHA1) - Most accurate", "hash"),
            ("File size and name comparison", "size_name"),
            ("Name similarity only", "name_only")
        ]
        
        for i, (text, value) in enumerate(methods):
            ctk.CTkRadioButton(
                method_frame, 
                text=text, 
                variable=self.detection_method, 
                value=value
            ).grid(row=i+1, column=0, padx=20, pady=5, sticky="w")
        
        # Action options
        options_frame = ctk.CTkFrame(dedup_frame, corner_radius=12)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            options_frame, 
            text="Duplicate Handling", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        self.move_to_folder_var = ctk.BooleanVar(value=True)
        self.keep_best_version_var = ctk.BooleanVar(value=True)
        
        ctk.CTkCheckBox(
            options_frame, 
            text="Move duplicates to separate folder", 
            variable=self.move_to_folder_var
        ).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        ctk.CTkCheckBox(
            options_frame, 
            text="Keep best version (prefer no-intro/redump)", 
            variable=self.keep_best_version_var
        ).grid(row=2, column=0, padx=20, pady=(5, 20), sticky="w")
        
        # Action buttons
        action_frame = ctk.CTkFrame(dedup_frame, corner_radius=12)
        action_frame.grid(row=2, column=0, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        scan_dupes_btn = ctk.CTkButton(
            action_frame,
            text="🔍 Scan for Duplicates",
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=12,
            fg_color="transparent",
            border_width=2
        )
        scan_dupes_btn.grid(
            row=0, column=0, padx=(20, 10), pady=20, sticky="ew"
        )
        
        remove_dupes_btn = ctk.CTkButton(
            action_frame,
            text="🗂️ Remove Duplicates",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12
        )
        remove_dupes_btn.grid(
            row=0, column=1, padx=(10, 20), pady=20, sticky="ew"
        )
        
        # Console output area
        console_frame = ctk.CTkFrame(dedup_frame, corner_radius=12)
        console_frame.grid(row=3, column=0, sticky="nsew", pady=(20, 0))
        console_frame.grid_columnconfigure(0, weight=1)
        console_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            console_frame, 
            text="🔍 Deduplication Output", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.dedup_console = ctk.CTkTextbox(
            console_frame,
            height=200,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=("gray95", "gray10"),
            text_color=("gray20", "gray80"),
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        self.dedup_console.grid(
            row=1, column=0, padx=20, pady=(5, 20), sticky="nsew"
        )
        
        # Add welcome message
        self.dedup_console.insert("0.0", "🗂️ Duplicate Finder Console\n")
        self.dedup_console.insert("end", "─" * 50 + "\n")
        self.dedup_console.insert("end", "Ready to find duplicate ROMs...\n")
        self.dedup_console.insert(
            "end", "Configure detection method and scan for duplicates.\n\n"
        )
        self.dedup_console.configure(state="disabled")
        
        self.status_label.configure(text="Ready to deduplicate ROMs")
    
    def show_settings_frame(self):
        """Show the settings interface"""
        self.clear_content_frame()
        self.update_nav_buttons(4)
        
        # Clear and update header
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        
        header_label = ctk.CTkLabel(
            self.header_frame,
            text="Settings",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("gray10", "gray90")
        )
        header_label.grid(row=0, column=0, sticky="w", pady=10)
        
        # Settings interface
        settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_rowconfigure(4, weight=1)  # Console expandable
        
        # ROM Directories
        dirs_frame = ctk.CTkFrame(settings_frame, corner_radius=12)
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
        
        ctk.CTkButton(
            dirs_frame, text="Browse", width=80
        ).grid(row=1, column=2, padx=20, pady=10)
        
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
        
        ctk.CTkButton(
            dirs_frame, text="Browse", width=80
        ).grid(row=2, column=2, padx=20, pady=(10, 20))
        
        # Appearance settings
        appearance_frame = ctk.CTkFrame(settings_frame, corner_radius=12)
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
            width=200,
            command=self.change_appearance_mode_event
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
            width=200,
            command=self.change_color_theme_event
        )
        
        # Set from config with proper title case conversion
        if Config.COLOR_THEME == "dark-blue":
            current_color = "Dark-blue"
        else:
            current_color = Config.COLOR_THEME.title()
        self.color_combo.set(current_color)
        self.color_combo.grid(row=2, column=1, padx=20, pady=(10, 20), sticky="w")
        
        # Database settings
        db_frame = ctk.CTkFrame(settings_frame, corner_radius=12)
        db_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            db_frame, 
            text="Database", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        self.auto_backup_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            db_frame, 
            text="Auto-backup database", 
            variable=self.auto_backup_var
        ).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        # Action buttons
        action_frame = ctk.CTkFrame(settings_frame, corner_radius=12)
        action_frame.grid(row=3, column=0, sticky="ew")
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        reset_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Reset to Defaults",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=12,
            fg_color="transparent",
            border_width=2,
            text_color=("gray70", "gray70")
        )
        reset_btn.grid(
            row=0, column=0, padx=(20, 10), pady=20, sticky="ew"
        )
        
        backup_btn = ctk.CTkButton(
            action_frame,
            text="💾 Backup Database",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=12,
            fg_color="transparent",
            border_width=2
        )
        backup_btn.grid(row=0, column=1, padx=10, pady=20, sticky="ew")
        
        save_btn = ctk.CTkButton(
            action_frame,
            text="💾 Save Settings",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12,
            command=self.save_settings
        )
        save_btn.grid(row=0, column=2, padx=(10, 20), pady=20, sticky="ew")
        
        # Console output area for settings
        console_frame = ctk.CTkFrame(settings_frame, corner_radius=12)
        console_frame.grid(row=4, column=0, sticky="nsew", pady=(20, 0))
        console_frame.grid_columnconfigure(0, weight=1)
        console_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            console_frame, 
            text="⚙️ Settings Output", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.settings_console = ctk.CTkTextbox(
            console_frame,
            height=150,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=("gray95", "gray10"),
            text_color=("gray20", "gray80"),
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        self.settings_console.grid(
            row=1, column=0, padx=20, pady=(5, 20), sticky="nsew"
        )
        
        # Add welcome message
        self.settings_console.insert("0.0", "🔧 Settings Console\n")
        self.settings_console.insert("end", "─" * 40 + "\n")
        self.settings_console.insert("end", "Configuration management ready...\n")
        self.settings_console.insert(
            "end", "Update paths and preferences as needed.\n\n"
        )
        self.settings_console.configure(state="disabled")
        
        self.status_label.configure(text="Configure application settings")
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Change the appearance mode (Dark/Light/System)"""
        # Convert display names to ctk values
        mode_mapping = {
            "Dark": "dark",
            "Light": "light", 
            "System": "system"
        }
        
        ctk_mode = mode_mapping.get(new_appearance_mode, "dark")
        ctk.set_appearance_mode(ctk_mode)
        
        # Update config and save
        Config.update_theme_settings(theme=ctk_mode)
        
        # Update status
        self.status_label.configure(
            text=f"Appearance mode changed to {new_appearance_mode}"
        )
        
    def change_color_theme_event(self, new_color_theme: str):
        """Change the color theme (Blue/Green/Dark-blue) and restart app"""
        # Convert display names to ctk values
        theme_mapping = {
            "Blue": "blue",
            "Green": "green",
            "Dark-blue": "dark-blue"
        }
        
        ctk_theme = theme_mapping.get(new_color_theme, "blue")
        
        # Update config and save
        Config.update_theme_settings(color_theme=ctk_theme)
        
        # Show restart dialog
        result = messagebox.askyesno(
            "Restart Required",
            f"Color theme changed to {new_color_theme}.\n\n"
            f"The application needs to restart to fully apply the new "
            f"color theme.\n\nRestart now?",
            icon="question"
        )
        
        if result:
            self.restart_application()
        else:
            self.status_label.configure(
                text="Color theme will apply after restart"
            )
    
    def restart_application(self):
        """Restart the application to apply color theme changes"""
        try:
            # Save current window size before restarting
            current_geometry = self.root.geometry()
            Config.WINDOW_SIZE = current_geometry
            Config.save_to_file()
            
            # Close current application
            self.root.quit()
            self.root.destroy()
            
            # Restart the application
            python_executable = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            
            # Use subprocess to start new instance
            subprocess.Popen([python_executable, script_path])
            
        except Exception as e:
            messagebox.showerror(
                "Restart Error", f"Could not restart application: {e}"
            )
            self.status_label.configure(
                text="Restart failed - please restart manually"
            )
    
    def save_settings(self):
        """Save all current settings to config file"""
        try:
            # Update paths from entry widgets
            Config.ROM_DIR = Path(self.default_rom_dir.get())
            Config.DUPLICATES_DIR = Path(self.duplicates_dir.get())
            
            # Save current theme settings from dropdowns
            theme_mapping = {
                "Dark": "dark",
                "Light": "light", 
                "System": "system"
            }
            color_mapping = {
                "Blue": "blue",
                "Green": "green",
                "Dark-blue": "dark-blue"
            }
            
            current_theme = theme_mapping.get(self.theme_combo.get(), "dark")
            current_color = color_mapping.get(self.color_combo.get(), "blue")
            
            Config.update_theme_settings(
                theme=current_theme, color_theme=current_color
            )
            
            # Save current window geometry
            Config.WINDOW_SIZE = self.root.geometry()
            
            # Save to file
            Config.save_to_file()
            
            self.status_label.configure(text="Settings saved successfully")
            messagebox.showinfo("Settings", "Settings saved successfully!")
            
        except Exception as e:
            self.status_label.configure(text=f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Could not save settings: {e}")
    
    def add_console_message(self, console_widget, message, message_type="info"):
        """Add a message to a console widget with timestamp and formatting"""
        # Enable editing temporarily
        console_widget.configure(state="normal")
        
        # Get timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Format message based on type
        if message_type == "info":
            prefix = "ℹ️"
        elif message_type == "success":
            prefix = "✅"
        elif message_type == "warning":
            prefix = "⚠️"
        elif message_type == "error":
            prefix = "❌"
        else:
            prefix = "📝"
        
        # Add message with formatting
        formatted_message = f"[{timestamp}] {prefix} {message}\n"
        console_widget.insert("end", formatted_message)
        
        # Auto-scroll to bottom
        console_widget.see("end")
        
        # Disable editing
        console_widget.configure(state="disabled")
    
    def clear_console(self, console_widget):
        """Clear a console widget"""
        console_widget.configure(state="normal")
        console_widget.delete("1.0", "end")
        console_widget.configure(state="disabled")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()