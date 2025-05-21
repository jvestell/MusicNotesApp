"""
Interactive fretboard visualization with cyberpunk styling
"""

import tkinter as tk
from typing import Dict, List, Optional, Tuple
from core.note_system import Note
from core.chord_system import Chord
from core.scale_system import Scale
import math

class FretboardCanvas(tk.Canvas):
    """Interactive fretboard visualization with cyberpunk styling"""
    
    def __init__(self, parent, bg="#2a2a35", color_scheme=None, **kwargs):
        """Initialize the fretboard canvas"""
        super().__init__(parent, bg=bg, highlightthickness=0, **kwargs)
        
        # Store colors
        self.colors = color_scheme or {
            "text_primary": "#00ccff",
            "text_secondary": "#ff00aa",
            "accent1": "#00ff99",
            "accent2": "#ff3366",
            "grid_line": "#303040",
            "fretboard": "#2a2a35"
        }
        
        # Fretboard configuration
        self.strings = 6  # Standard guitar
        self.frets = 15   # Number of frets to display
        self.tuning = ['E4', 'B3', 'G3', 'D3', 'A2', 'E2']  # Standard tuning (high to low)
        
        # Rendering configuration
        self.string_colors = [
            self.colors["text_primary"],
            self.colors["text_primary"],
            self.colors["text_primary"],
            self.colors["text_primary"],
            self.colors["text_primary"],
            self.colors["text_primary"]
        ]
        
        # Fretboard markers at specific positions
        self.markers = [3, 5, 7, 9, 12, 15, 17, 19, 21, 24]
        self.double_markers = [12, 24]
        
        # Notes currently displayed on the fretboard
        self.displayed_notes = []
        
        # Currently highlighted notes
        self.highlighted_notes = []
        
        # Current chord and scale
        self.current_chord = None
        self.current_scale = None
        
        # Current highlight type
        self.current_highlight_type = ""
        
        # Game mode state
        self.current_position = None  # Current triad position
        self.explosion_animation = None  # Store explosion animation items
        
        # Set up the canvas
        self.bind("<Configure>", self._on_resize)
        
        # Bind mouse events
        self.bind("<Button-1>", self._on_click)
        self.bind("<Motion>", self._on_hover)
        
        # Initial draw
        self._draw_fretboard()
        
    def _on_resize(self, event):
        """Handle canvas resize events"""
        self._draw_fretboard()
        
    def _on_click(self, event):
        """Handle mouse click events"""
        # Get the clicked note
        note_info = self._get_note_at_position(event.x, event.y)
        if note_info:
            string_idx, fret = note_info
            # Play the note sound
            # self._play_note(string_idx, fret)
            
    def _on_hover(self, event):
        """Handle mouse hover events"""
        # Get the hovered note
        note_info = self._get_note_at_position(event.x, event.y)
        if note_info:
            string_idx, fret = note_info
            # Show tooltip with note info
            self._show_note_tooltip(string_idx, fret, event.x, event.y)
        else:
            # Hide tooltip if not hovering over a note
            self._hide_tooltip()
            
    def _get_note_at_position(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Get the string and fret at the given position"""
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Calculate spacing
        string_spacing = height / (self.strings + 1)
        fret_spacing = width / (self.frets + 1)
        
        # Find the closest string
        for string_idx in range(self.strings):
            string_y = (string_idx + 1) * string_spacing
            if abs(y - string_y) < string_spacing / 2:
                # Find the closest fret
                for fret in range(self.frets + 1):
                    fret_x = fret * fret_spacing
                    next_fret_x = (fret + 1) * fret_spacing
                    
                    # For fret 0 (open string)
                    if fret == 0 and x < fret_spacing / 2:
                        return string_idx, 0
                    
                    # For other frets (center of the fret)
                    if fret_x < x < next_fret_x:
                        return string_idx, fret
        
        return None
        
    def _show_note_tooltip(self, string_idx: int, fret: int, x: int, y: int):
        """Show tooltip with note information"""
        # Get the note name
        note = self._get_note_name(string_idx, fret)
        
        # Create tooltip if it doesn't exist
        if not hasattr(self, 'tooltip'):
            self.tooltip = tk.Label(
                self, 
                text=note,
                font=("Orbitron", 10),
                bg=self.colors["accent1"],
                fg=self.colors["bg_dark"],
                padx=5,
                pady=2,
                relief=tk.RAISED,
                borderwidth=1
            )
        else:
            self.tooltip.config(text=note)
            
        # Calculate tooltip position
        self.tooltip.place(x=x + 15, y=y - 15)
        
    def _hide_tooltip(self):
        """Hide the note tooltip"""
        if hasattr(self, 'tooltip'):
            self.tooltip.place_forget()
            
    def _get_note_name(self, string_idx: int, fret: int) -> str:
        """Get the name of the note at the given string and fret"""
        # Get the open string note (using reversed string index)
        open_note = Note(self.tuning[string_idx])
        
        # Transpose by the fret number
        note = open_note.transpose(fret)
        
        return str(note.name)
        
    def _draw_fretboard(self):
        """Draw the fretboard with strings and frets"""
        self.delete("all")  # Clear canvas
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return  # Skip drawing if the canvas is not yet sized
            
        # Calculate spacing
        string_spacing = height / (self.strings + 1)
        fret_spacing = width / (self.frets + 1)
        
        # Draw fretboard background
        self.create_rectangle(0, 0, width, height, 
                            fill=self.colors["fretboard"], outline="")
        
        # Draw the frets
        for i in range(self.frets + 1):
            x = i * fret_spacing
            
            # Adjust line width for the nut (fret 0)
            line_width = 3 if i == 0 else 1
            
            self.create_line(x, string_spacing, x, self.strings * string_spacing, 
                           fill=self.colors["grid_line"], width=line_width)
                           
            # Add fret number (starting from 1)
            if i > 0:
                self.create_text(x, height - 10, 
                               text=str(i), fill=self.colors["text_primary"],
                               font=("Orbitron", 8))
        
        # Draw the strings
        for i in range(self.strings):
            y = (i + 1) * string_spacing
            
            # String thickness (thicker for lower strings)
            thickness = 1 + (self.strings - i) * 0.4
            
            self.create_line(0, y, width, y, 
                           fill=self.string_colors[i], width=thickness)
                           
            # Add string name (tuning)
            self.create_text(10, y - 12, 
                           text=self.tuning[i][0].lower() if i == 0 else self.tuning[i][0], 
                           fill=self.colors["text_secondary"],
                           font=("Orbitron", 9))
        
        # Draw fretboard markers
        for marker in self.markers:
            if marker <= self.frets:
                x = (marker - 0.5) * fret_spacing
                
                # For double markers
                if marker in self.double_markers:
                    y1 = (1.5) * string_spacing
                    y2 = (self.strings - 0.5) * string_spacing
                    
                    self.create_oval(x-5, y1-5, x+5, y1+5, 
                                   fill=self.colors["text_primary"], outline="")
                    self.create_oval(x-5, y2-5, x+5, y2+5, 
                                   fill=self.colors["text_primary"], outline="")
                else:
                    # Single marker
                    y = (self.strings / 2 + 0.5) * string_spacing
                    
                    self.create_oval(x-5, y-5, x+5, y+5, 
                                   fill=self.colors["text_primary"], outline="")
        
        # Redraw any notes that were displayed
        self._redraw_displayed_notes()
        
    def _redraw_displayed_notes(self):
        """Redraw the currently displayed notes"""
        if self.current_chord:
            self.display_chord(self.current_chord)
        elif self.current_scale:
            self.display_scale(self.current_scale)
            
    def display_chord(self, chord: Chord, visual_effect: str = None):
        """Display a chord on the fretboard"""
        self.clear()
        self.current_chord = chord
        self.current_scale = None
        
        # Add chord notes to the display
        for string_idx in range(self.strings):
            # Get the open string note
            open_note = Note(self.tuning[string_idx])
            
            # Find where chord tones appear on this string
            for fret in range(self.frets + 1):
                fretted_note = open_note.transpose(fret)
                
                # Check if this note is in the chord
                for chord_note in chord.notes:
                    if fretted_note.name == chord_note.name:
                        # Add note to display
                        color = self.colors["accent1"]
                        
                        # Highlight the root note
                        if fretted_note.name == chord.root.name:
                            color = self.colors["accent2"]
                            
                        self.displayed_notes.append((string_idx, fret, color))
                        break
        
        # Draw the notes
        self._draw_notes()
        
        # Apply current highlight if any
        if self.current_highlight_type:
            self._apply_highlight(self.current_highlight_type)
            
        # Handle visual effects
        if visual_effect == "explosion":
            self._create_explosion_effect()
        
    def display_scale(self, scale: Scale):
        """Display a scale on the fretboard"""
        self.clear()
        self.current_scale = scale
        self.current_chord = None
        
        # Add scale notes to the display
        scale_notes = []
        for string_idx in range(self.strings):
            # Get the open string note
            open_note = Note(self.tuning[string_idx])
            
            # Find where scale tones appear on this string
            for fret in range(self.frets + 1):
                fretted_note = open_note.transpose(fret)
                
                # Check if this note is in the scale
                for scale_note in scale.notes:
                    if fretted_note.name == scale_note.name:
                        # Add note to display with a different color
                        color = self.colors["text_primary"]
                        
                        # Highlight the root note
                        if fretted_note.name == scale.root.name:
                            color = self.colors["accent2"]
                            
                        scale_notes.append((string_idx, fret, color))
                        break
        
        # Store scale notes
        self.displayed_notes = scale_notes
        
        # Draw the notes
        self._draw_notes()
        
        # Apply current highlight if any
        if self.current_highlight_type:
            self._apply_highlight(self.current_highlight_type)
            
    def _apply_highlight(self, highlight_type: str):
        """Apply the specified highlight type"""
        if highlight_type == "triad":
            self.highlight_triad()
        elif highlight_type == "seventh":
            self.highlight_seventh()
        elif highlight_type == "root":
            self.highlight_root()
        elif highlight_type == "all":
            self.highlight_all()
        
    def clear(self):
        """Clear all displayed notes"""
        self.displayed_notes = []
        self.highlighted_notes = []
        self.current_chord = None
        self.current_scale = None
        self._draw_fretboard()
        
    def highlight_triad(self):
        """Highlight only the triad notes of the current chord or scale"""
        if not (self.current_chord or self.current_scale):
            return
            
        # Get the triad notes
        if self.current_chord:
            # For chords, get the actual triad from the chord
            triad = self.current_chord.get_triad()
            triad_names = [note.name for note in triad]
        else:
            # For scales, create a major triad from the root note
            root = self.current_scale.root
            triad_names = [
                root.name,  # Root
                root.transpose(4).name,  # Major third
                root.transpose(7).name   # Perfect fifth
            ]
        
        # Clear previous highlights
        self.highlighted_notes = []
        
        # Add highlighted notes
        for string_idx, fret, color in self.displayed_notes:
            # Get the note at this position
            open_note = Note(self.tuning[string_idx])
            fretted_note = open_note.transpose(fret)
            
            # Check if this note is in the triad
            if fretted_note.name in triad_names:
                self.highlighted_notes.append((string_idx, fret))
                
        # Redraw with highlights
        self._draw_notes()
        
    def highlight_seventh(self):
        """Highlight the seventh of the current chord or scale"""
        if not (self.current_chord or self.current_scale):
            return
            
        # Get the seventh note
        if self.current_chord:
            # For chords, check if it has a seventh
            if len(self.current_chord.notes) >= 4:
                seventh = self.current_chord.notes[3]  # Fourth note is the seventh
            else:
                # If chord doesn't have a seventh, create one from the root
                root = self.current_chord.root
                # For major chords, use major seventh (11 semitones)
                # For minor/diminished chords, use minor seventh (10 semitones)
                if "major" in self.current_chord.chord_type.lower():
                    seventh = root.transpose(11)  # Major seventh
                else:
                    seventh = root.transpose(10)  # Minor seventh
        else:
            # For scales, create a dominant seventh from the root note
            root = self.current_scale.root
            # For major scales, use major seventh
            # For minor scales, use minor seventh
            if "major" in self.current_scale.scale_type.lower():
                seventh = root.transpose(11)  # Major seventh
            else:
                seventh = root.transpose(10)  # Minor seventh
        
        # Clear previous highlights
        self.highlighted_notes = []
        
        # Add highlighted notes
        for string_idx, fret, color in self.displayed_notes:
            # Get the note at this position
            open_note = Note(self.tuning[string_idx])
            fretted_note = open_note.transpose(fret)
            
            # Check if this note is the seventh
            if fretted_note.name == seventh.name:
                self.highlighted_notes.append((string_idx, fret))
                
        # Redraw with highlights
        self._draw_notes()
        
    def highlight_root(self):
        """Highlight only the root note of the current chord or scale"""
        if not (self.current_chord or self.current_scale):
            return
            
        # Get the root note
        root = self.current_chord.root if self.current_chord else self.current_scale.root
        
        # Clear previous highlights
        self.highlighted_notes = []
        
        # Add highlighted notes
        for string_idx, fret, color in self.displayed_notes:
            # Get the note at this position
            open_note = Note(self.tuning[string_idx])
            fretted_note = open_note.transpose(fret)
            
            # Check if this note is the root
            if fretted_note.name == root.name:
                self.highlighted_notes.append((string_idx, fret))
                
        # Redraw with highlights
        self._draw_notes()
        
    def highlight_all(self):
        """Highlight all notes of the current chord or scale"""
        if not (self.current_chord or self.current_scale):
            return
            
        # Clear previous highlights
        self.highlighted_notes = []
        
        # Add all displayed notes to highlights
        for string_idx, fret, _ in self.displayed_notes:
            self.highlighted_notes.append((string_idx, fret))
                
        # Redraw with highlights
        self._draw_notes()
        
    def _draw_notes(self):
        """Draw the notes on the fretboard"""
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Calculate spacing
        string_spacing = height / (self.strings + 1)
        fret_spacing = width / (self.frets + 1)
        
        # Draw all notes
        for string_idx, fret, color in self.displayed_notes:
            # Calculate position
            y = (string_idx + 1) * string_spacing
            if fret == 0:
                # Draw open string note
                x = fret_spacing / 2
            else:
                # Draw fretted note
                x = (fret + 0.5) * fret_spacing  # Center between frets
            
            # Get the note name
            note_name = self._get_note_name(string_idx, fret)
            
            # Check if this note is highlighted
            is_highlighted = (string_idx, fret) in self.highlighted_notes
            
            # Draw note indicator
            if is_highlighted:
                # Make highlighted notes glow
                # Draw a larger background circle for glow effect
                self.create_oval(x-12, y-12, x+12, y+12, 
                               fill=color, outline="")
                               
                # Draw actual note
                self.create_oval(x-10, y-10, x+10, y+10, 
                               fill=self.colors["bg_dark"], outline="")
                               
                self.create_text(x, y, text=note_name, 
                               fill=self.colors["accent1"],
                               font=("Orbitron", 9, "bold"))
            else:
                self.create_oval(x-10, y-10, x+10, y+10, 
                               fill=color, outline="")
                               
                self.create_text(x, y, text=note_name, 
                               fill=self.colors["bg_dark"],
                               font=("Orbitron", 9))

    def set_highlight_type(self, highlight_type: str):
        """Set the current highlight type and apply it"""
        self.current_highlight_type = highlight_type
        if self.current_chord or self.current_scale:
            self._apply_highlight(highlight_type)

    def _create_explosion_effect(self):
        """Create an explosion effect when changing chords"""
        # Clear any existing explosion animation
        if self.explosion_animation:
            for item in self.explosion_animation:
                self.delete(item)
        self.explosion_animation = []
        
        # Get canvas dimensions
        width = self.winfo_width()
        height = self.winfo_height()
        center_x = width / 2
        center_y = height / 2
        
        # Create explosion particles
        num_particles = 20
        for i in range(num_particles):
            # Random angle and distance
            angle = (i / num_particles) * 360
            distance = 50 + (i % 3) * 20  # Varying distances
            
            # Calculate end position
            rad = math.radians(angle)
            end_x = center_x + distance * math.cos(rad)
            end_y = center_y + distance * math.sin(rad)
            
            # Create particle
            particle = self.create_line(
                center_x, center_y, end_x, end_y,
                fill=self.colors["accent2"],
                width=2
            )
            self.explosion_animation.append(particle)
            
            # Animate particle
            self.after(50 * i, lambda p=particle: self.delete(p))
            
        # Clear explosion animation after all particles are gone
        self.after(50 * num_particles, lambda: setattr(self, 'explosion_animation', None))
        
    def set_random_triad_position(self):
        """Set a random position for the current chord's triad"""
        if not self.current_chord:
            return
            
        # Get all possible positions for the triad
        triad = self.current_chord.get_triad()
        triad_names = [note.name for note in triad]
        
        # Find all valid positions where the triad can be played within 4 frets
        valid_positions = []
        for start_fret in range(self.frets - 3):  # -3 to ensure we have 4 frets available
            # Check if we can play the triad in this position
            triad_notes = []
            for string_idx in range(self.strings):
                open_note = Note(self.tuning[string_idx])
                for fret in range(start_fret, start_fret + 4):
                    fretted_note = open_note.transpose(fret)
                    if fretted_note.name in triad_names:
                        triad_notes.append((string_idx, fret))
                        if len(triad_notes) == 3:  # Found all triad notes
                            valid_positions.append(triad_notes)
                            break
                if len(triad_notes) == 3:
                    break
                    
        if valid_positions:
            # Select a random position
            import random
            self.current_position = random.choice(valid_positions)
            
            # Update highlighted notes
            self.highlighted_notes = self.current_position
            
            # Redraw with highlights
            self._draw_notes()