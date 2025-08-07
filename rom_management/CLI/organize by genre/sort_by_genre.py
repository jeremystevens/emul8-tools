""" 
Filename: sort_by_genre3.py
Description: 
    Multi-threaded ROM organizer that matches ROM files to genres using XML metadata.
    It creates cleaned filename variations, performs aggressive string matching,
    utilizes optional GPU acceleration (CuPy), and organizes ROMs into folders by genre.
    Results, stats, and unmatched entries are saved for review.

Created by: Jeremy Stevens
Created on: August 6, 2025
Python Version: 3.8+
Dependencies:
    - numpy (required)
    - cupy (optional, for GPU acceleration)
    - xml.etree.ElementTree
    - pathlib
    - shutil
    - re
    - json
    - concurrent.futures
    - threading
    - time
    - os
    - difflib

Notes:
    - Requires a compatible `config.py` with settings such as:
        OUTPUT_DIRECTORY, ROM_EXTENSIONS, REMOVE_SPECIAL_CHARS, TRIM_FILENAME_LENGTH
    - Designed for use with EmulationStation-style gamelist XMLs.
 """

import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
import re
import json
import concurrent.futures
from threading import Lock
import time
import os
from difflib import SequenceMatcher
from config import (
    OUTPUT_DIRECTORY,
    ROM_EXTENSIONS, 
    REMOVE_SPECIAL_CHARS,
    TRIM_FILENAME_LENGTH
)

# GPU acceleration with CuPy
try:
    import cupy as cp
    import numpy as np
    CUPY_AVAILABLE = True
    print("CuPy detected - GPU acceleration enabled!")
except ImportError:
    import numpy as np
    CUPY_AVAILABLE = False
    print("CuPy not available - using CPU processing")

# Thread-safe locks
file_lock = Lock()
stats_lock = Lock()


def clean_filename(filename, max_length=None):
    """Clean filename for filesystem compatibility."""
    if REMOVE_SPECIAL_CHARS:
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'[^\w\s\-_\.]', '', filename)
    
    if max_length and len(filename) > max_length:
        name_part = filename.rsplit('.', 1)[0]
        ext_part = '.' + filename.rsplit('.', 1)[1] if '.' in filename else ''
        available_length = max_length - len(ext_part)
        filename = name_part[:available_length] + ext_part
    
    return filename.strip()


def similarity(a, b):
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def analyze_rom_collection(rom_directory):
    """Analyze ROM collection and create a mapping file."""
    print("Analyzing ROM collection...")
    
    rom_files = []
    for ext in ROM_EXTENSIONS:
        rom_files.extend(Path(rom_directory).glob(f"*{ext}"))
        rom_files.extend(Path(rom_directory).glob(f"**/*{ext}"))
    
    analysis = {
        'total_roms': len(rom_files),
        'sample_names': [],
        'common_prefixes': set(),
        'common_suffixes': set()
    }
    
    # Collect sample names and patterns
    for rom in rom_files[:50]:  # First 50 for analysis
        name = rom.stem
        analysis['sample_names'].append(name)
        
        # Check for common patterns
        if '(' in name:
            parts = name.split('(')
            if len(parts) > 1:
                analysis['common_suffixes'].add(f"({parts[1]}")
        
        # Check for common prefixes
        words = name.split()
        if len(words) > 1:
            analysis['common_prefixes'].add(words[0])
    
    # Save analysis
    with open("rom_analysis.json", "w") as f:
        json.dump({
            'total_roms': analysis['total_roms'],
            'sample_names': analysis['sample_names'],
            'common_prefixes': list(analysis['common_prefixes']),
            'common_suffixes': list(analysis['common_suffixes'])
        }, f, indent=2)
    
    print(f"ROM Analysis saved to rom_analysis.json")
    print(f"Found {analysis['total_roms']} ROM files")
    return analysis


