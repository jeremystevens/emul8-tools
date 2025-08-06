import json
import shutil
import re
from pathlib import Path
from config import (
    ROM_DIRECTORY,
    OUTPUT_DIRECTORY,
    METADATA_FILE,
    TRIM_FILENAME_LENGTH,
    REMOVE_SPECIAL_CHARS,
    EVERDRIVE_LAYOUT
)

# Load metadata
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Output folder base
base_output = Path(OUTPUT_DIRECTORY)
base_output.mkdir(parents=True, exist_ok=True)

copied_count = 0
skipped_count = 0

# Helper: Clean filenames for EverDrive
invalid_chars = re.compile(r"[^a-zA-Z0-9 _\-\.]", re.UNICODE)

def clean_name(name):
    if REMOVE_SPECIAL_CHARS:
        name = invalid_chars.sub("", name)
    if TRIM_FILENAME_LENGTH:
        name = name[:TRIM_FILENAME_LENGTH]
    return name.strip()

# Folder tracking to enforce max_files_per_folder
folder_file_counts = {}

# Organizer
for rom in metadata:
    if "error" in rom:
        continue

    sha1 = rom.get("sha1", "")
    if "GPU hash error" in sha1 or not sha1 or len(sha1) != 40:
        continue

    rom_name = clean_name(rom["name"])
    letter = rom_name[0].upper() if rom_name else "_"
    folder_name = letter if letter.isalpha() else "_"

    # Final target folder
    target_folder = base_output / folder_name
    target_folder.mkdir(parents=True, exist_ok=True)

    # Enforce file count limit per folder
    count = folder_file_counts.get(folder_name, 0)
    if count >= EVERDRIVE_LAYOUT["max_files_per_folder"]:
        print(f"⚠️ Folder limit reached: {folder_name}, skipping {rom_name}")
        skipped_count += 1
        continue

    src = Path(rom["path"])
    dst = target_folder / rom_name

    if dst.exists():
        print(f"⏭️ Skipped (already exists): {dst}")
        skipped_count += 1
        continue

    try:
        shutil.copy2(src, dst)
        folder_file_counts[folder_name] = count + 1
        print(f"✅ Copied: {src} -> {dst}")
        copied_count += 1
    except Exception as e:
        print(f"❌ Failed to copy {src} to {dst}: {e}")

print(f"\n📦 EverDrive organization complete. {copied_count} copied, {skipped_count} skipped.")
