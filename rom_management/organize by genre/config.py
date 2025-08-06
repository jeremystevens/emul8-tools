from pathlib import Path

# Update this path to point to your ROM collection
ROM_DIRECTORY = Path(r"")  # Your ROM input folder
OUTPUT_DIRECTORY = Path("output")  # Final organized ROM folder
METADATA_FILE = Path("metadata/rom_metadata.json")

# File extensions to scan for
ROM_EXTENSIONS = (".nes", ".fds")  # Add others if needed

# Enable duplicate checking
ENABLE_DUPLICATE_SCAN = True

# EverDrive-compatible options
TRIM_FILENAME_LENGTH = 32  # Optional: NES EverDrive has filename limits
REMOVE_SPECIAL_CHARS = True  # Clean file/folder names

# EverDrive structure rules
EVERDRIVE_LAYOUT = {
    "max_files_per_folder": 255,
    "flatten_nested_tags": True,  # Flatten sub-tags into one level
    "grouping": ["letter"],  # Can be ["letter"] or ["genre", "letter"]
}