"""
Main application window with cyberpunk theme
"""

import tkinter as tk
from tkinter import ttk
import pygame
from pathlib import Path
from typing import Dict, List, Optional

from ui.fretboard import FretboardCanvas
from ui.control_panel import ControlPanel
from ui.visualizers.chord_builder import ChordBuilderVisualizer
from ui.visualizers.scale_chord import ScaleChordVisualizer
from ui.visualizers.ear_trainer import EarTrainerVisualizer
from utils.config_manager import ConfigManager
from core.music_theory import MusicTheory

class MainWindow:
    """Main application window with cyberpunk theme"""
    
    def __init__(self, config: ConfigManager):
        """Initialize the main window and setup UI components"""
        self.config = config
        
        # Initialize pygame for audio
        pygame.mixer.init()
        
        # Setup the main window
        self.root = tk.Tk()
        self.root.title("NEON FRETBOARD - Cyberpunk Guitar Theory Explorer")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 768)
        
        # Set the cyberpunk theme
        self._setup_theme()
        
        # Initialize the music theory engine
        self.theory = MusicTheory(Path(__file__).parent.parent / "data")
        
        # Create UI components
        self._create_menu()
        self._create_main_frame()
        
        # Set up keyboard shortcuts
        self._setup_shortcuts()
        
    def _setup_theme(self):
        """Setup the cyberpunk theme colors and fonts"""
        # Define theme colors
        self.colors = {
            "bg_dark": "#0a0a12",
            "bg_med": "#151525",
            "bg_light": "#1e1e2f",
            "text_primary": "#00ccff",
            "text_secondary": "#ff00aa",
            "accent1": "#00ff99",
            "accent2": "#ff3366",
            "grid_line": "#303040",
            "fretboard": "#2a2a35"
        }
        
        # Configure ttk styles for the cyberpunk theme
        style = ttk.Style()
        style.theme_use('clam')  # Use clam as base theme
        
        # Configure colors
        style.configure(".", 
                       background=self.colors["bg_dark"],
                       foreground=self.colors["text_primary"],
                       font=("Orbitron", 10))
        
        style.configure("TButton", 
                       background=self.colors["bg_light"],
                       foreground=self.colors["text_primary"])
        
        style.map("TButton",
                 background=[("active", self.colors["accent1"])],
                 foreground=[("active", self.colors["bg_dark"])])
        
        # Set window background
        self.root.configure(bg=self.colors["bg_dark"])
        
    def _create_menu(self):
        """Create the application menu bar"""
        self.menu_bar = tk.Menu(self.root, bg=self.colors["bg_med"], 
                               fg=self.colors["text_primary"],
                               activebackground=self.colors["accent1"],
                               activeforeground=self.colors["bg_dark"])
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0, 
                          bg=self.colors["bg_med"],
                          fg=self.colors["text_primary"],
                          activebackground=self.colors["accent1"],
                          activeforeground=self.colors["bg_dark"])
        
        file_menu.add_command(label="New Session", command=self._new_session)
        file_menu.add_command(label="Save Configuration", command=self._save_config)
        file_menu.add_command(label="Load Configuration", command=self._load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0,
                          bg=self.colors["bg_med"],
                          fg=self.colors["text_primary"],
                          activebackground=self.colors["accent1"],
                          activeforeground=self.colors["bg_dark"])
        
        view_menu.add_command(label="Chord Builder", command=self._show_chord_builder)
        view_menu.add_command(label="Scale-Chord Relationships", command=self._show_scale_chord)
        view_menu.add_command(label="Ear Trainer", command=self._show_ear_trainer)
        
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0,
                          bg=self.colors["bg_med"],
                          fg=self.colors["text_primary"],
                          activebackground=self.colors["accent1"],
                          activeforeground=self.colors["bg_dark"])
        
        help_menu.add_command(label="Tutorial", command=self._show_tutorial)
        help_menu.add_command(label="About", command=self._show_about)
        
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        
        # Set the menu
        self.root.config(menu=self.menu_bar)
        
    def _create_main_frame(self):
        """Create the main application frame with all components"""
        # Main container frame
        self.main_frame = tk.Frame(self.root, bg=self.colors["bg_dark"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section with fretboard
        self.fretboard_frame = tk.Frame(self.main_frame, bg=self.colors["bg_dark"])
        self.fretboard_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create the fretboard canvas
        self.fretboard = FretboardCanvas(self.fretboard_frame, 
                                        bg=self.colors["fretboard"],
                                        color_scheme=self.colors)
        self.fretboard.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bottom section with control panel
        self.control_panel = ControlPanel(self.main_frame, 
                                        self.theory,
                                        self.colors,
                                        self._on_control_change)
        self.control_panel.pack(fill=tk.X, expand=False, pady=5)
        
        # Frame for visualizers (initially hidden)
        self.visualizer_frame = tk.Frame(self.main_frame, bg=self.colors["bg_med"])
        self.visualizers = {}
        
        # Initialize visualizers
        self._init_visualizers()
        
    def _init_visualizers(self):
        """Initialize all visualizer components"""
        # Chord Builder
        self.visualizers["chord_builder"] = ChordBuilderVisualizer(
            self.visualizer_frame, self.theory, self.colors
        )
        
        # Scale-Chord Relationships
        self.visualizers["scale_chord"] = ScaleChordVisualizer(
            self.visualizer_frame, self.theory, self.colors
        )
        
        # Ear Trainer
        self.visualizers["ear_trainer"] = EarTrainerVisualizer(
            self.visualizer_frame, self.theory, self.colors
        )
        
    def _show_visualizer(self, name: str):
        """Show a specific visualizer and hide others"""
        # Hide all visualizers first
        for vis in self.visualizers.values():
            vis.pack_forget()
            
        # Show the requested visualizer
        if name in self.visualizers:
            self.visualizer_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            self.visualizers[name].pack(fill=tk.BOTH, expand=True)
        else:
            self.visualizer_frame.pack_forget()
            
    def _on_control_change(self, event_type: str, data: dict):
        """Handle control panel events"""
        if event_type == "chord_changed":
            self.fretboard.display_chord(data["chord"])
            self.visualizers["chord_builder"].update_chord(data["chord"])
        elif event_type == "scale_changed":
            self.fretboard.display_scale(data["scale"])
        elif event_type == "clear":
            self.fretboard.clear()
        elif event_type == "highlight_changed":
            self.fretboard.set_highlight_type(data["type"])
        
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Control-n>", lambda e: self._new_session())
        self.root.bind("<Control-s>", lambda e: self._save_config())
        self.root.bind("<Control-o>", lambda e: self._load_config())
        self.root.bind("<F1>", lambda e: self._show_chord_builder())
        self.root.bind("<F2>", lambda e: self._show_scale_chord())
        self.root.bind("<F3>", lambda e: self._show_ear_trainer())
        
    def _new_session(self):
        """Reset to a new session"""
        self.control_panel.reset()
        self.fretboard.clear()
        self._show_visualizer(None)
        
    def _save_config(self):
        """Save current configuration"""
        self.config.save_config()
        
    def _load_config(self):
        """Load saved configuration"""
        self.config.load_config()
        
    def _show_chord_builder(self):
        """Show the chord builder visualizer"""
        self._show_visualizer("chord_builder")
        
    def _show_scale_chord(self):
        """Show the scale-chord relationships visualizer"""
        self._show_visualizer("scale_chord")
        
    def _show_ear_trainer(self):
        """Show the ear trainer visualizer"""
        self._show_visualizer("ear_trainer")
        
    def _show_tutorial(self):
        """Show the tutorial dialog"""
        # Tutorial dialog implementation
        pass
        
    def _show_about(self):
        """Show the about dialog"""
        # About dialog implementation
        pass
        
    def run(self):
        """Run the main application loop"""
        self.root.mainloop()