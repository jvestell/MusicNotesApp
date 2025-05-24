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
            "fretboard": "#2a2a35",
            "correct_note": "#00ff99",  # Green for correct notes
            "incorrect_note": "#ff3366"  # Red for incorrect notes
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
        self.markers = [6, 8, 10, 13]  # Single dots on frets 6, 8, 10, and 13
        self.double_markers = [13]      # Double dots on 13th fret
        
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
        self.explosion_animation = []  # Initialize as empty list
        
        # Note placement state
        self.note_placement_mode = False
        self.placed_notes = []  # List of (string_idx, fret, note, is_correct) tuples
        self.target_notes = []  # List of notes that should be placed
        self.validation_mode = False  # Whether to validate placed notes
        
        # Drag and drop state
        self.drag_data = {
            "item": None,
            "x": 0,
            "y": 0,
            "note": None
        }
        
        # Set up the canvas
        self.bind("<Configure>", self._on_resize)
        
        # Bind mouse events
        self.bind("<Button-1>", self._on_click)
        self.bind("<Motion>", self._on_hover)
        
        # Bind drag and drop events
        self.bind("<ButtonPress-1>", self._on_drag_start)
        self.bind("<B1-Motion>", self._on_drag_motion)
        self.bind("<ButtonRelease-1>", self._on_drag_release)
        
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
        # Clear everything first
        self.clear()
        
        # Set new chord
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
        
        # Draw all notes at original size first
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
        # Clear all existing notes first
        self.delete("note")  # Delete all note-related items
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Calculate spacing
        string_spacing = height / (self.strings + 1)
        fret_spacing = width / (self.frets + 1)
        
        # Draw all notes
        for string_idx, fret, note, is_correct in self.placed_notes:
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
            
            # Choose color based on validation
            if self.validation_mode:
                color = self.colors["correct_note"] if is_correct else self.colors["incorrect_note"]
            else:
                color = self.colors["accent1"]
            
            # Draw note indicator with tags for easy management
            self.create_oval(x-15, y-15, x+15, y+15, 
                           fill=color, outline="",
                           tags=("note", "note_circle"))
                           
            self.create_text(x, y, text=note_name, 
                           fill=self.colors["bg_dark"],
                           font=("Orbitron", 10, "bold"),
                           tags=("note", "note_text"))

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
        self.explosion_animation = []  # Reset to empty list
        
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
                width=2,
                tags=("explosion",)
            )
            if particle:  # Only append if particle was created successfully
                self.explosion_animation.append(particle)
            
            # Animate particle
            self.after(50 * i, lambda p=particle: self.delete(p))
        
        # Clear explosion animation after all particles are gone
        self.after(50 * num_particles, lambda: setattr(self, 'explosion_animation', []))
        
    def set_random_triad_position(self):
        """Set a random position for the current chord's triad"""
        if not self.current_chord:
            return
            
        # Get all possible positions for the triad
        triad = self.current_chord.get_triad()
        triad_names = [note.name for note in triad]
        
        # Find all valid positions where the triad can be played within 4 frets
        valid_positions = []
        lower_string_positions = []  # Positions that use lower strings (E, A, D)
        
        for start_fret in range(self.frets - 3):  # -3 to ensure we have 4 frets available
            # Check if we can play the triad in this position
            triad_notes = []
            uses_lower_strings = False
            
            # First try to find positions on lower strings (E, A, D)
            for string_idx in [5, 4, 3]:  # E, A, D strings (0-based index)
                open_note = Note(self.tuning[string_idx])
                for fret in range(start_fret, start_fret + 4):
                    fretted_note = open_note.transpose(fret)
                    if fretted_note.name in triad_names:
                        triad_notes.append((string_idx, fret))
                        uses_lower_strings = True
                        if len(triad_notes) == 3:  # Found all triad notes
                            if self._is_playable_triad(triad_notes):
                                if uses_lower_strings:
                                    lower_string_positions.append(triad_notes)
                                else:
                                    valid_positions.append(triad_notes)
                            break
                    if len(triad_notes) == 3:
                        break
            
            # If we didn't find a position on lower strings, try all strings
            if len(triad_notes) < 3:
                triad_notes = []  # Reset for full search
                for string_idx in range(self.strings):
                    open_note = Note(self.tuning[string_idx])
                    for fret in range(start_fret, start_fret + 4):
                        fretted_note = open_note.transpose(fret)
                        if fretted_note.name in triad_names:
                            triad_notes.append((string_idx, fret))
                            if len(triad_notes) == 3:  # Found all triad notes
                                if self._is_playable_triad(triad_notes):
                                    valid_positions.append(triad_notes)
                                break
                        if len(triad_notes) == 3:
                            break
        
        # Select a position with a balanced distribution
        import random
        if lower_string_positions and valid_positions:
            # Combine all positions
            all_positions = lower_string_positions + valid_positions
            # Give lower string positions a 40% chance of being selected
            if random.random() < 0.4:
                new_position = random.choice(lower_string_positions)
            else:
                # 60% chance to pick from all positions
                new_position = random.choice(all_positions)
        elif lower_string_positions:
            new_position = random.choice(lower_string_positions)
        elif valid_positions:
            new_position = random.choice(valid_positions)
        else:
            new_position = None
        
        if new_position:
            # Store old position for transition
            old_position = self.current_position
            
            # Update current position
            self.current_position = new_position
            
            # Update highlighted notes with the new position
            self.highlighted_notes = new_position
            
            # Redraw with transition effect
            self._transition_triad_position(old_position, new_position)

    def _is_playable_triad(self, triad_notes):
        """Check if a triad position is physically playable"""
        if not triad_notes or len(triad_notes) != 3:
            return False
        
        # Get the frets and strings
        frets = [fret for _, fret in triad_notes]
        strings = [string for string, _ in triad_notes]
        
        # Check if frets are within 4 frets of each other
        if max(frets) - min(frets) > 4:
            return False
        
        # Check if strings are adjacent or within reasonable span
        if max(strings) - min(strings) > 3:
            return False
        
        return True

    def _transition_triad_position(self, old_position, new_position):
        """Handle the visual transition between triad positions"""
        # Clear any existing explosion animation
        if self.explosion_animation:
            for item in self.explosion_animation:
                self.delete(item)
        self.explosion_animation = []  # Reset to empty list
        
        # First, clear all highlighted notes
        self.delete("highlight")
        
        # If there was an old position, fade it out
        if old_position:
            for string_idx, fret in old_position:
                # Calculate position
                width = self.winfo_width()
                height = self.winfo_height()
                string_spacing = height / (self.strings + 1)
                fret_spacing = width / (self.frets + 1)
                
                y = (string_idx + 1) * string_spacing
                x = (fret + 0.5) * fret_spacing if fret > 0 else fret_spacing / 2
                
                # Create fade out effect
                note = self.create_oval(x-10, y-10, x+10, y+10,
                                      fill=self.colors["accent1"],
                                      outline="",
                                      tags=("transition", "fade_out"))
                if note:  # Only append if note was created successfully
                    self.explosion_animation.append(note)
                
                # Fade out animation
                for i in range(5):
                    self.after(100 * i, lambda n=note, s=i: 
                        self.itemconfig(n, fill=self.colors["bg_dark"]))
                
                # Delete the fade out note after animation
                self.after(500, lambda n=note: self.delete(n))
        
        # Then, animate the new position
        if new_position:
            # Clear any existing transition effects
            self.delete("transition")
            
            for string_idx, fret in new_position:
                # Calculate position
                width = self.winfo_width()
                height = self.winfo_height()
                string_spacing = height / (self.strings + 1)
                fret_spacing = width / (self.frets + 1)
                
                y = (string_idx + 1) * string_spacing
                x = (fret + 0.5) * fret_spacing if fret > 0 else fret_spacing / 2
                
                # Create grow effect
                for i in range(5):
                    size = 10 + (i * 3)  # Grow from 10 to 22
                    self.after(50 * i, lambda x=x, y=y, s=size: 
                        self._draw_highlighted_note(x, y, s))
        
        # Finally, redraw all notes to ensure proper state
        self.after(250, self._draw_notes)

    def _draw_highlighted_note(self, x, y, size):
        """Draw a highlighted note with the specified size"""
        # Delete any existing transition effects at this position
        self.delete("transition")
        
        # Draw a larger background circle for glow effect
        self.create_oval(x-size*1.2, y-size*1.2, x+size*1.2, y+size*1.2,
                        fill=self.colors["accent1"], outline="",
                        tags=("transition", "glow"))
                        
        # Draw actual note
        self.create_oval(x-size, y-size, x+size, y+size,
                        fill=self.colors["bg_dark"], outline="",
                        tags=("transition", "note_circle"))
                        
        # Get the note name at this position
        note_info = self._get_note_at_position(x, y)
        if note_info:
            string_idx, fret = note_info
            note_name = self._get_note_name(string_idx, fret)
            self.create_text(x, y, text=note_name,
                            fill=self.colors["accent1"],
                            font=("Orbitron", 12, "bold"),
                            tags=("transition", "note_text"))

    def _on_drag_start(self, event):
        """Handle the start of a drag operation"""
        # Check if we're in note placement mode
        if not hasattr(self, 'note_placement_mode') or not self.note_placement_mode:
            return
            
        # Get the note being dragged (if any)
        if hasattr(event, 'note'):
            self.drag_data["note"] = event.note
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            # Create a visual indicator for the dragged note
            self.drag_data["item"] = self.create_oval(
                event.x-15, event.y-15, event.x+15, event.y+15,
                fill=self.colors["accent1"],
                outline=self.colors["accent2"],
                width=2,
                tags=("drag",)
            )
            
            # Add note text
            self.create_text(
                event.x, event.y,
                text=str(self.drag_data["note"].name),
                fill=self.colors["bg_dark"],
                font=("Orbitron", 10, "bold"),
                tags=("drag",)
            )
            
    def _on_drag_motion(self, event):
        """Handle drag motion"""
        if self.drag_data["item"] is None:
            return
            
        # Calculate the new position
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        # Move the drag indicator
        self.move("drag", dx, dy)
        
        # Update the stored position
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
    def _on_drag_release(self, event):
        """Handle the end of a drag operation"""
        if self.drag_data["item"] is None:
            return
            
        # Get the position where the note was dropped
        note_info = self._get_note_at_position(event.x, event.y)
        
        if note_info and self.drag_data["note"]:
            string_idx, fret = note_info
            
            # Get the actual note at this position
            actual_note = self._get_note_name(string_idx, fret)
            
            # Check if this position already has a note
            for i, (s, f, _, _) in enumerate(self.placed_notes):
                if s == string_idx and f == fret:
                    # Remove the existing note
                    self.placed_notes.pop(i)
                    break
            
            # Determine if the note is correct (in validation mode)
            is_correct = True
            if self.validation_mode and self.target_notes:
                target_names = {note.name for note in self.target_notes}
                is_correct = actual_note in target_names
            
            # Add the new note
            self.placed_notes.append((string_idx, fret, self.drag_data["note"], is_correct))
            
            # Redraw the fretboard
            self._draw_notes()
            
        # Clean up the drag indicator
        self.delete("drag")
        self.drag_data = {"item": None, "x": 0, "y": 0, "note": None}

    def set_note_placement_mode(self, enabled: bool, validation_mode: bool = False):
        """Enable or disable note placement mode"""
        self.note_placement_mode = enabled
        self.validation_mode = validation_mode
        if not enabled:
            # Clean up any existing drag operation
            self.delete("drag")
            self.drag_data = {"item": None, "x": 0, "y": 0, "note": None}
            # Clear placed notes if not in validation mode
            if not self.validation_mode:
                self.placed_notes = []
                self.target_notes = []
                self._draw_fretboard()
                self._draw_notes()

    def set_target_notes(self, notes: List[Note]):
        """Set the target notes for validation"""
        self.target_notes = notes
        # Revalidate all placed notes
        self._validate_placed_notes()
        self._draw_notes()

    def _validate_placed_notes(self):
        """Validate all placed notes against target notes"""
        if not self.validation_mode or not self.target_notes:
            return

        # Convert target notes to a set of note names for easy lookup
        target_names = {note.name for note in self.target_notes}
        
        # Update validation status for each placed note
        validated_notes = []
        for string_idx, fret, note, _ in self.placed_notes:
            # Get the actual note at this position
            actual_note = self._get_note_name(string_idx, fret)
            # Check if this note is in the target set
            is_correct = actual_note in target_names
            validated_notes.append((string_idx, fret, note, is_correct))
        
        self.placed_notes = validated_notes

    def clear_placed_notes(self):
        """Clear all manually placed notes"""
        self.placed_notes = []
        self._draw_fretboard()
        self._draw_notes()

    def get_placement_score(self) -> Tuple[int, int]:
        """Get the current score (correct notes, total notes)"""
        if not self.validation_mode or not self.target_notes:
            return 0, 0
            
        correct_count = sum(1 for _, _, _, is_correct in self.placed_notes if is_correct)
        total_count = len(self.placed_notes)
        return correct_count, total_count