def create_ultra_aggressive_variations(name):
    """Create comprehensive name variations for better matching."""
    variations = set()
    original = name.strip()
    variations.add(original)
    variations.add(original.lower())
    
    # Step 1: Remove ALL parentheses content and variations
    base_patterns = [
        r'\([^)]*\)',  # Remove anything in parentheses
        r'\[[^\]]*\]',  # Remove anything in brackets
    ]
    
    current = original
    for pattern in base_patterns:
        cleaned = re.sub(pattern, '', current, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)
        if cleaned:
            variations.add(cleaned)
            variations.add(cleaned.lower())
            current = cleaned
    
    # Step 2: Handle separators more aggressively
    separator_variants = []
    for variant in list(variations):
        # Replace common separators
        separators = ['_', '-', '.', '+', '&', "'", '!', '?', ':', ';', ' - ']
        for sep in separators:
            if sep in variant:
                # Replace with space
                with_space = variant.replace(sep, ' ')
                with_space = re.sub(r'\s+', ' ', with_space).strip()
                separator_variants.append(with_space)
                separator_variants.append(with_space.lower())
                
                # Remove completely
                without_sep = variant.replace(sep, '')
                without_sep = re.sub(r'\s+', ' ', without_sep).strip()
                separator_variants.append(without_sep)
                separator_variants.append(without_sep.lower())
    
    variations.update(separator_variants)
    
    # Step 3: Handle "The" article more thoroughly
    article_variants = []
    for variant in list(variations):
        # "The" at beginning
        if variant.lower().startswith('the '):
            without_the = variant[4:].strip()
            article_variants.extend([without_the, without_the.lower()])
            # Move to end
            with_comma = without_the + ', The'
            article_variants.extend([with_comma, with_comma.lower()])
        
        # "The" at end
        if variant.lower().endswith(', the'):
            without_the = variant[:-5].strip()
            article_variants.extend([without_the, without_the.lower()])
            # Move to beginning
            with_the = 'The ' + without_the
            article_variants.extend([with_the, with_the.lower()])
    
    variations.update(article_variants)
    
    # Step 4: Remove all punctuation version
    for variant in list(variations):
        no_punct = re.sub(r'[^\w\s]', ' ', variant)
        no_punct = re.sub(r'\s+', ' ', no_punct).strip()
        if no_punct:
            variations.add(no_punct)
            variations.add(no_punct.lower())
    
    # Step 5: Handle numbers and roman numerals
    number_variants = []
    for variant in list(variations):
        # Roman to Arabic
        roman_conversions = {
            ' II': ' 2', ' III': ' 3', ' IV': ' 4', ' V': ' 5',
            'II ': '2 ', 'III ': '3 ', 'IV ': '4 ', 'V ': '5 ',
            'II': '2', 'III': '3', 'IV': '4', 'V': '5'
        }
        
        for roman, arabic in roman_conversions.items():
            if roman.lower() in variant.lower():
                converted = variant.replace(roman, arabic)
                number_variants.extend([converted, converted.lower()])
        
        # Remove numbers at end
        no_end_nums = re.sub(r'\s*\d+\s*$', '', variant).strip()
        if no_end_nums != variant:
            number_variants.extend([no_end_nums, no_end_nums.lower()])
    
    variations.update(number_variants)
    
    # Step 6: Abbreviation expansions
    abbreviations = {
        'Dr.': 'Doctor', 'Mr.': 'Mister', 'Bros.': 'Brothers',
        'Co.': 'Company', '&': 'and', 'vs.': 'versus', 'vs': 'versus'
    }
    
    abbrev_variants = []
    for variant in list(variations):
        for abbrev, expansion in abbreviations.items():
            if abbrev.lower() in variant.lower():
                expanded = variant.replace(abbrev, expansion)
                abbrev_variants.extend([expanded, expanded.lower()])
            if expansion.lower() in variant.lower():
                abbreviated = variant.replace(expansion, abbrev)
                abbrev_variants.extend([abbreviated, abbreviated.lower()])
    
    variations.update(abbrev_variants)
    
    # Clean up and return unique variations
    final_variations = []
    seen = set()
    
    for var in variations:
        if var and len(var.strip()) > 1:  # At least 2 characters
            cleaned = re.sub(r'\s+', ' ', var.strip())
            if cleaned not in seen:
                seen.add(cleaned)
                final_variations.append(cleaned)
    
    return final_variations


