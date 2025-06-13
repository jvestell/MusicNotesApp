"""
Configuration management for user preferences
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages configuration settings and user preferences"""
    
    def __init__(self, config_file="config.json"):
        """Initialize with the path to the config file"""
        self.config_file = config_file
        self.config_path = Path.home() / ".neon_fretboard" / config_file
        
        # Default configuration
        self.default_config = {
            "appearance": {
                "theme": "cyberpunk",
                "text_size": "medium"
            },
            "fretboard": {
                "num_frets": 15,
                "show_note_names": True,
                "lefty_mode": False
            },
            "tuning": {
                "current": "standard",
                "custom": []
            }
        }
        
        # Current configuration
        self.config = {}
        
        # Load or create configuration
        self.load_or_create_default()
        
    def load_or_create_default(self):
        """Load existing config or create a new one with defaults"""
        if self.config_path.exists():
            self.load_config()
        else:
            self.config = self.default_config.copy()
            self.save_config()
            
    def ensure_config_dir(self):
        """Ensure the configuration directory exists"""
        config_dir = self.config_path.parent
        if not config_dir.exists():
            config_dir.mkdir(parents=True)
            
    def load_config(self, path: Optional[Path] = None):
        """Load configuration from file"""
        config_path = path or self.config_path
        
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                
            # Validate loaded config
            self._ensure_required_fields()
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading config: {e}")
            self.config = self.default_config.copy()
            
    def save_config(self, path: Optional[Path] = None):
        """Save configuration to file"""
        config_path = path or self.config_path
        
        try:
            self.ensure_config_dir()
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def _ensure_required_fields(self):
        """Ensure all required fields are present"""
        for section, values in self.default_config.items():
            if section not in self.config:
                self.config[section] = values
            else:
                for key, value in values.items():
                    if key not in self.config[section]:
                        self.config[section][key] = value
                        
    def get(self, section: str, key: str) -> Any:
        """Get a configuration value"""
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        elif section in self.default_config and key in self.default_config[section]:
            return self.default_config[section][key]
        else:
            raise KeyError(f"Configuration key '{section}.{key}' not found")
            
    def set(self, section: str, key: str, value: Any):
        """Set a configuration value"""
        if section not in self.config:
            self.config[section] = {}
            
        self.config[section][key] = value
        
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.config = self.default_config.copy()
        self.save_config()
        
    def export_config(self, path: Path):
        """Export configuration to a specified path"""
        try:
            with open(path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
            
    def import_config(self, path: Path):
        """Import configuration from a specified path"""
        try:
            with open(path, 'r') as f:
                new_config = json.load(f)
                
            # Validate the imported config
            for section, values in new_config.items():
                if not isinstance(values, dict):
                    raise ValueError(f"Invalid section format: {section}")
                    
            # Update current config
            self.config = new_config
            
            # Ensure all required fields are present
            self._ensure_required_fields()
            
            # Save the imported config
            self.save_config()
            
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False