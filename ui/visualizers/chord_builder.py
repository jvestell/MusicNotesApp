"""
Chord construction visualizer with cyberpunk theme
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Dict, List, Optional

from core.music_theory import MusicTheory
from core.chord_system import Chord

class ChordBuilderVisualizer(tk.Frame):
    """Visualizer that shows how chords are constructed from intervals"""
    
    def __init__(self, parent, theory: MusicTheory, colors: Dict, **kwargs):
        """Initialize the chord builder visualizer"""
        bg_color = colors["bg_med"]
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.theory = theory
        self.colors = colors
        self.current_chord = None
        
        # Create the UI components
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all UI widgets"""
        # Title label
        title = tk.Label(self, 
                       text="CHORD CONSTRUCTION", 
                       font=("Orbitron", 16, "bold"),
                       fg=self.colors["accent2"],
                       bg=self.colors["bg_dark"],
                       padx=10,
                       pady=5)
        title.pack(fill=tk.X, pady=10)
        
        # Main content frame
        content_frame = tk.Frame(self, bg=self.colors["bg_dark"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Circle of intervals
        self.circle_frame = tk.Frame(content_frame, bg=self.colors["bg_dark"])
        self.circle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.circle_canvas = tk.Canvas(self.circle_frame, 
                                    bg=self.colors["bg_dark"],
                                    highlightthickness=0,
                                    height=400,
                                    width=400)
        self.circle_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Chord formula and explanation
        self.info_frame = tk.Frame(content_frame, bg=self.colors["bg_dark"])
        self.info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chord name display
        self.chord_name = tk.Label(self.info_frame, 
                               text="Select a chord", 
                               font=("Orbitron", 14, "bold"),
                               fg=self.colors["text_primary"],
                               bg=self.colors["bg_dark"])
        self.chord_name.pack(pady=10)
        
        # Chord formula display
        formula_frame = tk.LabelFrame(self.info_frame, 
                                   text="CHORD FORMULA", 
                                   font=("Orbitron", 10, "bold"),
                                   fg=self.colors["text_secondary"],
                                   bg=self.colors["bg_light"])
        formula_frame.pack(fill=tk.X, pady=10)
        
        self.formula_display = tk.Label(formula_frame, 
                                     text="", 
                                     font=("Orbitron", 12),
                                     fg=self.colors["accent1"],
                                     bg=self.colors["bg_light"],
                                     padx=10,
                                     pady=5)
        self.formula_display.pack(fill=tk.X, pady=5)
        
        # Intervals explanation
        intervals_frame = tk.LabelFrame(self.info_frame, 
                                     text="INTERVALS", 
                                     font=("Orbitron", 10, "bold"),
                                     fg=self.colors["text_secondary"],
                                     bg=self.colors["bg_light"])
        intervals_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.intervals_text = tk.Text(intervals_frame, 
                                   font=("Orbitron", 10),
                                   fg=self.colors["text_primary"],
                                   bg=self.colors["bg_light"],
                                   height=8,
                                   wrap=tk.WORD,
                                   padx=10,
                                   pady=5)
        self.intervals_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar for the text
        scrollbar = ttk.Scrollbar(self.intervals_text, 
                                command=self.intervals_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.intervals_text.config(yscrollcommand=scrollbar.set)
        
        # Make the text widget read-only
        self.intervals_text.config(state=tk.DISABLED)
        
        # Bind resize event
        self.circle_canvas.bind("<Configure>", self._on_resize)
        
        self.static_items = []  # Store static canvas item IDs
        self.chord_items = []   # Store dynamic chord highlight item IDs
        
    def _on_resize(self, event):
        """Handle canvas resize event"""
        self._draw_interval_circle()
        if self.current_chord:
            self._draw_chord_intervals(self.current_chord)
            
    def _draw_interval_circle(self):
        """Draw the circle of intervals (static, only once unless size changes)"""
        # Remove previous static items
        for item in getattr(self, 'static_items', []):
            self.circle_canvas.delete(item)
        self.static_items = []

        # Get canvas dimensions
        width = self.circle_canvas.winfo_width()
        height = self.circle_canvas.winfo_height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2.5

        # Draw outer circle
        self.static_items.append(
            self.circle_canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                outline=self.colors["grid_line"],
                width=2
            )
        )
        # Draw center point
        self.static_items.append(
            self.circle_canvas.create_oval(
                center_x - 5, center_y - 5,
                center_x + 5, center_y + 5,
                fill=self.colors["text_primary"],
                outline=""
            )
        )
        # Draw the 12 semitones
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        for i in range(12):
            angle = math.radians(i * 30 - 90)  # Start at top (C)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            # Draw connection line
            self.static_items.append(
                self.circle_canvas.create_line(
                    center_x, center_y, x, y,
                    fill=self.colors["grid_line"],
                    width=1
                )
            )
            # Draw semitone marker
            self.static_items.append(
                self.circle_canvas.create_oval(
                    x - 8, y - 8, x + 8, y + 8,
                    fill=self.colors["bg_light"],
                    outline=self.colors["text_primary"]
                )
            )
            # Add semitone label
            self.static_items.append(
                self.circle_canvas.create_text(
                    x, y,
                    text=notes[i],
                    fill=self.colors["text_primary"],
                    font=("Orbitron", 9)
                )
            )

    def _clear_chord_highlights(self):
        for item in getattr(self, 'chord_items', []):
            self.circle_canvas.delete(item)
        self.chord_items = []

    def _draw_chord_intervals(self, chord: Chord):
        """Draw the chord intervals on the circle (dynamic highlights only)"""
        self._draw_interval_circle()  # Ensure static items are present
        self._clear_chord_highlights()
        self.chord_items = []

        # Get canvas dimensions
        width = self.circle_canvas.winfo_width()
        height = self.circle_canvas.winfo_height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2.5
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        root_index = notes.index(chord.root.name)

        # Add chord root note name (moved further up to avoid overlap)
        self.chord_items.append(
            self.circle_canvas.create_text(
                center_x, center_y - radius - 65,  # Increased from -45 to -65
                text=f"Root: {chord.root.name}",
                fill=self.colors["accent2"],
                font=("Orbitron", 14, "bold")  # Increased font size from 12 to 14
            )
        )
        # Draw chord tones
        for i, semitones in enumerate(chord.formula):
            angle = math.radians(((semitones + root_index) % 12) * 30 - 90)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            # Draw highlighted connection line
            self.chord_items.append(
                self.circle_canvas.create_line(
                    center_x, center_y, x, y,
                    fill=self.colors["accent1"] if i > 0 else self.colors["accent2"],
                    width=3
                )
            )
            # Draw chord tone marker (larger than the regular markers)
            color = self.colors["accent2"] if i == 0 else self.colors["accent1"]
            self.chord_items.append(
                self.circle_canvas.create_oval(
                    x - 12, y - 12, x + 12, y + 12,
                    fill=color,
                    outline=self.colors["bg_dark"]
                )
            )
            # Get note name
            note_name = chord.notes[i].name if i < len(chord.notes) else "?"
            # Add chord tone label
            self.chord_items.append(
                self.circle_canvas.create_text(
                    x, y,
                    text=note_name,
                    fill=self.colors["bg_dark"],
                    font=("Orbitron", 9, "bold")
                )
            )
            # Add interval name (outside the circle)
            interval_name = self._get_interval_name(semitones)
            outer_x = center_x + (radius + 25) * math.cos(angle)
            outer_y = center_y + (radius + 25) * math.sin(angle)
            self.chord_items.append(
                self.circle_canvas.create_text(
                    outer_x, outer_y,
                    text=interval_name,
                    fill=self.colors["text_secondary"],
                    font=("Orbitron", 10)
                )
            )

    def update_chord(self, chord: Chord):
        """Update the visualizer with a new chord"""
        self.current_chord = chord
        # Only update chord name display if changed
        if self.chord_name.cget("text") != chord.name:
            self.chord_name.config(text=chord.name)
        # Update formula display only if changed
        formula_text = self._get_formula_text(chord)
        if self.formula_display.cget("text") != formula_text:
            self.formula_display.config(text=formula_text)
        # Update intervals explanation only if changed
        interval_explanation = self._get_interval_explanation(chord)
        current_text = self.intervals_text.get("1.0", "end-1c")
        if current_text != interval_explanation:
            self.intervals_text.config(state=tk.NORMAL)
            self.intervals_text.delete(1.0, tk.END)
            self.intervals_text.insert(tk.END, interval_explanation)
            self.intervals_text.config(state=tk.DISABLED)
        # Draw the chord on the interval circle
        self._draw_chord_intervals(chord)
        
    def _get_formula_text(self, chord: Chord) -> str:
        """Get a readable formula for the chord"""
        # Convert semitones to interval names
        intervals = []
        for semitones in chord.formula:
            interval_name = self._get_interval_name(semitones)
            intervals.append(interval_name)
            
        return " - ".join(intervals)
        
    def _get_interval_name(self, semitones: int) -> str:
        """Get a human-readable interval name"""
        interval_map = {
            0: "R", 1: "m2", 2: "M2", 3: "m3", 4: "M3",
            5: "P4", 6: "TT", 7: "P5", 8: "m6", 9: "M6",
            10: "m7", 11: "M7", 12: "P8"
        }
        
        return interval_map.get(semitones % 12, str(semitones))
        
    def _get_interval_explanation(self, chord: Chord) -> str:
        """Get an explanation of the chord's intervals"""
        chord_type = chord.chord_type.lower()
        
        explanations = {
            "major": (
                "Major chords have a bright, happy sound.\n\n"
                "Formula: Root - Major 3rd (4 semitones) - Perfect 5th (7 semitones)\n\n"
                "The major 3rd gives this chord its characteristic 'happy' sound."
            ),
            "minor": (
                "Minor chords have a darker, melancholic sound.\n\n"
                "Formula: Root - Minor 3rd (3 semitones) - Perfect 5th (7 semitones)\n\n"
                "The minor 3rd creates the 'sad' quality of this chord."
            ),
            "7": (
                "Dominant 7th chords have a bluesy, unresolved tension.\n\n"
                "Formula: Root - Major 3rd (4) - Perfect 5th (7) - Minor 7th (10)\n\n"
                "The minor 7th creates tension that wants to resolve."
            ),
            "maj7": (
                "Major 7th chords have a lush, jazzy quality.\n\n"
                "Formula: Root - Major 3rd (4) - Perfect 5th (7) - Major 7th (11)\n\n"
                "The major 7th creates a softer, more complex sound than dominant 7ths."
            ),
            "m7": (
                "Minor 7th chords have a smooth, jazzy, contemplative mood.\n\n"
                "Formula: Root - Minor 3rd (3) - Perfect 5th (7) - Minor 7th (10)\n\n"
                "Combines the darkness of minor with the softness of a 7th."
            ),
            "sus2": (
                "Sus2 chords have an open, ambiguous quality.\n\n"
                "Formula: Root - Major 2nd (2) - Perfect 5th (7)\n\n"
                "The 2nd replaces the 3rd, creating neither major nor minor tonality."
            ),
            "sus4": (
                "Sus4 chords have a floating, unresolved quality.\n\n"
                "Formula: Root - Perfect 4th (5) - Perfect 5th (7)\n\n"
                "The 4th replaces the 3rd, creating tension that wants to resolve."
            ),
            "aug": (
                "Augmented chords have a tense, dreamy, ethereal quality.\n\n"
                "Formula: Root - Major 3rd (4) - Augmented 5th (8)\n\n"
                "The raised 5th creates a distinctive tension."
            ),
            "dim": (
                "Diminished chords have an unstable, tense, spooky quality.\n\n"
                "Formula: Root - Minor 3rd (3) - Diminished 5th (6)\n\n"
                "Both the minor 3rd and diminished 5th create its eerie sound."
            ),
            "9": (
                "Dominant 9th chords have a rich, colorful, jazzy quality.\n\n"
                "Formula: Root - Major 3rd (4) - Perfect 5th (7) - Minor 7th (10) - Major 9th (14)\n\n"
                "The added 9th tone adds color to the dominant 7th chord structure."
            )
        }
        
        # Find the closest match for the chord type
        for key, explanation in explanations.items():
            if key in chord_type:
                return explanation
                
        # Default explanation if no match found
        return (
            f"The {chord.chord_type} chord uses the following intervals:\n\n"
            f"{self._get_formula_text(chord)}\n\n"
            "These specific intervals give the chord its unique sonic character."
        )