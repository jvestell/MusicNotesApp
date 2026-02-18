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
        self.current_position = None  # Current triad position
        self.explosion_animation = []  # Initialize as empty list
        
        # Note placement state
        self.note_placement_mode = False
        self.placed_notes = []  # List of (string_idx, fret, note, is_correct) tuples
        self.target_notes = []  # List of notes that should be placed
        self.validation_mode = False  # Whether to validate placed notes

        # Audio engine (optional)
        self.audio_engine = audio_engine

        # Revolving triads extras
        self.revolving_triads_mode = False  # Suppress full chord map when True
        self.ghost_position = None          # Upcoming triad position shown as ghost
        self._committed_next_position = None  # Position locked in by ghost preview
        self.voice_leading_notes = []       # [(string_idx, fret, label)] connector passage

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
            # In revolving triads mode restore the current triad position
            if self.revolving_triads_mode and self.current_position:
                self.highlighted_notes = list(self.current_position)
                self._draw_notes()
        elif self.current_scale:
            self.display_scale(self.current_scale)
            
    def display_chord(self, chord: Chord, visual_effect: str = None):
        """Display a chord on the fretboard"""
        # Clear everything first
        self.clear()

        # Set new chord
        self.current_chord = chord
        self.current_scale = None

        # In revolving triads mode only the selected triad position is shown;
        # skip populating the full chord map so the fretboard stays clean.
        if not self.revolving_triads_mode:
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
        if self.current_highlight_type and not self.revolving_triads_mode:
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

        # Ghost preview: upcoming triad position (dimmed, dashed outline)
        if self.ghost_position:
            GHOST_FILL = "#1a2a3a"
            GHOST_OUTLINE = "#3a6a9a"
            for string_idx, fret in self.ghost_position:
                y = (string_idx + 1) * string_spacing
                x = (fret + 0.5) * fret_spacing if fret > 0 else fret_spacing / 2
                note_name = self._get_note_name(string_idx, fret)
                self.create_oval(x - 15, y - 15, x + 15, y + 15,
                                 fill=GHOST_FILL,
                                 outline=GHOST_OUTLINE,
                                 width=2,
                                 dash=(4, 3),
                                 tags=("note", "ghost"))
                self.create_text(x, y, text=note_name,
                                 fill=GHOST_OUTLINE,
                                 font=("Orbitron", 9),
                                 tags=("note", "ghost_text"))

        # In revolving triads mode draw the active triad position directly
        if self.revolving_triads_mode and self.highlighted_notes:
            triad_names = (
                {n.name for n in self.current_chord.get_triad()}
                if self.current_chord else set()
            )
            root_name = self.current_chord.root.name if self.current_chord else None
            for string_idx, fret in self.highlighted_notes:
                y = (string_idx + 1) * string_spacing
                x = (fret + 0.5) * fret_spacing if fret > 0 else fret_spacing / 2
                note_name = self._get_note_name(string_idx, fret)
                color = self.colors["accent2"] if note_name == root_name else self.colors["accent1"]
                # Glow ring
                self.create_oval(x - 18, y - 18, x + 18, y + 18,
                                 fill=color, outline="", tags=("note", "triad_glow"))
                self.create_oval(x - 17, y - 17, x + 17, y + 17,
                                 fill=self.colors["bg_dark"], outline="", tags=("note", "triad_bg"))
                # Note dot
                self.create_oval(x - 15, y - 15, x + 15, y + 15,
                                 fill=color, outline="", tags=("note", "triad_dot"))
                self.create_text(x, y, text=note_name,
                                 fill=self.colors["bg_dark"],
                                 font=("Orbitron", 10, "bold"),
                                 tags=("note", "triad_text"))

        # Re-render voice-leading overlay on top
        self._draw_voice_leading()

        # Position / inversion label (revolving triads mode only)
        if self.revolving_triads_mode and self.highlighted_notes and self.current_chord:
            self._draw_position_label(width, height)

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

        # If a position was already committed via the ghost preview, use it directly
        if self._committed_next_position:
            new_position = self._committed_next_position
            self._committed_next_position = None
            old_position = self.current_position
            self.current_position = new_position
            self.highlighted_notes = new_position
            self._transition_triad_position(old_position, new_position)
            return

        triad = self.current_chord.get_triad()
        triad_names = [note.name for note in triad]

        # Build a lookup: for each (string, fret) what triad note does it produce
        # Then enumerate all 3-string combinations within a 4-fret window,
        # one note per string, covering all 3 triad tones.
        import random
        from itertools import permutations

        valid_positions = []
        lower_string_positions = []
        lower_string_set = {3, 4, 5}  # D, A, E (indices high-to-low)

        # For each starting fret window
        for start_fret in range(0, self.frets - 2):
            end_fret = start_fret + 4

            # For each group of 3 adjacent strings
            for top_string in range(self.strings - 2):
                string_group = [top_string, top_string + 1, top_string + 2]

                # Find which frets on each string produce a triad tone
                options = {}  # string_idx -> list of (fret, tone_name)
                for s in string_group:
                    open_note = Note(self.tuning[s])
                    hits = []
                    for fret in range(start_fret, end_fret):
                        name = open_note.transpose(fret).name
                        if name in triad_names:
                            hits.append((fret, name))
                    if hits:
                        options[s] = hits

                if len(options) < 3:
                    continue  # Not all 3 strings have a triad tone in this window

                # Try every combination (one fret choice per string) that
                # covers all 3 distinct triad tones
                for f0, n0 in options[string_group[0]]:
                    for f1, n1 in options[string_group[1]]:
                        for f2, n2 in options[string_group[2]]:
                            if len({n0, n1, n2}) < len(triad_names):
                                continue  # Doesn't cover all triad tones
                            position = [
                                (string_group[0], f0),
                                (string_group[1], f1),
                                (string_group[2], f2),
                            ]
                            if not self._is_playable_triad(position):
                                continue
                            uses_lower = bool(lower_string_set & set(string_group))
                            if uses_lower:
                                lower_string_positions.append(position)
                            else:
                                valid_positions.append(position)

        # Deduplicate
        def pos_key(p):
            return tuple(sorted(p))
        seen = set()
        unique_lower, unique_valid = [], []
        for p in lower_string_positions:
            k = pos_key(p)
            if k not in seen:
                seen.add(k)
                unique_lower.append(p)
        for p in valid_positions:
            k = pos_key(p)
            if k not in seen:
                seen.add(k)
                unique_valid.append(p)

        all_positions = unique_lower + unique_valid
        if not all_positions:
            new_position = None
        elif unique_lower and random.random() < 0.4:
            new_position = random.choice(unique_lower)
        else:
            new_position = random.choice(all_positions)
        
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
        """Draw a single growing note dot during the transition animation"""
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

    # ------------------------------------------------------------------ #
    #  Revolving Triads – ghost preview (Feature 3)                       #
    # ------------------------------------------------------------------ #

    def show_ghost_preview(self, chord):
        """Show a dimmed ghost of the upcoming triad position."""
        triad = chord.get_triad()
        triad_names = [n.name for n in triad]

        import random
        valid = []
        for start_fret in range(0, self.frets - 2):
            end_fret = start_fret + 4
            for top_string in range(self.strings - 2):
                string_group = [top_string, top_string + 1, top_string + 2]
                options = {}
                for s in string_group:
                    open_note = Note(self.tuning[s])
                    hits = []
                    for fret in range(start_fret, end_fret):
                        name = open_note.transpose(fret).name
                        if name in triad_names:
                            hits.append((fret, name))
                    if hits:
                        options[s] = hits
                if len(options) < 3:
                    continue
                for f0, n0 in options[string_group[0]]:
                    for f1, n1 in options[string_group[1]]:
                        for f2, n2 in options[string_group[2]]:
                            if len({n0, n1, n2}) < len(triad_names):
                                continue
                            position = [
                                (string_group[0], f0),
                                (string_group[1], f1),
                                (string_group[2], f2),
                            ]
                            if self._is_playable_triad(position):
                                valid.append(position)

        chosen = random.choice(valid) if valid else None
        self.ghost_position = chosen
        self._committed_next_position = chosen  # Lock in — set_random_triad_position will use this
        self._draw_notes()

    def clear_ghost_preview(self):
        """Remove the ghost visual only. The committed position is preserved for set_random_triad_position to consume."""
        self.ghost_position = None
        self._draw_notes()

    def reset_committed_position(self):
        """Discard the committed next position (call on game stop/clear)."""
        self._committed_next_position = None

    # ------------------------------------------------------------------ #
    #  Revolving Triads – voice-leading connector (Feature 1)             #
    # ------------------------------------------------------------------ #

    def show_voice_leading(self, from_position, to_chord):
        """
        Compute and display a stepwise connecting passage from the current
        triad position to the nearest note of the incoming chord.

        Strategy:
        - Use the major scale rooted on the outgoing chord's root note.
        - Stay within a 5-fret window centred on the current hand position.
        - Walk stepwise (scale-step by scale-step) toward the closest
          incoming triad note, capping the passage at 5 notes.
        - Draw each note as a numbered amber dot so the player reads
          them in order.
        """
        self.voice_leading_notes = []
        self.delete("voice_lead")

        if not from_position or not self.current_chord:
            return

        # --- 1. Build the major scale from the outgoing chord root ---
        MAJOR = [0, 2, 4, 5, 7, 9, 11]
        root = self.current_chord.root
        scale_note_names = set()
        for interval in MAJOR:
            scale_note_names.add(root.transpose(interval).name)

        # --- 2. Determine the hand's fret window ---
        frets_used = [f for _, f in from_position if f > 0]
        if frets_used:
            center_fret = sum(frets_used) // len(frets_used)
        else:
            center_fret = 5
        window_lo = max(0, center_fret - 2)
        window_hi = min(self.frets, center_fret + 5)

        # --- 3. Collect all scale notes in the window (not already in triad) ---
        triad_names = {n.name for n in self.current_chord.get_triad()}
        to_triad_names = {n.name for n in to_chord.get_triad()}

        # All candidate positions: (string, fret, note_name, midi)
        candidates = []
        for string_idx in range(self.strings):
            open_note = Note(self.tuning[string_idx])
            for fret in range(window_lo, window_hi + 1):
                note = open_note.transpose(fret)
                if note.name in scale_note_names and note.name not in triad_names:
                    candidates.append((string_idx, fret, note.name, note.midi_number))

        if not candidates:
            return

        # --- 4. Find the target: closest incoming triad note by pitch ---
        # Use the average midi of the current position as "current pitch"
        current_midi_avg = sum(
            Note(self.tuning[s]).transpose(f).midi_number
            for s, f in from_position
        ) / len(from_position)

        # Find the incoming triad note whose pitch is closest to current average
        best_target_midi = None
        best_dist = 9999
        for string_idx in range(self.strings):
            open_note = Note(self.tuning[string_idx])
            for fret in range(window_lo, window_hi + 1):
                note = open_note.transpose(fret)
                if note.name in to_triad_names:
                    dist = abs(note.midi_number - current_midi_avg)
                    if dist < best_dist:
                        best_dist = dist
                        best_target_midi = note.midi_number

        if best_target_midi is None:
            return

        # --- 5. Walk stepwise toward the target, picking closest candidate ---
        passage = []
        used = set()
        current_midi = current_midi_avg

        for _ in range(5):
            # Pick the unused candidate closest in pitch to current_midi
            # that is also moving toward the target
            direction = 1 if best_target_midi > current_midi else -1
            best = None
            best_score = 9999
            for c in candidates:
                s, f, name, midi = c
                key = (s, f)
                if key in used:
                    continue
                step = midi - current_midi
                # Prefer steps in the right direction, 1-2 semitones away
                if direction * step <= 0:
                    continue
                if abs(step) > 4:
                    continue
                score = abs(step)
                if score < best_score:
                    best_score = score
                    best = c
            if best is None:
                break
            s, f, name, midi = best
            passage.append((s, f, str(len(passage) + 1)))
            used.add((s, f))
            current_midi = midi
            if abs(midi - best_target_midi) <= 2:
                break

        self.voice_leading_notes = passage
        self._draw_voice_leading()

    def clear_voice_leading(self):
        """Remove the voice-leading overlay."""
        self.voice_leading_notes = []
        self.delete("voice_lead")

    def _draw_voice_leading(self):
        """Render the voice-leading passage on the canvas."""
        self.delete("voice_lead")
        if not self.voice_leading_notes:
            return

        width = self.winfo_width()
        height = self.winfo_height()
        string_spacing = height / (self.strings + 1)
        fret_spacing = width / (self.frets + 1)

        AMBER = "#ffaa00"
        prev_xy = None

        for i, (string_idx, fret, label) in enumerate(self.voice_leading_notes):
            y = (string_idx + 1) * string_spacing
            x = (fret + 0.5) * fret_spacing if fret > 0 else fret_spacing / 2

            # Draw connector line from previous note
            if prev_xy:
                self.create_line(
                    prev_xy[0], prev_xy[1], x, y,
                    fill=AMBER, width=2, dash=(4, 3),
                    tags=("voice_lead",)
                )
            prev_xy = (x, y)

            # Outer glow
            self.create_oval(x - 18, y - 18, x + 18, y + 18,
                             fill=AMBER, outline="", tags=("voice_lead",))
            # Inner dark circle
            self.create_oval(x - 14, y - 14, x + 14, y + 14,
                             fill=self.colors["bg_dark"], outline="",
                             tags=("voice_lead",))
            # Step number
            self.create_text(x, y, text=label,
                             fill=AMBER,
                             font=("Orbitron", 9, "bold"),
                             tags=("voice_lead",))

        # Fade out the passage after 4 seconds
        self.after(4000, self.clear_voice_leading)

    # ------------------------------------------------------------------ #
    #  Position / inversion label                                          #
    # ------------------------------------------------------------------ #

    def _get_inversion_label(self) -> str:
        """
        Determine the inversion of the current triad position.

        The bass note is the note on the lowest-pitched string in the
        current position (highest string_idx in our top-to-low tuning).
        Compare that note name against the triad tones.
        """
        if not self.highlighted_notes or not self.current_chord:
            return ""

        triad = self.current_chord.get_triad()
        if len(triad) < 3:
            return ""

        # Lowest-pitched string has the highest string_idx (E2 = index 5)
        bass_string, bass_fret = max(self.highlighted_notes, key=lambda sf: sf[0])
        bass_note_name = self._get_note_name(bass_string, bass_fret)

        root_name  = triad[0].name
        third_name = triad[1].name
        fifth_name = triad[2].name

        if bass_note_name == root_name:
            return "Root Position"
        elif bass_note_name == third_name:
            return "1st Inversion"
        elif bass_note_name == fifth_name:
            return "2nd Inversion"
        else:
            return ""

    def _get_neck_position_label(self) -> str:
        """
        Return a conventional neck-position label based on the lowest
        non-open fret in the current triad shape.

        Guitar neck positions:
          open / fret 1-2  → Open / 1st Position
          fret 3-5         → 2nd Position
          fret 6-8         → 3rd Position  (near 5th-fret marker)
          fret 9-11        → 4th Position  (near 9th-fret marker)
          fret 12+         → 5th Position  (octave)
        """
        if not self.highlighted_notes:
            return ""

        fretted = [f for _, f in self.highlighted_notes if f > 0]
        if not fretted:
            return "Open Position"

        lo = min(fretted)
        if lo <= 2:
            return "1st Position"
        elif lo <= 5:
            return "2nd Position"
        elif lo <= 8:
            return "3rd Position"
        elif lo <= 11:
            return "4th Position"
        else:
            return "5th Position"

    def _get_chord_label(self) -> str:
        """Return a compact chord symbol e.g. 'Gmaj7', 'Cm', 'D7'."""
        if not self.current_chord:
            return ""
        TYPE_SYMBOLS = {
            "Major": "",      "Minor": "m",     "7": "7",
            "maj7": "maj7",   "m7": "m7",       "sus2": "sus2",
            "sus4": "sus4",   "aug": "aug",      "dim": "dim",
            "dim7": "dim7",   "9": "9",          "maj9": "maj9",
            "m9": "m9",       "6": "6",          "m6": "m6",
            "add9": "add9",   "madd9": "madd9",  "7sus4": "7sus4",
            "7#5": "7#5",     "7b5": "7b5",      "m7b5": "m7b5",
            "13": "13",       "m13": "m13",
        }
        symbol = TYPE_SYMBOLS.get(self.current_chord.chord_type,
                                  self.current_chord.chord_type)
        return f"{self.current_chord.root.name}{symbol}"

    def _draw_position_label(self, canvas_width: int, canvas_height: int):
        """Draw chord name + inversion + neck-position panel in the top-right corner."""
        self.delete("pos_label")

        chord_label = self._get_chord_label()
        inversion   = self._get_inversion_label()
        position    = self._get_neck_position_label()

        if not chord_label and not inversion and not position:
            return

        CHORD_COLOR = "#ffffff"
        ACCENT      = self.colors["accent1"]
        SECONDARY   = self.colors["text_secondary"]
        PANEL_BG    = "#0e1a2a"

        pad_x, pad_y = 10, 10
        box_w, box_h = 190, 100
        x1 = canvas_width - pad_x - box_w
        y1 = pad_y
        x2 = canvas_width - pad_x
        y2 = pad_y + box_h
        cx = x1 + box_w // 2

        # Panel background
        self.create_rectangle(x1, y1, x2, y2,
                              fill=PANEL_BG,
                              outline=ACCENT,
                              width=1,
                              tags=("pos_label",))

        # Large bold chord name
        self.create_text(cx, y1 + 26,
                         text=chord_label,
                         fill=CHORD_COLOR,
                         font=("Orbitron", 22, "bold"),
                         anchor=tk.CENTER,
                         tags=("pos_label",))

        # Divider
        self.create_line(x1 + 8, y1 + 52, x2 - 8, y1 + 52,
                         fill=self.colors["grid_line"],
                         tags=("pos_label",))

        # Inversion line
        self.create_text(cx, y1 + 66,
                         text=inversion,
                         fill=ACCENT,
                         font=("Orbitron", 9, "bold"),
                         anchor=tk.CENTER,
                         tags=("pos_label",))

        # Divider
        self.create_line(x1 + 8, y1 + 78, x2 - 8, y1 + 78,
                         fill=self.colors["grid_line"],
                         tags=("pos_label",))

        # Neck position line
        self.create_text(cx, y1 + 90,
                         text=position,
                         fill=SECONDARY,
                         font=("Orbitron", 9),
                         anchor=tk.CENTER,
                         tags=("pos_label",))

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