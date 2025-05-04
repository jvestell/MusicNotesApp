#!/usr/bin/env python3
"""
NEON FRETBOARD - Cyberpunk Guitar Theory Explorer
A visual learning tool for guitar music theory with a cyberpunk aesthetic.
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# Import necessary modules
from ui.main_window import MainWindow
from utils.config_manager import ConfigManager

def main():
    """Launch the Neon Fretboard application"""
    # Setup configuration
    config = ConfigManager()
    config.load_or_create_default()
    
    # Create and run the application
    app = MainWindow(config)
    app.run()

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════╗
    ║ NEON FRETBOARD v1.0.0                         ║
    ║ Cyberpunk Guitar Theory Explorer              ║
    ║ ©2025 Neural String Technologies              ║
    ╚═══════════════════════════════════════════════╝
    """)
    main()