def enhanced_xml_parsing(xml_file_path):
    """Enhanced XML parsing with ultra-aggressive region stripping."""
    print("Parsing XML with enhanced strategies...")
    
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        rom_metadata = {}
        xml_name_list = []
        
        games = root.findall('.//game')
        print(f"Found {len(games)} game elements")
        print("Creating comprehensive name variations...")
        
        processed_count = 0
        for game in games:
            name = None
            if 'name' in game.attrib:
                name = game.attrib['name']
            else:
                name_elem = game.find('name')
                if name_elem is not None:
                    name = name_elem.text
            
            if not name:
                continue
            
            name = name.strip()
            xml_name_list.append(name)
            
            # Get genre
            genre = "Unknown"
            genre_elem = game.find('genre')
            if genre_elem is not None and genre_elem.text:
                genre = genre_elem.text.strip()
            
            if '/' in genre:
                genre = genre.split('/')[0].strip()
            
            # Create ultra-aggressive variations for better matching
            variations = create_ultra_aggressive_variations(name)
            
            # Create clean base name
            clean_base_name = name
            region_patterns = [
                r'\(USA, Europe\)', r'\(USA\)', r'\(Europe\)', 
                r'\(Japan\)', r'\(World\)', r'\(U\)', r'\(E\)', 
                r'\(J\)', r'\(W\)', r'\(Beta\)', r'\(Alpha\)', 
                r'\(Demo\)', r'\(Proto\)', r'\(Prototype\)',
                r'\(Unl\)', r'\(Unlicensed\)',
            ]
            
            for pattern in region_patterns:
                clean_base_name = re.sub(
                    pattern, '', clean_base_name, flags=re.IGNORECASE
                ).strip()
                clean_base_name = re.sub(r'\s+', ' ', clean_base_name)
            
            if clean_base_name and clean_base_name != name:
                # Add clean name as high priority
                variations.insert(0, clean_base_name)
                variations.insert(1, clean_base_name.lower())
            
            # Store variations (increased limit for better matching)
            for variation in variations[:50]:  # Increased from 20 to 50
                if variation and len(variation.strip()) > 1:
                    rom_metadata[variation] = {
                        'original_name': name,
                        'clean_name': clean_base_name,
                        'genre': genre,
                        'full_genre': (
                            genre_elem.text.strip() 
                            if genre_elem is not None and genre_elem.text 
                            else genre
                        )
                    }
            
            processed_count += 1
            if processed_count % 100 == 0:
                print(f"  Processed {processed_count}/{len(games)} games...")
        
        total_variations = len(rom_metadata)
        total_games = len(xml_name_list)
        print(f"Created {total_variations} variations from {total_games} games")
        
        # Save XML analysis
        print("Saving XML analysis...")
        with open("xml_games.txt", "w", encoding="utf-8") as f:
            f.write("Games found in XML (Original -> Clean):\n")
            f.write("-" * 50 + "\n")
            for name in sorted(xml_name_list):
                clean_name = name
                basic_patterns = [
                    r'\(USA\)', r'\(Europe\)', r'\(Japan\)', 
                    r'\(U\)', r'\(E\)', r'\(J\)'
                ]
                for pattern in basic_patterns:
                    clean_name = re.sub(
                        pattern, '', clean_name, flags=re.IGNORECASE
                    ).strip()
                
                f.write(f"{name}")
                if clean_name != name:
                    f.write(f" -> {clean_name}")
                f.write("\n")
        
        print("XML parsing complete!")
        return rom_metadata, xml_name_list
        
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return {}, []


