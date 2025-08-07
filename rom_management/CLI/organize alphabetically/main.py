from rom_scanner import scan_roms, write_metadata_parallel, find_duplicates, save_duplicates_to_file, move_duplicates
from config import ROM_DIRECTORY, METADATA_FILE, ROM_EXTENSIONS, ENABLE_DUPLICATE_SCAN

if __name__ == "__main__":
    print(f"📂 Scanning ROMs in: {ROM_DIRECTORY}")
    rom_metadata = scan_roms(ROM_DIRECTORY, extensions=ROM_EXTENSIONS)

    if not rom_metadata:
        print("⚠️ No ROM files found. Please check the ROM_DIRECTORY path and ROM_EXTENSIONS in config.py")
    else:
        print(f"✅ Found {len(rom_metadata)} ROM(s)")

        print(f"💾 Writing metadata to: {METADATA_FILE}")
        write_metadata_parallel(rom_metadata, METADATA_FILE)

        if ENABLE_DUPLICATE_SCAN:
            print("🔍 Checking for duplicate ROMs...")
            dupes = find_duplicates(rom_metadata)
            for original, duplicate in dupes:
                print(f"⚠️ Duplicate found:\n - {original['path']}\n - {duplicate['path']}\n")
            print(f"🧩 Total duplicates: {len(dupes)}")

            save_duplicates_to_file(dupes)
            print("📁 Duplicate results saved to: metadata/duplicate_roms.json")

            move_duplicates(dupes)
            print("✅ All duplicate files moved.")
