# ROM Collection Manager - Project Structure

## Directory Structure
```
rom_manager/
├── main.py                 # Entry point
├── config.py              # Configuration settings
├── gui/
│   ├── __init__.py
│   └── rom_manager_gui.py  # Main GUI class
├── modules/               # Future function modules
│   ├── __init__.py
│   ├── scanner.py         # ROM scanning functionality
│   ├── organizer.py       # ROM organization
│   ├── renamer.py         # ROM renaming
│   ├── deduplicator.py    # Duplicate detection/removal
│   └── database.py        # SQLite database operations
├── requirements.txt       # Python dependencies
└── README.md
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install customtkinter pillow sqlite3
```

### 2. Create Directory Structure
```bash
mkdir rom_manager
cd rom_manager
mkdir gui modules
touch gui/__init__.py modules/__init__.py
```

### 3. File Contents
- Copy `main.py` to the root directory
- Copy `config.py` to the root directory  
- Create `gui/__init__.py` (empty file)
- Copy `rom_manager_gui.py` to the `gui/` directory

### 4. Run the Application
```bash
python main.py
```

## Features Implemented

### ✅ GUI Layout Complete
- **Modern Dark Mode Interface** - Sleek, cutting-edge design with rounded corners and smooth styling
- **Sidebar Navigation** - Icon-based navigation with hover effects and active states
- **Responsive Layout** - Scales properly with window resizing
- **Status Bar** - Shows current application status

### ✅ Sections Implemented
1. **Scan ROMs** - Interface for directory selection, scan options, and progress tracking
2. **Organize ROMs** - Options for alphabetical, genre, and console organization
3. **Rename ROMs** - Multiple naming conventions with custom format support
4. **Deduplicate** - Hash-based and name-based duplicate detection options
5. **Settings** - Comprehensive configuration panel for all app settings

### ✅ Design Features
- **Icon Integration** - Modern emoji icons for visual appeal
- **Gradient Effects** - Subtle color transitions and hover states
- **Card-based Layout** - Organized content in rounded frames
- **Professional Typography** - Varied font weights and sizes for hierarchy
- **Interactive Elements** - Buttons with hover effects and state changes

## Next Steps (Module Implementation)

### 1. Database Module (`modules/database.py`)
```python
# SQLite operations for ROM metadata
# Tables: roms, genres, platforms, duplicates
```

### 2. Scanner Module (`modules/scanner.py`)
```python
# Directory scanning, metadata extraction
# Archive support, recursive scanning
```

### 3. Organizer Module (`modules/organizer.py`)
```python
# File moving/copying based on organization rules
# Folder structure creation
```

### 4. Renamer Module (`modules/renamer.py`)
```python
# Filename processing and standardization
# Custom format application
```

### 5. Deduplicator Module (`modules/deduplicator.py`)
```python
# Hash calculation, duplicate detection
# Smart duplicate removal with priority rules
```

## Configuration

The `config.py` file contains all application settings:
- **Supported file extensions** for various console systems
- **Default directories** and paths
- **Scanning, organizing, and naming options**
- **UI themes and appearance settings**
- **Performance and priority configurations**

## Modern Design Elements

### Color Scheme
- **Primary**: Blue accent (#1f6aa5, #4a9eff)
- **Background**: Dark theme with subtle frame colors
- **Text**: High contrast with multiple gray levels
- **Interactive**: Hover effects and state-based styling

### Layout Principles
- **Generous spacing** with consistent padding (20-40px)
- **Rounded corners** (12-15px) for modern appearance
- **Grid-based layout** for responsive behavior
- **Visual hierarchy** through typography and spacing
- **Card-style components** for content organization

The GUI is now complete and ready for backend module integration. Each section provides a clean, intuitive interface for ROM management tasks with a cutting-edge, modern aesthetic.




### UPDATED PLAN 

ROM Manager GUI Modularization Plan
====================================

Goal: Split the large GUI class into focused modules (views, components, controllers, services, and utils). Keep GUI lean by moving logic and bulky widget construction out of rom_manager_gui.py.

Project Layout (proposed)
-------------------------
rom_manager/
├── app.py                                 # App bootstrap; creates root, loads theme, mounts main window
├── gui/
│   ├── main_window.py                     # ROMManagerGUI shell (routing between views, high-level layout)
│   ├── components/
│   │   ├── sidebar.py                     # Sidebar (buttons, version label); emits navigation events
│   │   ├── header.py                      # Header area component
│   │   ├── status_bar.py                  # Status bar component
│   │   └── console_box.py                 # Reusable console textbox with timestamped append/clear helpers
│   └── views/
│       ├── scanning_view.py               # Scan & Index screen (UI only, no business logic)
│       ├── organizing_view.py             # Organize screen (UI only)
│       ├── renaming_view.py               # Rename screen (UI only)
│       ├── dedup_view.py                  # Deduplicate screen (UI only)
│       └── settings_view.py               # Settings screen (UI only; delegates to SettingsController)
├── controllers/
│   ├── nav_controller.py                  # Handles view switching; receives signals from Sidebar
│   ├── scan_controller.py                 # Wires scanning_view to scanning services
│   ├── organize_controller.py             # Wires organizing_view to organize services
│   ├── rename_controller.py               # Wires renaming_view to rename services
│   ├── dedup_controller.py                # Wires dedup_view to dedup services
│   └── settings_controller.py             # Load/save config, theme changes, backups, restart
├── services/
│   ├── theme_service.py                   # get/set appearance & color theme; persists via Config
│   ├── restart_service.py                 # Safe app restart logic
│   ├── dialog_service.py                  # File/folder browse, confirmation prompts
│   ├── config_service.py                  # Thin wrapper around Config with validation & persistence
│   └── db_backup_service.py               # Backs up DB (if applicable)
├── utils/
│   ├── console_logger.py                  # append_message(console, msg, type); timestamps, emoji map
│   ├── validators.py                      # Path validation, writable checks, etc.
│   └── constants.py                       # Shared strings, emoji, default sizes
└── styles/
    └── theme.py                           # Centralized fonts, sizes, paddings, corner radii

Mapping Current Code → New Files
--------------------------------
1) App/Window bootstrap
   - rom_manager_gui.py: class ROMManagerGUI.__init__, setup_ui, run
   - → gui/main_window.py (class MainWindow) for main container & region layout
   - → app.py for the real entrypoint (creates ctk.CTk, applies theme, instantiates MainWindow, mainloop)

