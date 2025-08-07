from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import hashlib
import time
import json
import shutil
from config import (
    ROM_DIRECTORY,
    METADATA_FILE,
    ROM_EXTENSIONS,
    ENABLE_DUPLICATE_SCAN
)

def hash_file_cpu(filepath, algo="sha1"):
    h = hashlib.new(algo)
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def hash_file(filepath):
    return hash_file_cpu(filepath)

def scan_file(file_path):
    try:
        return {
            "name": file_path.name,
            "path": str(file_path),
            "size": file_path.stat().st_size,
            "modified": time.ctime(file_path.stat().st_mtime),
            "sha1": hash_file(file_path)
        }
    except Exception as e:
        return {"error": str(e), "path": str(file_path)}

def scan_roms(directory, extensions=(".nes",)):
    rom_files = list(Path(directory).rglob("*"))
    rom_files = [f for f in rom_files if f.suffix.lower() in extensions]

    results = []
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(scan_file, f) for f in rom_files]
        for future in as_completed(futures):
            results.append(future.result())

    return results

def write_metadata_parallel(data, output_file):
    def write_json():
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(write_json)

def find_duplicates(rom_data):
    seen = {}
    duplicates = []
    for rom in rom_data:
        sha1 = rom.get("sha1")
        if sha1 in seen:
            duplicates.append((seen[sha1], rom))
        else:
            seen[sha1] = rom
    return duplicates

def save_duplicates_to_file(dupes, output_file="metadata/duplicate_roms.json"):
    data = []
    for original, duplicate in dupes:
        data.append({
            "original": original,
            "duplicate": duplicate
        })
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def move_duplicates(dupes, target_folder="output/duplicates"):
    target_path = Path(target_folder)
    target_path.mkdir(parents=True, exist_ok=True)

    for _, duplicate in dupes:
        src = Path(duplicate["path"])
        dst = target_path / src.name
        try:
            shutil.move(str(src), str(dst))
            print(f"📁 Moved duplicate: {src} -> {dst}")
        except Exception as e:
            print(f"❌ Failed to move {src}: {e}")

# ===== Main Execution =====
if __name__ == "__main__":
    print(f"📂 Scanning ROMs in: {ROM_DIRECTORY}")
    rom_metadata = scan_roms(ROM_DIRECTORY, extensions=ROM_EXTENSIONS)

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
        # now run rom_organizer.py from external script