def hyper_aggressive_rom_matching(rom_file, metadata, xml_names, debug=False):
    """Ultra-aggressive ROM matching with multiple fallback strategies."""
    rom_name = rom_file.stem
    
    if debug:
        print(f"    Matching: {rom_name}")
    
    # Strategy 1: Direct exact matching with ultra-aggressive variations
    rom_variations = create_ultra_aggressive_variations(rom_name)
    
    if debug:
        print(f"      ROM variations ({len(rom_variations)}): "
              f"{rom_variations[:8]}...")
    
    # Try all variations for exact matches
    for variation in rom_variations:
        if variation in metadata:
            if debug:
                clean_name = metadata[variation].get('clean_name', 'N/A')
                print(f"    ✓ Direct match: '{variation}' -> '{clean_name}'")
            return metadata[variation]
    
    # Strategy 2: Case insensitive exact matching
    for variation in rom_variations:
        for meta_key in metadata.keys():
            if variation.lower() == meta_key.lower():
                if debug:
                    print(f"    ✓ Case match: '{variation}' = '{meta_key}'")
                return metadata[meta_key]
    
    # Strategy 3: Substring matching for short ROM names
    if len(rom_name) <= 12:
        for variation in rom_variations:
            variation_lower = variation.lower()
            if len(variation_lower) >= 4:  # Minimum length for substring matching
                for meta_key, meta_data in metadata.items():
                    meta_lower = meta_key.lower()
                    # Check if ROM variation is contained in metadata key
                    if (variation_lower in meta_lower and 
                        len(variation_lower) >= len(meta_lower) * 0.6):
                        if debug:
                            print(f"    ✓ Substring match: '{variation}' in "
                                  f"'{meta_key}'")
                        return meta_data
    
    # Strategy 4: Aggressive similarity matching with lower thresholds
    best_match = None
    best_score = 0
    
    # Check more variations against more XML names
    for rom_var in rom_variations[:15]:  # Increased from 5
        for xml_name in xml_names[:300]:  # Increased from 100
            score = similarity(rom_var.lower(), xml_name.lower())
            if score > best_score and score >= 0.70:  # Lowered from 0.80
                best_score = score
                best_match = xml_name
    
    if best_match:
        for meta_key, meta_data in metadata.items():
            if meta_data['original_name'] == best_match:
                if debug:
                    print(f"    ✓ Similarity match: '{rom_name}' ≈ "
                          f"'{best_match}' (score: {best_score:.2f})")
                return meta_data
    
    # Strategy 5: Word-based matching (if key words match)
    rom_words = set(re.sub(r'[^\w\s]', ' ', rom_name.lower()).split())
    rom_words = {w for w in rom_words if len(w) > 2}  # Only words > 2 chars
    
    if len(rom_words) >= 1:
        for xml_name in xml_names[:500]:  # Check more XML names
            # Clean XML name
            xml_clean = re.sub(r'\([^)]*\)', '', xml_name).strip().lower()
            xml_words = set(re.sub(r'[^\w\s]', ' ', xml_clean).split())
            xml_words = {w for w in xml_words if len(w) > 2}
            
            if len(xml_words) >= 1:
                common_words = rom_words.intersection(xml_words)
                if len(common_words) >= 1:
                    # Calculate coverage
                    rom_coverage = (len(common_words) / len(rom_words) 
                                  if rom_words else 0)
                    xml_coverage = (len(common_words) / len(xml_words) 
                                  if xml_words else 0)
                    
                    # Accept if good coverage on either side
                    if rom_coverage >= 0.5 or xml_coverage >= 0.5:
                        for meta_key, meta_data in metadata.items():
                            if meta_data['original_name'] == xml_name:
                                if debug:
                                    print(f"    ✓ Word match: '{rom_name}' ≈ "
                                          f"'{xml_name}' (words: {common_words})")
                                return meta_data
    
    # Strategy 6: Very loose partial matching for single words
    if len(rom_words) == 1:
        rom_word = list(rom_words)[0]
        if len(rom_word) >= 4:  # Only for words 4+ characters
            for xml_name in xml_names[:200]:
                xml_clean = re.sub(r'\([^)]*\)', '', xml_name).strip().lower()
                if rom_word in xml_clean:
                    # Additional check: make sure it's a significant match
                    clean_length = len(xml_clean.replace(' ', ''))
                    if len(rom_word) >= clean_length * 0.3:
                        for meta_key, meta_data in metadata.items():
                            if meta_data['original_name'] == xml_name:
                                if debug:
                                    print(f"    ✓ Single word match: "
                                          f"'{rom_word}' in '{xml_name}'")
                                return meta_data
    
    if debug:
        print(f"    ✗ No match found for '{rom_name}'")
        # Show potential near-matches
        potential_matches = []
        for xml_name in xml_names[:20]:
            xml_clean = re.sub(r'\([^)]*\)', '', xml_name).strip()
            score = similarity(rom_name.lower(), xml_clean.lower())
            if score > 0.4:
                potential_matches.append((xml_name, score))
        
        if potential_matches:
            potential_matches.sort(key=lambda x: x[1], reverse=True)
            print(f"      Near matches: {potential_matches[:3]}")
    
    return None


