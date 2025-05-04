"""
Control panel for the fretboard
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable
import logging

from core.music_theory import MusicTheory
from core.note_system import Note

# Configure logging
logger = logging.getLogger(__name__)

class ControlPanel(tk.Frame):
    """Control panel for the fretboard with cyberpunk styling"""
    
    def __init__(self, parent, theory: MusicTheory, colors: Dict, callback: Callable, **kwargs):
        """Initialize the control panel"""
        bg_color = colors["bg_med"]
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.theory = theory
        self.colors = colors
        self.callback = callback
        
        # Track selected highlight type
        self.selected_highlight_type = tk.StringVar(value="")
        
        # Create the UI components
        self._create_widgets()
        
        # Initialize with empty state
        self.reset()
        
    def _create_widgets(self):
        """Create all UI widgets"""
        # Create frames for organizing controls
        self.left_frame = tk.Frame(self, bg=self.colors["bg_med"])
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.right_frame = tk.Frame(self, bg=self.colors["bg_med"])
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Note selection
        self._create_note_selector()
        
        # Chord selection
        self._create_chord_selector()
        
        # Scale selection
        self._create_scale_selector()
        
        # Highlight options
        self._create_highlight_selector()
        
        # Action buttons
        self._create_action_buttons()
        
    def _create_note_selector(self):
        """Create the root note selector"""
        # Frame for root note
        note_frame = tk.LabelFrame(self.left_frame, 
                                  text="ROOT NOTE", 
                                  font=("Orbitron", 10, "bold"),
                                  fg=self.colors["text_secondary"],
                                  bg=self.colors["bg_light"])
        note_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Root note buttons
        self.selected_note = tk.StringVar(value="C")
        
        # Natural notes
        natural_notes = ["C", "D", "E", "F", "G", "A", "B"]
        sharps = ["C#", "D#", "F#", "G#", "A#"]
        
        # Create a grid of note buttons
        for i, note in enumerate(natural_notes):
            btn = self._create_neon_button(note_frame, note, 
                                         lambda n=note: self._on_note_selected(n))
            btn.grid(row=i, column=0, padx=3, pady=3, sticky="ew")
            
        for i, note in enumerate(sharps):
            btn = self._create_neon_button(note_frame, note, 
                                         lambda n=note: self._on_note_selected(n))
            btn.grid(row=i, column=1, padx=3, pady=3, sticky="ew")
            
    def _create_chord_selector(self):
        """Create the chord type selector"""
        # Frame for chord types
        chord_frame = tk.LabelFrame(self.left_frame, 
                                   text="CHORD TYPE", 
                                   font=("Orbitron", 10, "bold"),
                                   fg=self.colors["text_secondary"],
                                   bg=self.colors["bg_light"])
        chord_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Chord type buttons
        self.selected_chord_type = tk.StringVar(value="Major")
        
        chord_types = [
            "Major", "Minor", "7", "maj7", "m7", 
            "sus2", "sus4", "aug", "dim", "9"
        ]
        
        # Create a grid of chord buttons
        for i, chord_type in enumerate(chord_types):
            row = i % 5
            col = i // 5
            btn = self._create_neon_button(chord_frame, chord_type, 
                                         lambda ct=chord_type: self._on_chord_type_selected(ct))
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
            
    def _create_scale_selector(self):
        """Create the scale type selector"""
        # Frame for scale types
        scale_frame = tk.LabelFrame(self.left_frame, 
                                   text="SCALE TYPE", 
                                   font=("Orbitron", 10, "bold"),
                                   fg=self.colors["text_secondary"],
                                   bg=self.colors["bg_light"])
        scale_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Scale type buttons
        self.selected_scale_type = tk.StringVar(value="Major")
        
        scale_types = [
            "Major", "Minor", "Pentatonic Major", "Pentatonic Minor",
            "Blues", "Harmonic Minor", "Melodic Minor", "Dorian",
            "Phrygian", "Lydian", "Mixolydian", "Locrian"
        ]
        
        # Create a grid of scale buttons
        for i, scale_type in enumerate(scale_types):
            row = i % 6
            col = i // 6
            btn = self._create_neon_button(scale_frame, scale_type, 
                                         lambda st=scale_type: self._on_scale_type_selected(st))
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")

        # Add status display frame
        status_frame = tk.LabelFrame(self.left_frame,
                                   text="CURRENT SELECTION",
                                   font=("Orbitron", 10, "bold"),
                                   fg=self.colors["text_secondary"],
                                   bg=self.colors["bg_light"])
        status_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Root note display
        self.root_display = tk.Label(status_frame,
                                   text="Root: C",
                                   font=("Orbitron", 9),
                                   fg=self.colors["text_primary"],
                                   bg=self.colors["bg_light"])
        self.root_display.pack(fill=tk.X, padx=5, pady=2)

        # Chord type display
        self.chord_display = tk.Label(status_frame,
                                    text="Chord: Major",
                                    font=("Orbitron", 9),
                                    fg=self.colors["text_primary"],
                                    bg=self.colors["bg_light"])
        self.chord_display.pack(fill=tk.X, padx=5, pady=2)

        # Scale type display
        self.scale_display = tk.Label(status_frame,
                                    text="Scale: Major",
                                    font=("Orbitron", 9),
                                    fg=self.colors["text_primary"],
                                    bg=self.colors["bg_light"])
        self.scale_display.pack(fill=tk.X, padx=5, pady=2)

        # Highlight display
        self.highlight_display = tk.Label(status_frame,
                                        text="Highlight: All",
                                        font=("Orbitron", 9),
                                        fg=self.colors["text_primary"],
                                        bg=self.colors["bg_light"])
        self.highlight_display.pack(fill=tk.X, padx=5, pady=2)

        # Scale notes display
        self.scale_notes_display = tk.Label(status_frame,
                                          text="Scale Notes: C D E F G A B",
                                          font=("Orbitron", 9),
                                          fg=self.colors["text_primary"],
                                          bg=self.colors["bg_light"],
                                          wraplength=150)
        self.scale_notes_display.pack(fill=tk.X, padx=5, pady=2)
            
    def _create_highlight_selector(self):
        """Create the highlight options"""
        # Frame for highlighting
        highlight_frame = tk.LabelFrame(self.right_frame, 
                                      text="HIGHLIGHT", 
                                      font=("Orbitron", 10, "bold"),
                                      fg=self.colors["text_secondary"],
                                      bg=self.colors["bg_light"])
        highlight_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Highlight buttons
        self.highlight_buttons = {}  # Store references to highlight buttons
        highlight_options = [
            ("Triad", "triad"),
            ("7th", "seventh"),
            ("Root", "root"),
            ("All", "all")
        ]
        
        for i, (text, value) in enumerate(highlight_options):
            btn = self._create_neon_button(highlight_frame, text, 
                                         lambda v=value: self._on_highlight_selected(v))
            btn.pack(fill=tk.X, padx=3, pady=3)
            self.highlight_buttons[value] = btn
            # Set initial state
            if value == "all":
                btn.config(bg=self.colors["accent1"])
            
    def _create_action_buttons(self):
        """Create action buttons"""
        # Frame for actions
        action_frame = tk.LabelFrame(self.right_frame, 
                                    text="ACTIONS", 
                                    font=("Orbitron", 10, "bold"),
                                    fg=self.colors["text_secondary"],
                                    bg=self.colors["bg_light"])
        action_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Action buttons
        actions = [
            ("Show Chord", self._show_chord),
            ("Show Scale", self._show_scale),
            ("Play Sound", self._play_sound),
            ("Clear", self._clear)
        ]
        
        for text, command in actions:
            btn = self._create_neon_button(action_frame, text, command)
            btn.pack(fill=tk.X, padx=3, pady=3)
            
    def _create_neon_button(self, parent, text, command):
        """Create a neon-styled button"""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            relief=tk.RAISED,
            borderwidth=2,
            font=("Orbitron", 9),
            bg=self.colors["bg_dark"],
            fg=self.colors["text_primary"],
            activebackground=self.colors["accent1"],
            activeforeground=self.colors["bg_dark"],
            width=12,
            height=1,
            padx=5,
            pady=3
        )
        
        # Add hover effects
        button.bind("<Enter>", lambda e, b=button: self._on_button_hover(b, True))
        button.bind("<Leave>", lambda e, b=button: self._on_button_hover(b, False))
        
        return button
        
    def _on_button_hover(self, button, is_hover):
        """Handle button hover effects"""
        if is_hover:
            button.config(bg=self.colors["bg_light"])
        else:
            button.config(bg=self.colors["bg_dark"])
            
    def _on_note_selected(self, note):
        """Handle root note selection"""
        self.selected_note.set(note)
        self.root_display.config(text=f"Root: {note}")
        
        # Only update scale notes if a scale type is selected
        if self.selected_scale_type.get():
            self._update_scale_notes()
            
        # Update display if a chord or scale is active
        if self.selected_chord_type.get():
            self._show_chord()
        elif self.selected_scale_type.get():
            self._show_scale()
            
    def _on_chord_type_selected(self, chord_type: str):
        """Handle chord type selection"""
        # Update the selected chord type
        self.selected_chord_type.set(chord_type)
        
        # Update the display
        self.chord_display.config(text=f"Chord: {chord_type}")
        
        # Update button states
        for value, btn in self.highlight_buttons.items():
            if value == chord_type:
                btn.config(bg=self.colors["accent1"])
            else:
                btn.config(bg=self.colors["bg_dark"])
        
        # If we have a root note selected, create and display the chord
        if self.selected_note.get():
            try:
                root_note = Note(self.selected_note.get())
                chord = self.theory.get_chord(root_note, chord_type)
                self.callback("chord_changed", {"chord": chord})
            except Exception as e:
                logger.error(f"Error creating chord: {e}")
                self.chord_display.config(text="Error creating chord")
        
    def _on_scale_type_selected(self, scale_type):
        """Handle scale type selection"""
        self.selected_scale_type.set(scale_type)
        self.scale_display.config(text=f"Scale: {scale_type}")
        self._update_scale_notes()
        self._show_scale()
        
    def _on_highlight_selected(self, highlight_type):
        """Handle highlight selection"""
        # Update the selected highlight type
        self.selected_highlight_type.set(highlight_type)
        
        # Update the display
        self.highlight_display.config(text=f"Highlight: {highlight_type.capitalize()}")
        
        # Update button states
        for value, btn in self.highlight_buttons.items():
            if value == highlight_type:
                btn.config(bg=self.colors["accent1"])
            else:
                btn.config(bg=self.colors["bg_dark"])
        
        # Only trigger highlight callback if we have an active chord or scale
        if self.selected_chord_type.get() or self.selected_scale_type.get():
            self.callback("highlight_changed", {"type": highlight_type})
        
    def _show_chord(self):
        """Show the selected chord"""
        if not self.selected_note.get():
            return  # Prevent invalid note format error
        root_note = Note(self.selected_note.get() + "4")  # Default to octave 4
        chord_type = self.selected_chord_type.get()
        try:
            chord = self.theory.get_chord(root_note, chord_type)
            self.callback("chord_changed", {"chord": chord})
        except ValueError as e:
            print(f"Error: {e}")
            
    def _show_scale(self):
        """Show the selected scale"""
        if not self.selected_note.get():
            return  # Prevent invalid note format error
        root_note = Note(self.selected_note.get() + "4")  # Default to octave 4
        scale_type = self.selected_scale_type.get()
        try:
            scale = self.theory.get_scale(root_note, scale_type)
            self.callback("scale_changed", {"scale": scale})
        except ValueError as e:
            print(f"Error: {e}")
            
    def _play_sound(self):
        """Play the sound of the current chord or scale"""
        # This would be implemented with the audio engine
        pass
        
    def _clear(self):
        """Clear the fretboard"""
        # Clear the fretboard
        self.callback("clear", {})
        
        # Reset all displays to empty state
        self.root_display.config(text="Root: ")
        self.chord_display.config(text="Chord: ")
        self.scale_display.config(text="Scale: ")
        self.highlight_display.config(text="Highlight: ")
        self.scale_notes_display.config(text="Scale Notes: ")
        
        # Reset selected values
        self.selected_note.set("")
        self.selected_chord_type.set("")
        self.selected_scale_type.set("")
        self.selected_highlight_type.set("")
        
        # Reset highlight buttons to default state
        for value, btn in self.highlight_buttons.items():
            btn.config(bg=self.colors["bg_dark"])
        
    def reset(self):
        """Reset the control panel to defaults"""
        # Reset all selected values
        self.selected_note.set("")
        self.selected_chord_type.set("")
        self.selected_scale_type.set("")
        self.selected_highlight_type.set("")
        
        # Reset all displays
        self.root_display.config(text="Root: ")
        self.chord_display.config(text="Chord: ")
        self.scale_display.config(text="Scale: ")
        self.highlight_display.config(text="Highlight: ")
        self.scale_notes_display.config(text="Scale Notes: ")
        
        # Reset highlight buttons
        for value, btn in self.highlight_buttons.items():
            btn.config(bg=self.colors["bg_dark"])
            
        # Clear the fretboard
        self.callback("clear", {})
        
    def _update_scale_notes(self):
        """Update the scale notes display"""
        try:
            # Only proceed if we have both a root note and scale type
            if not self.selected_note.get() or not self.selected_scale_type.get():
                self.scale_notes_display.config(text="Scale Notes: ")
                return
                
            root_note = Note(self.selected_note.get() + "4")
            scale_type = self.selected_scale_type.get()
            scale = self.theory.get_scale(root_note, scale_type)
            
            # Format scale notes with proper spacing and highlighting
            scale_notes = []
            for note in scale.notes:
                # Add root note with special formatting
                if note.name == root_note.name:
                    scale_notes.append(f"*{note.name}*")
                else:
                    scale_notes.append(note.name)
            
            # Join notes with proper spacing
            scale_notes_str = " ".join(scale_notes)
            self.scale_notes_display.config(text=f"Scale Notes: {scale_notes_str}")
        except Exception as e:
            print(f"Error updating scale notes: {e}")
            self.scale_notes_display.config(text="Scale Notes: ")