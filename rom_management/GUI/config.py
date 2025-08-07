# ROM Manager Configuration File

import os
import configparser
from pathlib import Path

class Config:
    """Configuration class for ROM Manager"""
    
    # Application Info
    APP_NAME = "ROM Collection Manager"
    APP_VERSION = "1.0.0"
    
    # Default Directories
    BASE_DIR = Path.home() / "ROM_Manager"
    ROM_DIR = BASE_DIR / "ROMs"
    DUPLICATES_DIR = BASE_DIR / "Duplicates"
    BACKUP_DIR = BASE_DIR / "Backups"
    THUMBNAILS_DIR = BASE_DIR / "Thumbnails"
    
    # Configuration file
    CONFIG_FILE = BASE_DIR / "config.ini"
    
    # Database Configuration
    DATABASE_PATH = BASE_DIR / "rom_collection.db"
    BACKUP_DATABASE = True
    MAX_BACKUPS = 5
    
    # Scanning Options
    SUPPORTED_EXTENSIONS = {
        '.zip', '.rar', '.7z', '.gz', '.tar',  # Archives
        '.iso', '.cue', '.bin', '.img', '.nrg',  # Disc images
        '.rom', '.smc', '.sfc', '.fig',  # SNES
        '.nes', '.fds', '.nsf',  # NES
        '.gb', '.gbc', '.gba',  # Game Boy
        '.n64', '.z64', '.v64',  # N64
        '.md', '.smd', '.gen',  # Genesis/Mega Drive
        '.32x', '.sms', '.gg',  # Sega
        '.pce', '.sgx',  # PC Engine
        '.lnx',  # Lynx
        '.ngp', '.ngc',  # Neo Geo Pocket
        '.ws', '.wsc',  # WonderSwan
    }
    
    RECURSIVE_SCAN = True
    EXTRACT_METADATA = True
    GENERATE_THUMBNAILS = False
    SCAN_ARCHIVES = True
    
    # Organization Options
    DEFAULT_ORGANIZATION = "alphabetical"  # alphabetical, genre, console
    CREATE_SUBFOLDERS = True
    PRESERVE_ORIGINAL_STRUCTURE = False
    
    # Naming Convention Options
    DEFAULT_NAMING_CONVENTION = "no_tags"  # no_tags, standard, custom
    CUSTOM_FORMAT = "{name} [{region}]"
    REMOVE_BRACKETS = True
    CLEAN_NAMES = True
    
    # Deduplication Options
    DETECTION_METHOD = "hash"  # hash, size_name, name_only
    HASH_ALGORITHM = "md5"  # md5, sha1, sha256
    MOVE_DUPLICATES = True
    KEEP_BEST_VERSION = True
    
    # Priority for keeping "best" versions (higher number = higher priority)
    VERSION_PRIORITIES = {
        "no-intro": 100,
        "redump": 95,
        "goodtools": 80,
        "tosec": 70,
        "trurip": 60,
        "unknown": 50
    }
    
    # Region priorities (for keeping best version)
    REGION_PRIORITIES = {
        "USA": 100,
        "World": 95,
        "Europe": 90,
        "Japan": 85,
        "UK": 80,
        "Germany": 75,
        "France": 70,
        "Unknown": 50
    }
    
    # UI Settings
    THEME = "dark"  # dark, light, system
    COLOR_THEME = "blue"  # blue, green, dark-blue
    WINDOW_SIZE = "1400x900"
    WINDOW_MIN_SIZE = "1200x800"
    
    # Performance Settings
    MAX_CONCURRENT_SCANS = 4
    CHUNK_SIZE = 8192  # For file hashing
    PROGRESS_UPDATE_INTERVAL = 100  # milliseconds
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.BASE_DIR,
            cls.ROM_DIR,
            cls.DUPLICATES_DIR,
            cls.BACKUP_DIR,
            cls.THUMBNAILS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def load_from_file(cls):
        """Load configuration from config.ini file"""
        config = configparser.ConfigParser()
        
        if cls.CONFIG_FILE.exists():
            try:
                config.read(cls.CONFIG_FILE)
                
                # Load UI settings
                if 'UI' in config:
                    cls.THEME = config['UI'].get('theme', cls.THEME)
                    cls.COLOR_THEME = config['UI'].get('color_theme', cls.COLOR_THEME)
                    cls.WINDOW_SIZE = config['UI'].get('window_size', cls.WINDOW_SIZE)
                
                # Load directories
                if 'DIRECTORIES' in config:
                    rom_dir = config['DIRECTORIES'].get('rom_dir', str(cls.ROM_DIR))
                    duplicates_dir = config['DIRECTORIES'].get('duplicates_dir', str(cls.DUPLICATES_DIR))
                    cls.ROM_DIR = Path(rom_dir)
                    cls.DUPLICATES_DIR = Path(duplicates_dir)
                
                # Load scanning options
                if 'SCANNING' in config:
                    cls.RECURSIVE_SCAN = config['SCANNING'].getboolean('recursive_scan', cls.RECURSIVE_SCAN)
                    cls.EXTRACT_METADATA = config['SCANNING'].getboolean('extract_metadata', cls.EXTRACT_METADATA)
                    cls.GENERATE_THUMBNAILS = config['SCANNING'].getboolean('generate_thumbnails', cls.GENERATE_THUMBNAILS)
                
                # Load organization options
                if 'ORGANIZATION' in config:
                    cls.DEFAULT_ORGANIZATION = config['ORGANIZATION'].get('default_organization', cls.DEFAULT_ORGANIZATION)
                
                # Load naming options
                if 'NAMING' in config:
                    cls.DEFAULT_NAMING_CONVENTION = config['NAMING'].get('default_naming_convention', cls.DEFAULT_NAMING_CONVENTION)
                    cls.CUSTOM_FORMAT = config['NAMING'].get('custom_format', cls.CUSTOM_FORMAT)
                
                # Load deduplication options
                if 'DEDUPLICATION' in config:
                    cls.DETECTION_METHOD = config['DEDUPLICATION'].get('detection_method', cls.DETECTION_METHOD)
                    cls.MOVE_DUPLICATES = config['DEDUPLICATION'].getboolean('move_duplicates', cls.MOVE_DUPLICATES)
                    cls.KEEP_BEST_VERSION = config['DEDUPLICATION'].getboolean('keep_best_version', cls.KEEP_BEST_VERSION)
                
            except Exception as e:
                print(f"Error loading config file: {e}")
    
    @classmethod
    def save_to_file(cls):
        """Save current configuration to config.ini file"""
        config = configparser.ConfigParser()
        
        # UI Settings
        config['UI'] = {
            'theme': cls.THEME,
            'color_theme': cls.COLOR_THEME,
            'window_size': cls.WINDOW_SIZE
        }
        
        # Directories
        config['DIRECTORIES'] = {
            'rom_dir': str(cls.ROM_DIR),
            'duplicates_dir': str(cls.DUPLICATES_DIR),
            'backup_dir': str(cls.BACKUP_DIR),
            'thumbnails_dir': str(cls.THUMBNAILS_DIR)
        }
        
        # Scanning Options
        config['SCANNING'] = {
            'recursive_scan': str(cls.RECURSIVE_SCAN),
            'extract_metadata': str(cls.EXTRACT_METADATA),
            'generate_thumbnails': str(cls.GENERATE_THUMBNAILS),
            'scan_archives': str(cls.SCAN_ARCHIVES)
        }
        
        # Organization Options
        config['ORGANIZATION'] = {
            'default_organization': cls.DEFAULT_ORGANIZATION,
            'create_subfolders': str(cls.CREATE_SUBFOLDERS),
            'preserve_original_structure': str(cls.PRESERVE_ORIGINAL_STRUCTURE)
        }
        
        # Naming Options
        config['NAMING'] = {
            'default_naming_convention': cls.DEFAULT_NAMING_CONVENTION,
            'custom_format': cls.CUSTOM_FORMAT,
            'remove_brackets': str(cls.REMOVE_BRACKETS),
            'clean_names': str(cls.CLEAN_NAMES)
        }
        
        # Deduplication Options
        config['DEDUPLICATION'] = {
            'detection_method': cls.DETECTION_METHOD,
            'hash_algorithm': cls.HASH_ALGORITHM,
            'move_duplicates': str(cls.MOVE_DUPLICATES),
            'keep_best_version': str(cls.KEEP_BEST_VERSION)
        }
        
        # Performance Settings
        config['PERFORMANCE'] = {
            'max_concurrent_scans': str(cls.MAX_CONCURRENT_SCANS),
            'chunk_size': str(cls.CHUNK_SIZE),
            'progress_update_interval': str(cls.PROGRESS_UPDATE_INTERVAL)
        }
        
        try:
            # Ensure directory exists
            cls.ensure_directories()
            
            # Save to file
            with open(cls.CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
                
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    @classmethod
    def update_theme_settings(cls, theme=None, color_theme=None):
        """Update theme settings and save to config"""
        if theme:
            cls.THEME = theme.lower()
        if color_theme:
            cls.COLOR_THEME = color_theme.lower()
        
        # Save the updated configuration
        cls.save_to_file()