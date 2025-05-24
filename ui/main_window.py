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
from ui.note_palette import NotePalette
from ui.visualizers.chord_builder import ChordBuilderVisualizer
from ui.visualizers.scale_chord import ScaleChordVisualizer
from ui.visualizers.ear_trainer import EarTrainerVisualizer
from utils.config_manager import ConfigManager
from core.music_theory import MusicTheory
from core.note_system import Note
from core.chord_system import Chord
from core.scale_system import Scale

class MainWindow:
    """Main application window with cyberpunk theme"""
    
    def __init__(self, config: ConfigManager):
        """Initialize the main window and setup UI components"""
        self.config = config
        
        # Initialize pygame for audio
        pygame.mixer.init()
        
        # Setup the main window
        self.root = tk.Tk()
        self.root.title("NeckNavigator - Guitar Theory Explorer")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 768)
        
        # Set the NeckNavigator theme
        self._setup_theme()
        
        # Initialize the music theory engine
        self.theory = MusicTheory(Path(__file__).parent.parent / "data")
        
        # Create UI components
        self._create_menu()
        self._create_main_frame()
        
        # Set up keyboard shortcuts
        self._setup_shortcuts()
        
    def _setup_theme(self):
        """Setup the NeckNavigator theme colors and fonts"""
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
        
        # Configure ttk styles for the NeckNavigator theme
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
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        
        # View menu (Chord Builder only)
        view_menu = tk.Menu(self.menu_bar, tearoff=0,
                          bg=self.colors["bg_med"],
                          fg=self.colors["text_primary"],
                          activebackground=self.colors["accent1"],
                          activeforeground=self.colors["bg_dark"])
        
        view_menu.add_command(label="Chord Builder", command=self._show_chord_builder)
        
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        
        self.root.config(menu=self.menu_bar)
        
    def _create_main_frame(self):
        """Create the main application frame with all components"""
        # Main container frame
        self.main_frame = tk.Frame(self.root, bg=self.colors["bg_dark"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section with fretboard and note palette
        self.fretboard_frame = tk.Frame(self.main_frame, bg=self.colors["bg_dark"])
        self.fretboard_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create the fretboard canvas
        self.fretboard = FretboardCanvas(self.fretboard_frame, 
                                        bg=self.colors["fretboard"],
                                        color_scheme=self.colors)
        self.fretboard.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the note palette (initially hidden)
        self.note_palette = NotePalette(self.fretboard_frame,
                                      self.colors,
                                      self._on_note_drag_start,
                                      self._on_note_drag_end)
        self.note_palette.pack_forget()
        
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
        # Chord Builder only
        self.visualizers["chord_builder"] = ChordBuilderVisualizer(
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
            # Check for visual effect
            visual_effect = data.get("visual_effect")
            self.fretboard.display_chord(data["chord"], visual_effect)
            self.visualizers["chord_builder"].update_chord(data["chord"])
        elif event_type == "scale_changed":
            self.fretboard.display_scale(data["scale"])
        elif event_type == "clear":
            self.fretboard.clear()
        elif event_type == "highlight_changed":
            self.fretboard.set_highlight_type(data["type"])
        elif event_type == "new_position":
            # Handle new random position request for game mode
            self.fretboard.set_random_triad_position()
        elif event_type == "note_placement_mode":
            # Handle note placement mode toggle
            if data["enabled"]:
                self.note_palette.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
                self.fretboard.set_note_placement_mode(True)
            else:
                self.note_palette.pack_forget()
                self.fretboard.set_note_placement_mode(False)
        elif event_type == "clear_placed_notes":
            # Clear all manually placed notes
            self.fretboard.clear_placed_notes()
        
    def _on_note_drag_start(self, note, event):
        """Handle the start of a note drag operation"""
        # Create a custom event with the note data
        event.note = note
        # Trigger the drag start event on the fretboard
        self.fretboard._on_drag_start(event)
        
    def _on_note_drag_end(self, note, event):
        """Handle the end of a note drag operation"""
        # Create a custom event with the note data
        event.note = note
        # Trigger the drag end event on the fretboard
        self.fretboard._on_drag_release(event)
        
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Control-n>", lambda e: self._new_session())
        self.root.bind("<F1>", lambda e: self._show_chord_builder())
        
    def _new_session(self):
        """Reset to a new session"""
        self.control_panel.reset()
        self.fretboard.clear()
        self._show_visualizer(None)
        
    def _show_chord_builder(self):
        """Show the chord builder visualizer"""
        self._show_visualizer("chord_builder")
        
    def run(self):
        """Run the main application loop"""
        self.root.mainloop()