"""
Control panel for the fretboard
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable
import logging
import threading

from core.music_theory import MusicTheory
from core.note_system import Note
from core.chord_system import Chord
from core.scale_system import Scale

# Configure logging
logger = logging.getLogger(__name__)

class ControlPanel(tk.Frame):
    """Control panel for the fretboard with cyberpunk styling"""
    
    def __init__(self, parent, theory: MusicTheory, colors: Dict, callback: Callable, audio_engine=None, **kwargs):
        """Initialize the control panel"""
        bg_color = colors["bg_med"]
        super().__init__(parent, bg=bg_color, **kwargs)

        self.theory = theory
        self.colors = colors
        self.callback = callback
        self.audio_engine = audio_engine

        # Track current chord/scale for playback
        self._current_chord = None
        self._current_scale = None
        
        # Track selected highlight type
        self.selected_highlight_type = tk.StringVar(value="")
        
        # Triad Finder state
        self.tf_active = False
        self.tf_phase = 0      # 0=idle, 1=note selection, 2=fretboard placement
        self.tf_chord = None
        self.tf_triad_note_names = []
        self.tf_selected_notes = set()
        self.tf_note_btns = {}   # note_name -> tk.Button

        # Note placement mode state
        self.note_placement_mode = tk.BooleanVar(value=False)
        
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
        
        # Game mode selector
        self._create_game_mode_selector()
        
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
        
    def _create_game_mode_selector(self):
        """Create the game mode selector"""
        # Frame for game mode
        game_frame = tk.LabelFrame(self.left_frame,
                                  text="GAME MODE",
                                  font=("Orbitron", 10, "bold"),
                                  fg=self.colors["text_secondary"],
                                  bg=self.colors["bg_light"])
        game_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Game mode buttons
        modes = [
            ("Normal", "normal"),
            ("Note Placement", "note_placement"),
            ("Triad Finder", "triad_finder")
        ]
        
        for text, value in modes:
            btn = self._create_neon_button(game_frame, text,
                                         lambda v=value: self._on_game_mode_selected(v))
            btn.pack(side=tk.LEFT, fill=tk.X, padx=3, pady=3, expand=True)
            
        # Triad Finder frame (initially hidden)
        self.tf_frame = tk.LabelFrame(self.left_frame,
                                     text="TRIAD FINDER",
                                     font=("Orbitron", 10, "bold"),
                                     fg=self.colors["text_secondary"],
                                     bg=self.colors["bg_light"])

        # Status label (chord name + instructions)
        self.tf_status_label = tk.Label(self.tf_frame,
                                       text="",
                                       font=("Orbitron", 10, "bold"),
                                       fg=self.colors["accent1"],
                                       bg=self.colors["bg_light"],
                                       wraplength=220,
                                       justify=tk.CENTER)
        self.tf_status_label.pack(fill=tk.X, padx=5, pady=4)

        # Start button
        self.tf_start_btn = self._create_neon_button(self.tf_frame, "Start",
                                                    self._start_triad_finder)
        self.tf_start_btn.pack(fill=tk.X, padx=5, pady=3)

        # Stop button (hidden until game is active)
        self.tf_stop_btn = self._create_neon_button(self.tf_frame, "Stop",
                                                   self._stop_triad_finder)
        self.tf_stop_btn.pack(fill=tk.X, padx=5, pady=3)
        self.tf_stop_btn.pack_forget()

        # Note selection frame (Phase 1) – 12 chromatic note buttons
        self.tf_note_selection_frame = tk.Frame(self.tf_frame, bg=self.colors["bg_light"])
        self.tf_note_selection_frame.pack(fill=tk.X, padx=5, pady=3)

        chromatic = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.tf_note_btns = {}
        for i, note_name in enumerate(chromatic):
            row, col = divmod(i, 6)
            btn = tk.Button(
                self.tf_note_selection_frame,
                text=note_name,
                font=("Orbitron", 10, "bold"),
                bg=self.colors["bg_dark"],
                fg=self.colors["text_primary"],
                activebackground=self.colors["accent1"],
                activeforeground=self.colors["bg_dark"],
                width=4, height=1,
                command=lambda n=note_name: self._on_tf_note_selected(n)
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.tf_note_btns[note_name] = btn
        self.tf_note_selection_frame.pack_forget()

        # Tracker label (Phase 2)
        self.tf_tracker_label = tk.Label(self.tf_frame,
                                        text="Notes remaining: 0",
                                        font=("Orbitron", 11, "bold"),
                                        fg=self.colors["accent1"],
                                        bg=self.colors["bg_light"])
        self.tf_tracker_label.pack(fill=tk.X, padx=5, pady=4)
        self.tf_tracker_label.pack_forget()

        # Initially hide the whole TF frame
        self.tf_frame.pack_forget()

                # Note placement controls (initially hidden)
        self.note_placement_frame = tk.LabelFrame(self.left_frame,
                                                text="NOTE PLACEMENT",
                                                font=("Orbitron", 10, "bold"),
                                                fg=self.colors["text_secondary"],
                                                bg=self.colors["bg_light"])
        
        # Clear notes button
        self.clear_notes_btn = self._create_neon_button(self.note_placement_frame,
                                                      "Clear Notes",
                                                      self._clear_placed_notes)
        self.clear_notes_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Initially hide note placement controls
        self.note_placement_frame.pack_forget()
        
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
            "sus2", "sus4", "aug", "dim", "dim7", "9",
            "maj9", "m9", "6", "m6", "add9", "madd9",
            "7sus4", "7#5", "7b5", "m7b5", "13", "m13"
        ]
        
        # Create a grid of chord buttons
        for i, chord_type in enumerate(chord_types):
            row = i % 6  # Changed from 5 to 6 to fit more buttons per row
            col = i // 6
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
        actions = [
            ("Show Chord", self._show_chord),
            ("Show Scale", self._show_scale),
            ("Play Chord", self._play_chord),
            ("Play Scale", self._play_scale),
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
                self._current_chord = chord
                self._current_scale = None
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
            self._current_chord = chord
            self._current_scale = None
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
            self._current_scale = scale
            self._current_chord = None
            self.callback("scale_changed", {"scale": scale})
        except ValueError as e:
            print(f"Error: {e}")
            
    def _play_chord(self):
        """Play the currently displayed chord"""
        if not self.audio_engine or not self._current_chord:
            return
        chord = self._current_chord
        threading.Thread(target=self.audio_engine.play_chord, args=(chord,), daemon=True).start()

    def _play_scale(self):
        """Play the currently displayed scale"""
        if not self.audio_engine or not self._current_scale:
            return
        scale = self._current_scale
        threading.Thread(target=self.audio_engine.play_scale, args=(scale,), daemon=True).start()
        
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

    def _on_game_mode_selected(self, mode):
        """Handle game mode selection"""
        # Hide all mode-specific frames first
        self.tf_frame.pack_forget()
        self.note_placement_frame.pack_forget()

        # Stop triad finder if active
        if self.tf_active:
            self._stop_triad_finder()

        if mode == "note_placement":
            self.note_placement_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            self.note_placement_mode.set(True)
            self.callback("note_placement_mode", {"enabled": True})
        elif mode == "triad_finder":
            self.tf_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            self.note_placement_mode.set(False)
            self.callback("note_placement_mode", {"enabled": False})
        else:  # normal mode
            self.note_placement_mode.set(False)
            self.callback("note_placement_mode", {"enabled": False})


    # ------------------------------------------------------------------ #
    #  Triad Finder                                                        #
    # ------------------------------------------------------------------ #

    TRIAD_CHORD_TYPES = ["Major", "Minor", "aug", "dim"]
    TYPE_DISPLAY = {
        "Major": "Major", "Minor": "Minor",
        "aug": "Augmented", "dim": "Diminished"
    }
    CHROMATIC_ROOTS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def _start_triad_finder(self):
        """Start or restart the Triad Finder game."""
        import random
        self.tf_active = True

        # Pick a random chord
        root = random.choice(self.CHROMATIC_ROOTS)
        chord_type = random.choice(self.TRIAD_CHORD_TYPES)
        root_note = Note(root + "4")
        self.tf_chord = self.theory.get_chord(root_note, chord_type)

        # Extract the 3 triad note names
        triad = self.tf_chord.get_triad()
        self.tf_triad_note_names = [n.name for n in triad]

        # Build display name
        display_type = self.TYPE_DISPLAY.get(chord_type, chord_type)
        chord_display = f"{root} {display_type}"

        # Phase 1 setup
        self.tf_phase = 1
        self.tf_selected_notes = set()

        # Reset note buttons appearance
        for note_name, btn in self.tf_note_btns.items():
            btn.config(bg=self.colors["bg_dark"], fg=self.colors["text_primary"])

        # Update status label
        self.tf_status_label.config(text=f"{chord_display}\nSelect its 3 notes:")

        # Show note selection, hide tracker
        self.tf_note_selection_frame.pack(fill=tk.X, padx=5, pady=3)
        self.tf_tracker_label.pack_forget()

        # Hide start btn, show stop btn
        self.tf_start_btn.pack_forget()
        self.tf_stop_btn.pack(fill=tk.X, padx=5, pady=3)

        # Tell fretboard to show the chord label (Phase 1 — no targets yet)
        self.callback("triad_finder_label", {"chord_name": chord_display})

    def _on_tf_note_selected(self, note_name: str):
        """Handle a note button click during Phase 1."""
        if self.tf_phase != 1:
            return
        if note_name in self.tf_selected_notes:
            return  # Already selected correctly

        if note_name in self.tf_triad_note_names:
            # Correct note
            self.tf_note_btns[note_name].config(bg=self.colors["accent1"],
                                                fg=self.colors["bg_dark"])
            self.tf_selected_notes.add(note_name)
            if len(self.tf_selected_notes) == 3:
                self._transition_to_phase2()
        else:
            # Wrong note — flash red then reset
            btn = self.tf_note_btns[note_name]
            btn.config(bg=self.colors["accent2"], fg=self.colors["bg_dark"])
            self.after(400, lambda b=btn: b.config(
                bg=self.colors["bg_dark"], fg=self.colors["text_primary"]))

    def _transition_to_phase2(self):
        """Switch from note selection (Phase 1) to fretboard placement (Phase 2)."""
        self.tf_phase = 2

        # Hide note selection, show tracker
        self.tf_note_selection_frame.pack_forget()

        # Build the display name for the chord label
        chord_type = self.tf_chord.chord_type
        display_type = self.TYPE_DISPLAY.get(chord_type, chord_type)
        chord_display = f"{self.tf_chord.root.name} {display_type}"

        # Tell fretboard & main window to start Phase 2
        self.callback("triad_finder_phase2", {
            "note_names": self.tf_triad_note_names,
            "chord": self.tf_chord,
            "chord_name": chord_display
        })

        # Compute target count via fretboard callback result — but we don't have
        # direct access to the fretboard here, so set a placeholder; the first
        # "note_found" callback will give us the real remaining count.
        # For now show tracker with a "..." placeholder until first note placed.
        total = self._compute_tf_total()
        self.tf_tracker_label.config(text=f"Notes remaining: {total}")
        self.tf_tracker_label.pack(fill=tk.X, padx=5, pady=4)
        self.tf_status_label.config(text=f"Find all notes on the fretboard!")

    def _compute_tf_total(self) -> int:
        """Count total target positions (all triad note occurrences, frets 1-13)."""
        # Standard tuning fret computation
        tuning = ["E4", "B3", "G3", "D3", "A2", "E2"]
        count = 0
        for string_note_name in tuning:
            open_note = Note(string_note_name)
            for fret in range(1, 14):
                if open_note.transpose(fret).name in self.tf_triad_note_names:
                    count += 1
        return count

    def on_triad_finder_event(self, event_type: str, data: dict):
        """Receive feedback from fretboard during Phase 2."""
        if event_type == "note_found":
            remaining = data.get("remaining", 0)
            self.tf_tracker_label.config(text=f"Notes remaining: {remaining}")
        elif event_type == "all_found":
            self.tf_tracker_label.config(text="Chord Complete!")
            self.tf_status_label.config(text="Nice work!")
            self.after(1500, self._start_triad_finder)

    def _stop_triad_finder(self):
        """Stop the game and return to idle."""
        self.tf_active = False
        self.tf_phase = 0
        self.tf_chord = None
        self.tf_note_selection_frame.pack_forget()
        self.tf_tracker_label.pack_forget()
        self.tf_start_btn.pack(fill=tk.X, padx=5, pady=3)
        self.tf_stop_btn.pack_forget()
        self.tf_status_label.config(text="")
        self.callback("triad_finder_stop", {})


    def _clear_placed_notes(self):
        """Clear all manually placed notes"""
        self.callback("clear_placed_notes", {})