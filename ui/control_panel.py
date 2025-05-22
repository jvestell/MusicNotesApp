"""
Control panel for the fretboard
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable
import logging
import time

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
        
        # Game mode state
        self.game_mode = tk.StringVar(value="normal")
        self.is_game_paused = tk.BooleanVar(value=False)
        self.game_timer = None
        self.position_timer = None
        self.current_chord_index = 0
        self.selected_chords = []
        self.chord_progression = []  # Store the selected chord progression
        
        # Create the UI components
        self._create_widgets()
        
        # Initialize with empty state
        self.reset()
        
        # Set up default Revolving Triads settings
        self._setup_default_triad_settings()
        
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
            ("Revolving Triads", "revolving_triads")
        ]
        
        for text, value in modes:
            btn = self._create_neon_button(game_frame, text,
                                         lambda v=value: self._on_game_mode_selected(v))
            btn.pack(side=tk.LEFT, fill=tk.X, padx=3, pady=3, expand=True)
            
        # Game settings frame (initially hidden)
        self.game_settings_frame = tk.LabelFrame(self.left_frame,
                                               text="GAME SETTINGS",
                                               font=("Orbitron", 10, "bold"),
                                               fg=self.colors["text_secondary"],
                                               bg=self.colors["bg_light"])
        
        # Triad cycle time setting
        triad_frame = tk.Frame(self.game_settings_frame, bg=self.colors["bg_light"])
        triad_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=3)
        
        tk.Label(triad_frame,
                text="Triad Cycle (sec):",
                font=("Orbitron", 9),
                fg=self.colors["text_primary"],
                bg=self.colors["bg_light"]).pack(side=tk.LEFT, padx=5)
        
        self.triad_cycle_time = tk.StringVar(value="7")
        triad_spinbox = ttk.Spinbox(triad_frame,
                                   from_=1,
                                   to=60,
                                   increment=0.5,
                                   width=5,
                                   textvariable=self.triad_cycle_time,
                                   state="readonly")
        triad_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Chord cycle time setting
        chord_frame = tk.Frame(self.game_settings_frame, bg=self.colors["bg_light"])
        chord_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=3)
        
        tk.Label(chord_frame,
                text="Chord Cycle (sec):",
                font=("Orbitron", 9),
                fg=self.colors["text_primary"],
                bg=self.colors["bg_light"]).pack(side=tk.LEFT, padx=5)
        
        self.chord_cycle_time = tk.StringVar(value="21")
        chord_spinbox = ttk.Spinbox(chord_frame,
                                   from_=5,
                                   to=120,
                                   increment=0.5,
                                   width=5,
                                   textvariable=self.chord_cycle_time,
                                   state="readonly")
        chord_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Start game button (initially disabled)
        self.start_game_btn = self._create_neon_button(self.game_settings_frame,
                                                      "Start Game",
                                                      self._start_game)
        self.start_game_btn.config(state=tk.DISABLED)  # Start disabled
        self.start_game_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Initially hide game settings
        self.game_settings_frame.pack_forget()
        
        # Chord progression selector (initially hidden)
        self.progression_frame = tk.LabelFrame(self.left_frame,
                                             text="CHORD PROGRESSION",
                                             font=("Orbitron", 10, "bold"),
                                             fg=self.colors["text_secondary"],
                                             bg=self.colors["bg_light"])
        
        # Create three chord selectors
        self.progression_chords = []
        for i in range(3):
            chord_frame = tk.Frame(self.progression_frame, bg=self.colors["bg_light"])
            chord_frame.pack(side=tk.LEFT, fill=tk.X, padx=3, pady=3, expand=True)
            
            # Note selector
            note_var = tk.StringVar(value="")
            note_menu = ttk.Combobox(chord_frame, 
                                   textvariable=note_var,
                                   values=["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
                                   state="readonly",
                                   width=3)
            note_menu.pack(side=tk.LEFT, padx=2)
            
            # Chord type selector
            type_var = tk.StringVar(value="")
            type_menu = ttk.Combobox(chord_frame,
                                   textvariable=type_var,
                                   values=["Major", "Minor", "7", "maj7", "m7", "sus2", "sus4", "aug", "dim", "9"],
                                   state="readonly",
                                   width=6)
            type_menu.pack(side=tk.LEFT, padx=2)
            
            # Add button
            add_btn = self._create_neon_button(chord_frame, "Add",
                                             lambda n=note_var, t=type_var, idx=i: self._add_chord_to_progression(n, t, idx))
            add_btn.pack(side=tk.LEFT, padx=2)
            
            # Delete button (initially hidden)
            delete_btn = self._create_neon_button(chord_frame, "×",
                                               lambda idx=i: self._delete_chord_from_progression(idx))
            delete_btn.pack(side=tk.LEFT, padx=2)
            delete_btn.pack_forget()  # Initially hidden
            
            # Store the variables
            self.progression_chords.append({
                "note": note_var,
                "type": type_var,
                "button": add_btn,
                "delete_button": delete_btn
            })
        
        # Initially hide progression selector
        self.progression_frame.pack_forget()
        
        # Game controls (initially hidden)
        self.game_controls_frame = tk.Frame(game_frame, bg=self.colors["bg_light"])
        self.game_controls_frame.pack(side=tk.TOP, fill=tk.X, padx=3, pady=3)
        
        # Pause/Resume button
        self.pause_btn = self._create_neon_button(self.game_controls_frame, "Pause",
                                                self._toggle_game_pause)
        self.pause_btn.pack(side=tk.LEFT, fill=tk.X, padx=3, pady=3, expand=True)
        
        # Stop button
        self.stop_btn = self._create_neon_button(self.game_controls_frame, "Stop",
                                               self._stop_game)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, padx=3, pady=3, expand=True)
        
        # Initially hide game controls
        self.game_controls_frame.pack_forget()
        
        # Game status display
        self.game_status_frame = tk.LabelFrame(self.left_frame,
                                             text="GAME STATUS",
                                             font=("Orbitron", 10, "bold"),
                                             fg=self.colors["text_secondary"],
                                             bg=self.colors["bg_light"])
        
        # Timer display
        self.timer_display = tk.Label(self.game_status_frame,
                                    text="Time: 00:00",
                                    font=("Orbitron", 9),
                                    fg=self.colors["text_primary"],
                                    bg=self.colors["bg_light"])
        self.timer_display.pack(fill=tk.X, padx=5, pady=2)
        
        # Current chord display
        self.current_chord_display = tk.Label(self.game_status_frame,
                                           text="Current Chord: None",
                                           font=("Orbitron", 9),
                                           fg=self.colors["text_primary"],
                                           bg=self.colors["bg_light"])
        self.current_chord_display.pack(fill=tk.X, padx=5, pady=2)
        
        # Initially hide game status
        self.game_status_frame.pack_forget()
        
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
        # Action buttons (remove Play Sound)
        actions = [
            ("Show Chord", self._show_chord),
            ("Show Scale", self._show_scale),
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
        pass  # Remove Play Sound implementation
        
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
        self.game_mode.set(mode)
        
        if mode == "revolving_triads":
            # Show game settings and progression selector
            self.game_settings_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            self.progression_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            # Set up default chord progression if it's empty
            if not self.chord_progression:
                self._setup_default_chord_progression()
            else:
                # Reset progression and disable start button
                self.chord_progression = []
                self.start_game_btn.config(state=tk.DISABLED)
                for chord in self.progression_chords:
                    chord["note"].set("")
                    chord["type"].set("")
                    chord["button"].config(text="Add", bg=self.colors["bg_dark"])
                    chord["delete_button"].pack_forget()
                # Set up defaults after clearing
                self._setup_default_chord_progression()
            
            # Hide game controls and status until game starts
            self.game_controls_frame.pack_forget()
            self.game_status_frame.pack_forget()
        else:
            # Hide all game-related frames
            self.game_settings_frame.pack_forget()
            self.progression_frame.pack_forget()
            self.game_controls_frame.pack_forget()
            self.game_status_frame.pack_forget()
            
            # Stop any running game
            self._stop_game()
            
    def _setup_default_chord_progression(self):
        """Set up the default chord progression (G major, C major, D major)"""
        default_chords = [
            ("G", "Major"),
            ("C", "Major"),
            ("D", "Major")
        ]
        
        # Clear existing progression
        self.chord_progression = []
        
        # Add each chord to the progression
        for i, (note, chord_type) in enumerate(default_chords):
            # Set the values in the UI
            self.progression_chords[i]["note"].set(note)
            self.progression_chords[i]["type"].set(chord_type)
            
            # Create and add the chord to the progression
            try:
                root_note = Note(note + "4")  # Default to octave 4
                chord = self.theory.get_chord(root_note, chord_type)
                self.chord_progression.append(chord)
                
                # Update button states
                self.progression_chords[i]["button"].config(
                    text="✓",
                    bg=self.colors["accent1"]
                )
                # Show delete button
                self.progression_chords[i]["delete_button"].pack(side=tk.LEFT, padx=2)
            except Exception as e:
                logger.error(f"Error setting up default chord {note} {chord_type}: {e}")
        
        # Enable start button since we have chords
        self.start_game_btn.config(state=tk.NORMAL)

    def _setup_default_triad_settings(self):
        """Set up default settings for the Revolving Triads game"""
        # Set default cycle times
        self.triad_cycle_time.set("7")
        self.chord_cycle_time.set("21")
        
        # Note: We don't set up the chord progression here anymore
        # It will be set up when the Revolving Triads mode is selected

    def _add_chord_to_progression(self, note_var, type_var, index):
        """Add a chord to the progression"""
        note = note_var.get()
        chord_type = type_var.get()
        
        if not note or not chord_type:
            return
            
        try:
            # Create the chord
            root_note = Note(note + "4")  # Default to octave 4
            chord = self.theory.get_chord(root_note, chord_type)
            
            # Update the progression
            while len(self.chord_progression) <= index:
                self.chord_progression.append(None)
            self.chord_progression[index] = chord
            
            # Update button states
            self.progression_chords[index]["button"].config(
                text="✓",
                bg=self.colors["accent1"]
            )
            # Show delete button
            self.progression_chords[index]["delete_button"].pack(side=tk.LEFT, padx=2)
            
            # Enable start button if we have at least one chord
            if any(self.chord_progression):
                self.start_game_btn.config(state=tk.NORMAL)
            else:
                self.start_game_btn.config(state=tk.DISABLED)
                
        except Exception as e:
            logger.error(f"Error adding chord to progression: {e}")

    def _delete_chord_from_progression(self, index):
        """Delete a chord from the progression"""
        if index < len(self.chord_progression):
            # Clear the chord
            self.chord_progression[index] = None
            
            # Reset UI elements
            self.progression_chords[index]["note"].set("")
            self.progression_chords[index]["type"].set("")
            self.progression_chords[index]["button"].config(
                text="Add",
                bg=self.colors["bg_dark"]
            )
            # Hide delete button
            self.progression_chords[index]["delete_button"].pack_forget()
            
            # Update start button state
            if any(self.chord_progression):
                self.start_game_btn.config(state=tk.NORMAL)
            else:
                self.start_game_btn.config(state=tk.DISABLED)

    def _start_game(self):
        """Start the revolving triads game"""
        # Validate chord progression
        if not any(self.chord_progression):
            # Show error message
            tk.messagebox.showwarning(
                "No Chords Selected",
                "Please add at least one chord to the progression before starting."
            )
            return
        
        # Get cycle times from settings
        try:
            triad_cycle = float(self.triad_cycle_time.get())  # Use float for more precise timing
            chord_cycle = float(self.chord_cycle_time.get())
            
            if triad_cycle >= chord_cycle:
                tk.messagebox.showwarning(
                    "Invalid Settings",
                    "Triad cycle time must be less than chord cycle time."
                )
                return
        except ValueError:
            tk.messagebox.showwarning(
                "Invalid Settings",
                "Please enter valid numbers for cycle times."
            )
            return
        
        # Store cycle times
        self.triad_cycle_seconds = triad_cycle
        self.chord_cycle_seconds = chord_cycle
        
        # Reset game state
        self.current_chord_index = 0
        self.is_game_paused.set(False)
        
        # Reset timers
        self.last_chord_change = time.time()
        self.last_position_change = time.time()
        self.timer_start_time = time.time()
        
        # Use only the selected chords (filter out None values)
        self.selected_chords = [chord for chord in self.chord_progression if chord is not None]
        
        # Show first chord immediately
        self._update_current_chord()
        
        # Show game controls and status
        self.game_controls_frame.pack(side=tk.TOP, fill=tk.X, padx=3, pady=3)
        self.game_status_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Start timers
        self._start_timers()
        
    def _start_timers(self):
        """Start the game timers"""
        # Stop any existing timers
        self._stop_timers()
        
        # Start the main timer loop
        self._check_timers()
        
        # Start the display timer
        self._update_timer_display()

    def _check_timers(self):
        """Check and update all game timers"""
        if self.is_game_paused.get():
            return
        
        current_time = time.time()
        
        # Check chord timer using custom cycle time
        if current_time - self.last_chord_change >= self.chord_cycle_seconds:
            self._next_chord()
            self.last_chord_change = current_time
            self.timer_start_time = current_time
        
        # Check position timer using custom cycle time
        # Use a small buffer to account for timer precision
        if current_time - self.last_position_change >= self.triad_cycle_seconds:
            self._next_position()
            self.last_position_change = current_time
        
        # Continue checking with a shorter interval for more precise timing
        self.game_timer = self.after(50, self._check_timers)

    def _update_timer_display(self):
        """Update the timer display"""
        if self.is_game_paused.get():
            return
        
        # Calculate remaining time until next chord change
        elapsed = time.time() - self.timer_start_time
        remaining = max(0, self.chord_cycle_seconds - elapsed)
        
        # Convert to minutes and seconds, rounding down to nearest second
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        # Update display
        self.timer_display.config(text=f"Time: {minutes:02d}:{seconds:02d}")
        
        # Always continue updating the display
        self.after(100, self._update_timer_display)

    def _next_chord(self):
        """Move to the next chord in the sequence"""
        if not self.selected_chords:
            return
            
        # Move to next chord
        self.current_chord_index = (self.current_chord_index + 1) % len(self.selected_chords)
        
        # Update display with visual effect
        self._update_current_chord()
        
        # Don't reset position timer or trigger new position on chord change
        # This ensures positions only change every 5 seconds

    def _stop_timers(self):
        """Stop all game timers"""
        if self.game_timer:
            self.after_cancel(self.game_timer)
            self.game_timer = None
        
        # Also cancel the position timer if it exists
        if hasattr(self, 'position_timer') and self.position_timer:
            self.after_cancel(self.position_timer)
            self.position_timer = None

    def _toggle_game_pause(self):
        """Toggle game pause state"""
        self.is_game_paused.set(not self.is_game_paused.get())
        
        if self.is_game_paused.get():
            # Pause the game
            self._stop_timers()
            self.pause_btn.config(text="Resume")
        else:
            # Resume the game
            self._start_timers()
            self.pause_btn.config(text="Pause")
            
    def _stop_game(self):
        """Stop the game and return to normal mode"""
        self._stop_timers()
        
        # Reset game state
        self.current_chord_index = 0
        self.is_game_paused.set(False)
        
        # Reset button states
        self.start_game_btn.config(state=tk.NORMAL if any(self.chord_progression) else tk.DISABLED)
        self.pause_btn.config(text="Pause")
        
        # Clear the fretboard
        self.callback("clear", {})
        
    def _next_position(self):
        """Move to a new random position for the current chord"""
        if not self.selected_chords or self.is_game_paused.get():
            return
            
        # Get current chord
        current_chord = self.selected_chords[self.current_chord_index]
        
        # Request a new random position from the callback
        self.callback("new_position", {"chord": current_chord})
        
    def _update_current_chord(self):
        """Update the current chord display with visual effect"""
        if not self.selected_chords:
            return
            
        current_chord = self.selected_chords[self.current_chord_index]
        
        # Update display with visual effect
        self.current_chord_display.config(
            text=f"Current Chord: {current_chord.root.name} {current_chord.chord_type}",
            fg=self.colors["accent1"]  # Highlight color for effect
        )
        
        # Reset color after a short delay
        self.after(500, lambda: self.current_chord_display.config(
            fg=self.colors["text_primary"]
        ))
        
        # Notify callback of chord change with visual effect
        self.callback("chord_changed", {
            "chord": current_chord,
            "visual_effect": "explosion"
        })