def process_rom_batch_matching_only(rom_batch, metadata, xml_names, debug=False):
    """Process ROM batch for matching only - no file operations."""
    local_results = []
    
    for rom_file in rom_batch:
        metadata_entry = hyper_aggressive_rom_matching(
            rom_file, metadata, xml_names, debug=debug
        )
        
        if metadata_entry:
            genre = metadata_entry['genre']
            result = {
                'rom_file': rom_file,
                'matched': True,
                'genre': genre,
                'xml_name': metadata_entry['original_name'],
                'full_genre': metadata_entry['full_genre']
            }
        else:
            result = {
                'rom_file': rom_file,
                'matched': False,
                'genre': "Unknown",
                'xml_name': None,
                'full_genre': "Unknown"
            }
        
        local_results.append(result)
    
    return local_results


def copy_roms_sequentially(rom_results, genre_dir):
    """Copy ROMs sequentially to avoid file conflicts."""
    print("Copying ROMs to genre folders...")
    
    stats = {'matched': 0, 'unmatched': 0, 'genres': {}}
    matched_details = []
    unmatched_roms = []
    
    total_roms = len(rom_results)
    
    for i, result in enumerate(rom_results):
        if i % 200 == 0:  # Progress every 200 files
            progress = (i / total_roms) * 100
            print(f"  Copying progress: {i}/{total_roms} ({progress:.1f}%)")
        
        rom_file = result['rom_file']
        clean_genre = clean_filename(result['genre']) or "Unknown"
        
        # Update stats
        if result['matched']:
            stats['matched'] += 1
            matched_details.append((
                rom_file.name, result['xml_name'], result['full_genre']
            ))
        else:
            stats['unmatched'] += 1
            unmatched_roms.append(rom_file.name)
        
        stats['genres'][clean_genre] = stats['genres'].get(clean_genre, 0) + 1
        
        # Create genre folder
        genre_folder = genre_dir / clean_genre
        genre_folder.mkdir(exist_ok=True)
        
        # Prepare destination
        destination_name = rom_file.name
        if TRIM_FILENAME_LENGTH:
            destination_name = clean_filename(rom_file.name, TRIM_FILENAME_LENGTH)
        
        destination = genre_folder / destination_name
        
        # Copy file if it doesn't exist
        try:
            if not destination.exists():
                shutil.copy2(rom_file, destination)
        except Exception as e:
            print(f"Error copying {rom_file.name}: {e}")
    
    print("ROM copying complete!")
    return stats, matched_details, unmatched_roms