2) Layout scaffolding
   - create_sidebar, create_main_content, create_status_bar
   - → components/sidebar.py (Sidebar class)
   - → components/header.py (Header class)
   - → components/status_bar.py (StatusBar class)
   - main_window wires them together and exposes set_status(text)

3) Navigation state & button highlighting
   - update_nav_buttons, current_frame logic
   - → controllers/nav_controller.py (tracks active view, updates Sidebar active state, swaps view frames)

4) Console helpers
   - add_console_message, clear_console
   - → utils/console_logger.py (ConsoleLogger.append / .clear)
   - → components/console_box.py (builds a styled CTkTextbox with scroll + convenience methods)

5) The five view builders
   - show_scanning_frame
   - show_organizing_frame
   - show_renaming_frame
   - show_deduplication_frame
   - show_settings_frame
   - → gui/views/*.py — each file exports a <Name>View(ctk.CTkFrame) subclass.
     * Pure UI: define widgets and expose events/callbacks (e.g., on_start_scan, on_preview, on_apply, on_save_settings)
     * No filesystem logic; emit to their controller

6) Theme/color change + restart
   - change_appearance_mode_event → services/theme_service.py.set_appearance(mode) + config_service
   - change_color_theme_event → services/theme_service.py.set_color_theme(color); if confirmed, restart_service.restart()
   - restart_application → services/restart_service.py.restart(root)

7) Settings persistence
   - save_settings → controllers/settings_controller.py.save_from_view(view)
   - Uses services/config_service.py to validate & save paths, theme, window size
   - Updates StatusBar via main_window.set_status()

8) Config I/O
   - Direct Config usage spread around → funnel through services/config_service.py
   - Provide load(), save(), update_theme_settings(), get_window_geometry(), set_window_geometry()

9) Constants & styling
   - Hardcoded strings/emojis and fonts spread around
   - → utils/constants.py (EMOJI, LABELS, VERSION, DEFAULT_GEOMETRY)
   - → styles/theme.py (font sizes, paddings, corner radii, shared CTkFont instances)

10) Dialogs / File pickers / Messageboxes
   - Direct messagebox & browse calls
   - → services/dialog_service.py (ask_yes_no, info, error, choose_directory, choose_file)
   - Views call a provided callback; controllers call dialog_service

Refactor Notes & Interface Contracts
------------------------------------
- Views accept a controller or callbacks at init:
  ScanningView(on_browse_dir, on_start_scan, options_model)
- Controllers connect to services and push messages to the view via small interfaces:
  view.show_progress(p), view.append_log(msg, type), view.set_enabled(state)

- MainWindow responsibilities:
  * Owns Sidebar, Header, StatusBar, and a central ViewHost frame
  * Exposes: switch_view(name: str), set_status(text: str)

- Sidebar emits navigation via a callback:
  on_nav("scan"|"organize"|"rename"|"dedup"|"settings")

- Theme service centralizes ctk.set_appearance_mode and color theme handling.
  Avoid calling messagebox directly inside the service—let controller handle UX.

Suggested File Extractions (direct from current methods)
--------------------------------------------------------
- create_sidebar                        → gui/components/sidebar.py (Sidebar)
- create_main_content                   → gui/components/header.py (Header host) + ViewHost in main_window.py
- create_status_bar                     → gui/components/status_bar.py (StatusBar)
- show_scanning_frame                   → gui/views/scanning_view.py (ScanningView)
- show_organizing_frame                 → gui/views/organizing_view.py (OrganizingView)
- show_renaming_frame                   → gui/views/renaming_view.py (RenamingView)
- show_deduplication_frame              → gui/views/dedup_view.py (DedupView)
- show_settings_frame                   → gui/views/settings_view.py (SettingsView)
- change_appearance_mode_event          → services/theme_service.py
- change_color_theme_event              → controllers/settings_controller.py + services/theme_service.py + services/restart_service.py
- restart_application                   → services/restart_service.py
- save_settings                         → controllers/settings_controller.py + services/config_service.py
- add_console_message / clear_console   → utils/console_logger.py + gui/components/console_box.py

Lean rom_manager_gui.py After Refactor
--------------------------------------
- Option A: Delete it; use app.py + gui/main_window.py as the new entry
- Option B: Keep rom_manager_gui.py as a single import/export that re-exports MainWindow for backward compatibility

Migration Steps (incremental)
-----------------------------
1) Extract ConsoleLogger + ConsoleBox first (no behavior change).
2) Extract Sidebar, StatusBar, Header into components/ and use them from a new MainWindow.
3) Move the 5 show_* methods into separate View classes.
4) Introduce NavController to switch views.
5) Move theme/restart/settings save into services/controllers.
6) Replace direct Config usage with ConfigService.
7) Move strings to constants and tune styles in styles/theme.py.
8) Create app.py as the entrypoint and trim the original file.

Benefits
--------
- Smaller, testable units (views are pure UI; controllers are logic)
- Clear separation of concerns; easier to replace views or logic
- Reusable console component across all screens
- Single place for theme and config logic, avoiding drift
