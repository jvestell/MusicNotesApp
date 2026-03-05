"""
Interactive fretboard visualization with cyberpunk styling
"""

import tkinter as tk
import threading
from typing import Dict, List, Optional, Tuple
from core.note_system import Note
from core.chord_system import Chord
from core.scale_system import Scale
import math

class FretboardCanvas(tk.Canvas):
    """Interactive fretboard visualization with cyberpunk styling"""
    
    def __init__(self, parent, bg="#2a2a35", color_scheme=None, audio_engine=None, **kwargs):
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
        self.explosion_animation = []  # Initialize as empty list

        # Note placement state
        self.note_placement_mode = False
        self.placed_notes = []  # List of (string_idx, fret, note, is_correct) tuples
        self.target_notes = []  # List of notes that should be placed
        self.validation_mode = False  # Whether to validate placed notes

        # Audio engine (optional)
        self.audio_engine = audio_engine

        # Triad Finder mode
        self.triad_finder_mode = False
        self.triad_finder_target_positions = set()   # {(string_idx, fret), ...}
        self.triad_finder_found_positions = set()    # {(string_idx, fret), ...}
        self.triad_finder_chord_label = ""
        self.triad_finder_callback = None            # callable(event_type, data)

        # Drag and drop state
        self.drag_data = {
            "item": None,
            "x": 0,
            "y": 0,
            "note": None,
            "is_dragging": False
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
        if self.triad_finder_mode:
            self._draw_notes()
        
    def _on_click(self, event):
        """Handle mouse click events"""
        # Get the clicked note
        note_info = self._get_note_at_position(event.x, event.y)
        if note_info:
            string_idx, fret = note_info
            self._play_note(string_idx, fret)
            
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
        
    def _play_note(self, string_idx: int, fret: int):
        """Play the note at the given string and fret position in a background thread"""
        if not self.audio_engine:
            return
        open_note = Note(self.tuning[string_idx])
        note = open_note.transpose(fret)
        threading.Thread(target=self.audio_engine.play_note, args=(note,), daemon=True).start()

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

        for string_idx in range(self.strings):
            open_note = Note(self.tuning[string_idx])
            for fret in range(self.frets + 1):
                fretted_note = open_note.transpose(fret)
                for chord_note in chord.notes:
                    if fretted_note.name == chord_note.name:
                        color = self.colors["accent1"]
                        if fretted_note.name == chord.root.name:
                            color = self.colors["accent2"]
                        self.displayed_notes.append((string_idx, fret, color))
                        break

        # Draw all notes
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
        
        # First draw displayed notes (chord/scale notes) if not in note placement mode
        if not self.note_placement_mode:
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
                
                # If this note is highlighted, draw highlight effect first
                if (string_idx, fret) in self.highlighted_notes:
                    # Draw a larger background circle for glow effect
                    self.create_oval(x-18, y-18, x+18, y+18,
                                   fill=self.colors["accent1"], outline="",
                                   tags=("note", "highlight_glow"))
                    # Draw a slightly smaller circle for the highlight outline
                    self.create_oval(x-17, y-17, x+17, y+17,
                                   fill=self.colors["bg_dark"], outline="",
                                   tags=("note", "highlight_bg"))
                
                # Draw the note circle
                self.create_oval(x-15, y-15, x+15, y+15, 
                               fill=color, outline="",
                               tags=("note", "note_circle"))
                               
                # Draw the note text on top
                self.create_text(x, y, text=note_name, 
                               fill=self.colors["bg_dark"],
                               font=("Orbitron", 10, "bold"),
                               tags=("note", "note_text"))
        
        # Then draw placed notes (in note placement mode)
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
                # In validation mode, only show correct placements
                if is_correct:
                    color = self.colors["correct_note"]
                else:
                    # Skip drawing incorrect notes
                    continue
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

        # Draw triad finder overlay if active
        if self.triad_finder_mode:
            self._draw_triad_finder_overlay(width, height, string_spacing, fret_spacing)

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
        
    # ------------------------------------------------------------------ #
    #  Triad Finder                                                        #
    # ------------------------------------------------------------------ #

    def set_triad_finder_label(self, chord_name: str):
        """Phase 1: show chord name label on fretboard without computing targets."""
        self.triad_finder_mode = True
        self.triad_finder_chord_label = chord_name
        self.triad_finder_target_positions = set()
        self.triad_finder_found_positions = set()
        self.triad_finder_callback = None
        # Clear the fretboard and redraw with just the label
        self.displayed_notes = []
        self.highlighted_notes = []
        self.current_chord = None
        self.current_scale = None
        self.placed_notes = []
        self._draw_fretboard()
        self._draw_notes()

    def start_triad_finder(self, chord, triad_note_names, callback, chord_name=None):
        """Phase 2: compute target positions and begin tracking."""
        self.triad_finder_mode = True
        self.triad_finder_chord_label = chord_name or (chord.name if chord else "")
        self.triad_finder_callback = callback
        self.note_placement_mode = True
        self.triad_finder_found_positions = set()

        # Compute every (string_idx, fret) where the note is a triad note (frets 1-13)
        targets = set()
        for string_idx in range(self.strings):
            for fret in range(1, 14):
                note_name = self._get_note_name(string_idx, fret)
                if note_name in triad_note_names:
                    targets.add((string_idx, fret))
        self.triad_finder_target_positions = targets

        self.placed_notes = []
        self._draw_fretboard()
        self._draw_notes()

    def stop_triad_finder(self):
        """Stop triad finder mode and restore clean fretboard."""
        self.triad_finder_mode = False
        self.triad_finder_target_positions = set()
        self.triad_finder_found_positions = set()
        self.triad_finder_chord_label = ""
        self.triad_finder_callback = None
        self.note_placement_mode = False
        self.placed_notes = []
        self.clear()

    def _draw_triad_finder_overlay(self, width, height, string_spacing, fret_spacing):
        """Draw the chord label and found notes for Triad Finder mode."""
        # Chord label at the top of the canvas
        if self.triad_finder_chord_label:
            self.create_text(
                width / 2, string_spacing * 0.45,
                text=self.triad_finder_chord_label,
                fill=self.colors["text_primary"],
                font=("Orbitron", 18, "bold"),
                anchor=tk.CENTER,
                tags=("note", "tf_label")
            )

        # Draw found positions as green dots
        for string_idx, fret in self.triad_finder_found_positions:
            y = (string_idx + 1) * string_spacing
            x = (fret + 0.5) * fret_spacing
            note_name = self._get_note_name(string_idx, fret)
            # Glow ring
            self.create_oval(x - 18, y - 18, x + 18, y + 18,
                             fill=self.colors["correct_note"], outline="",
                             tags=("note", "tf_found_glow"))
            self.create_oval(x - 17, y - 17, x + 17, y + 17,
                             fill=self.colors["bg_dark"], outline="",
                             tags=("note", "tf_found_bg"))
            # Note dot
            self.create_oval(x - 15, y - 15, x + 15, y + 15,
                             fill=self.colors["correct_note"], outline="",
                             tags=("note", "tf_found_dot"))
            self.create_text(x, y, text=note_name,
                             fill=self.colors["bg_dark"],
                             font=("Orbitron", 10, "bold"),
                             tags=("note", "tf_found_text"))

    def _on_drag_start(self, event):
        """Handle the start of a drag operation"""
        # Check if we're in note placement mode
        if not self.note_placement_mode:
            return
            
        # Get the note being dragged (if any)
        if hasattr(event, 'note'):
            # Clean up any existing drag indicator
            self.delete("drag")
            
            # Store the note and start drag operation
            self.drag_data["note"] = event.note
            self.drag_data["is_dragging"] = True
            self.drag_data["x"] = self.winfo_pointerx() - self.winfo_rootx()
            self.drag_data["y"] = self.winfo_pointery() - self.winfo_rooty()
            
            # Create a visual indicator for the dragged note at the cursor position
            self.drag_data["item"] = self.create_oval(
                self.drag_data["x"]-15, self.drag_data["y"]-15,
                self.drag_data["x"]+15, self.drag_data["y"]+15,
                fill=self.colors["accent1"],
                outline=self.colors["accent2"],
                width=2,
                tags=("drag",)
            )
            
            # Add note text at the cursor position
            self.create_text(
                self.drag_data["x"], self.drag_data["y"],
                text=str(self.drag_data["note"].name),
                fill=self.colors["bg_dark"],
                font=("Orbitron", 10, "bold"),
                tags=("drag",)
            )
            
            # Configure the canvas to track mouse motion
            self.config(cursor="crosshair")
            
    def _on_drag_motion(self, event):
        """Handle drag motion"""
        if not self.drag_data["is_dragging"]:
            return
            
        # Get the cursor position relative to the canvas
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
            
        # Clean up the old drag indicator before creating a new one
        self.delete("drag")
        
        # Create new indicator at current cursor position
        self.drag_data["item"] = self.create_oval(
            x-15, y-15, x+15, y+15,
            fill=self.colors["accent1"],
            outline=self.colors["accent2"],
            width=2,
            tags=("drag",)
        )
        
        # Add note text at current cursor position
        self.create_text(
            x, y,
            text=str(self.drag_data["note"].name),
            fill=self.colors["bg_dark"],
            font=("Orbitron", 10, "bold"),
            tags=("drag",)
        )
        
        # Update the stored position
        self.drag_data["x"] = x
        self.drag_data["y"] = y
        
    def _on_drag_release(self, event):
        """Handle the end of a drag operation"""
        if not self.drag_data["is_dragging"]:
            return
            
        # Reset cursor and drag state
        self.config(cursor="")
        self.drag_data["is_dragging"] = False
            
        # Get the cursor position relative to the canvas
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
        
        # Get the position where the note was dropped
        note_info = self._get_note_at_position(x, y)
        
        if note_info and self.drag_data["note"]:
            string_idx, fret = note_info

            # Triad Finder mode: special validation
            if self.triad_finder_mode:
                if 1 <= fret <= 13:
                    pos = (string_idx, fret)
                    actual_note = self._get_note_name(string_idx, fret)
                    dragged_name = str(self.drag_data["note"].name)
                    if (pos in self.triad_finder_target_positions
                            and pos not in self.triad_finder_found_positions
                            and dragged_name == actual_note):
                        self.triad_finder_found_positions.add(pos)
                        self._play_note(string_idx, fret)
                        self._draw_notes()
                        remaining = len(self.triad_finder_target_positions) - len(self.triad_finder_found_positions)
                        if self.triad_finder_callback:
                            if remaining == 0:
                                self.triad_finder_callback("all_found", {})
                            else:
                                self.triad_finder_callback("note_found", {"remaining": remaining})
                self.delete("drag")
                self.drag_data = {"item": None, "x": 0, "y": 0, "note": None, "is_dragging": False}
                return

            # Get the actual note at this position
            actual_note = self._get_note_name(string_idx, fret)

            # Validate the note placement
            if self.validation_mode:
                # In validation mode, only allow placement if the dragged note matches the actual note
                if str(self.drag_data["note"].name) == actual_note:
                    # Check if this position already has a note
                    for i, (s, f, _, _) in enumerate(self.placed_notes):
                        if s == string_idx and f == fret:
                            # Remove the existing note
                            self.placed_notes.pop(i)
                            break
                    # Add the new note
                    self.placed_notes.append((string_idx, fret, self.drag_data["note"], True))
                    self._play_note(string_idx, fret)
            else:
                # In non-validation mode, allow any placement
                # Check if this position already has a note
                for i, (s, f, _, _) in enumerate(self.placed_notes):
                    if s == string_idx and f == fret:
                        # Remove the existing note
                        self.placed_notes.pop(i)
                        break
                # Add the new note
                self.placed_notes.append((string_idx, fret, self.drag_data["note"], True))
                self._play_note(string_idx, fret)

            # Redraw the fretboard
            self._draw_notes()
            
        # Clean up the drag indicator
        self.delete("drag")
        self.drag_data = {
            "item": None,
            "x": 0,
            "y": 0,
            "note": None,
            "is_dragging": False
        }

    def set_note_placement_mode(self, enabled: bool, validation_mode: bool = False):
        """Enable or disable note placement mode"""
        self.note_placement_mode = enabled
        self.validation_mode = validation_mode
        
        if not enabled:
            # Clean up any existing drag operation
            self.delete("drag")
            self.drag_data = {
                "item": None,
                "x": 0,
                "y": 0,
                "note": None,
                "is_dragging": False
            }
            
            # Store current display state
            current_chord = self.current_chord
            current_scale = self.current_scale
            current_highlight = self.current_highlight_type
            
            # Clear placed notes if not in validation mode
            if not self.validation_mode:
                self.placed_notes = []
                self.target_notes = []
            
            # Redraw the fretboard
            self._draw_fretboard()
            
            # Restore display state
            if current_chord:
                self.display_chord(current_chord)
            elif current_scale:
                self.display_scale(current_scale)
                
            # Restore highlight if any
            if current_highlight:
                self._apply_highlight(current_highlight)
        else:
            # When enabling note placement mode, validate existing notes
            self._validate_placed_notes()
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
            # Check if this note is in the target set AND matches the actual note at this position
            is_correct = (actual_note in target_names) and (str(note.name) == actual_note)
            if is_correct:  # Only keep correct notes
                validated_notes.append((string_idx, fret, note, True))
        
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