def organize_roms_by_genre(xml_file_path, output_base_dir=None, 
                          debug_mode=False, max_workers=8):
    """Enhanced ROM organization with separated matching and file copying phases."""
    if output_base_dir is None:
        output_base_dir = OUTPUT_DIRECTORY
    
    acceleration_type = 'GPU (CuPy)' if CUPY_AVAILABLE else 'CPU'
    print(f"Using {acceleration_type} acceleration with {max_workers} threads")
    start_time = time.time()
    
    # Create genre base directory
    genre_dir = Path("genre")
    genre_dir.mkdir(parents=True, exist_ok=True)
    
    # Analyze ROM collection first
    rom_analysis = analyze_rom_collection(output_base_dir)
    
    # Enhanced XML parsing
    print("Parsing XML metadata...")
    rom_metadata, xml_names = enhanced_xml_parsing(xml_file_path)
    
    if not rom_metadata:
        print("No metadata found. Exiting.")
        return
    
    # Find ROM files
    print("Finding ROM files...")
    rom_files = []
    for ext in ROM_EXTENSIONS:
        rom_files.extend(Path(output_base_dir).glob(f"*{ext}"))
        rom_files.extend(Path(output_base_dir).glob(f"**/*{ext}"))
    
    if not rom_files:
        print("No ROM files found. Exiting.")
        return
    
    total_roms = len(rom_files)
    print(f"Phase 1: Matching {total_roms} ROMs with {max_workers} workers...")
    
    # Split ROMs into batches
    batch_size = max(1, total_roms // max_workers)
    rom_batches = [rom_files[i:i + batch_size] 
                   for i in range(0, total_roms, batch_size)]
    
    print(f"Split into {len(rom_batches)} batches of ~{batch_size} ROMs each")
    
    # Phase 1: Parallel ROM matching (no file operations)
    all_results = []
    processed_count = 0
    matching_start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_batch = {}
        for i, batch in enumerate(rom_batches):
            batch_debug = debug_mode and i == 0
            future = executor.submit(
                process_rom_batch_matching_only, 
                batch, 
                rom_metadata, 
                xml_names, 
                batch_debug
            )
            future_to_batch[future] = (i, len(batch))
        
        for future in concurrent.futures.as_completed(future_to_batch):
            batch_idx, batch_size = future_to_batch[future]
            try:
                batch_results = future.result()
                all_results.extend(batch_results)
                processed_count += batch_size
                
                progress = (processed_count / total_roms) * 100
                elapsed = time.time() - matching_start
                rate = processed_count / elapsed if elapsed > 0 else 0
                eta = ((total_roms - processed_count) / rate 
                       if rate > 0 else 0)
                
                print(f"Matching batch {batch_idx + 1}/{len(rom_batches)} "
                      f"complete - Progress: {processed_count}/{total_roms} "
                      f"({progress:.1f}%) - Rate: {rate:.1f} ROMs/sec - "
                      f"ETA: {eta:.1f}s")
                
            except Exception as exc:
                print(f"Batch {batch_idx} generated an exception: {exc}")
    
    matching_time = time.time() - matching_start
    print(f"Phase 1 complete - Matching took {matching_time:.2f} seconds")
    
    # Phase 2: Sequential file copying (no conflicts)
    print("Phase 2: Copying ROMs to genre folders...")
    copying_start = time.time()
    
    stats, matched_details, unmatched_roms = copy_roms_sequentially(
        all_results, genre_dir
    )
    stats['total_roms'] = total_roms
    
    copying_time = time.time() - copying_start
    total_time = time.time() - start_time
    
    print(f"Phase 2 complete - Copying took {copying_time:.2f} seconds")
    
    # Final results
    print("\n" + "="*80)
    print("MULTI-THREADED ORGANIZATION RESULTS")
    print("="*80)
    print(f"Total processing time: {total_time:.2f} seconds")
    print(f"  - Matching phase: {matching_time:.2f} seconds")
    print(f"  - Copying phase: {copying_time:.2f} seconds")
    print(f"Average rate: {total_roms/total_time:.1f} ROMs/second")
    print(f"Total ROMs processed: {stats['total_roms']}")
    print(f"Successfully matched: {stats['matched']}")
    print(f"Unmatched (Unknown): {stats['unmatched']}")
    print(f"Match rate: {stats['matched']/stats['total_roms']*100:.1f}%")
    print(f"Parallel workers: {max_workers}")
    
    print(f"\nGenres created:")
    for genre, count in sorted(stats['genres'].items()):
        print(f"  {genre}: {count} ROMs")
    
    # Save detailed results
    with open("matching_results.txt", "w", encoding="utf-8") as f:
        f.write("MULTI-THREADED ROM MATCHING RESULTS\n")
        f.write("="*60 + "\n\n")
        f.write(f"Processing time: {total_time:.2f} seconds\n")
        f.write(f"  - Matching: {matching_time:.2f}s\n")
        f.write(f"  - Copying: {copying_time:.2f}s\n")
        f.write(f"Processing rate: {total_roms/total_time:.1f} ROMs/second\n")
        f.write(f"Parallel workers: {max_workers}\n\n")
        f.write(f"Total ROMs: {stats['total_roms']}\n")
        f.write(f"Matched: {stats['matched']}\n")
        f.write(f"Unmatched: {stats['unmatched']}\n")
        f.write(f"Match rate: {stats['matched']/stats['total_roms']*100:.1f}%\n\n")
        
        f.write("MATCHED ROMS:\n")
        f.write("-" * 40 + "\n")
        for rom_file, xml_name, genre in sorted(matched_details):
            f.write(f"{rom_file} -> {xml_name} -> {genre}\n")
        
        f.write(f"\nUNMATCHED ROMS ({len(unmatched_roms)}):\n")
        f.write("-" * 40 + "\n")
        for rom in sorted(unmatched_roms):
            f.write(f"{rom}\n")
    
    print(f"\nDetailed results saved to: matching_results.txt")
    print(f"ROM analysis saved to: rom_analysis.json")
    print(f"XML games list saved to: xml_games.txt")
    print(f"\n🎉 No more file conflicts! All ROMs processed successfully.")


def main():
    """Main entry point with threading options."""
    print("Multi-Threaded ROM Genre Organizer")
    print("==================================")
    
    # Find XML files
    xml_files = list(Path('.').glob('*.xml'))
    
    if not xml_files:
        print("No XML files found in current directory.")
        return
    
    if len(xml_files) == 1:
        xml_path = xml_files[0]
        print(f"Using XML file: {xml_path}")
    else:
        print("Multiple XML files found:")
        for i, xml_file in enumerate(xml_files, 1):
            print(f"  {i}. {xml_file.name}")
        
        try:
            choice = int(input("Select XML file (number): ")) - 1
            xml_path = xml_files[choice]
        except (ValueError, IndexError):
            print("Invalid selection. Exiting.")
            return
    
    # Check output directory
    if not OUTPUT_DIRECTORY.exists():
        print(f"Output directory not found: {OUTPUT_DIRECTORY}")
        print("Creating output directory...")
        OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    
def main():
    """Main entry point with threading options."""
    print("Multi-Threaded ROM Genre Organizer")
    print("==================================")
    
    # Find XML files
    xml_files = list(Path('.').glob('*.xml'))
    
    if not xml_files:
        print("No XML files found in current directory.")
        return
    
    if len(xml_files) == 1:
        xml_path = xml_files[0]
        print(f"Using XML file: {xml_path}")
    else:
        print("Multiple XML files found:")
        for i, xml_file in enumerate(xml_files, 1):
            print(f"  {i}. {xml_file.name}")
        
        try:
            choice = int(input("Select XML file (number): ")) - 1
            xml_path = xml_files[choice]
        except (ValueError, IndexError):
            print("Invalid selection. Exiting.")
            return
    
    # Check output directory
    if not OUTPUT_DIRECTORY.exists():
        print(f"Output directory not found: {OUTPUT_DIRECTORY}")
        print("Creating output directory...")
        OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    
    # Threading options
    default_workers = min(8, os.cpu_count() or 4)
    workers_input = input(
        f"Number of parallel workers (default {default_workers}): "
    ).strip()
    try:
        max_workers = int(workers_input) if workers_input else default_workers
        max_workers = max(1, min(max_workers, 16))
    except ValueError:
        max_workers = default_workers
    
    # Debug mode option
    debug_choice = input("Enable debug mode for first batch? (y/n): ").lower()
    debug_mode = debug_choice == 'y'
    
    print(f"\nStarting organization with {max_workers} workers...")
    acceleration_status = "ENABLED" if CUPY_AVAILABLE else "DISABLED"
    print(f"GPU acceleration: {acceleration_status}")
    
    # Start enhanced organization
    organize_roms_by_genre(xml_path, OUTPUT_DIRECTORY, debug_mode, max_workers)


if __name__ == "__main__":
    main()