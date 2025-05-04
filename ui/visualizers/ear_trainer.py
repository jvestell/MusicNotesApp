"""
Ear training module with cyberpunk theme
"""

import tkinter as tk
from tkinter import ttk
import random
import pygame
from typing import Dict, List, Optional

from core.music_theory import MusicTheory
from core.chord_system import Chord
from core.scale_system import Scale
from core.note_system import Note

class EarTrainerVisualizer(tk.Frame):
    """Ear training component for learning to identify chords and intervals"""
    
    def __init__(self, parent, theory: MusicTheory, colors: Dict, **kwargs):
        """Initialize the ear trainer"""
        bg_color = colors["bg_med"]
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.theory = theory
        self.colors = colors
        
        # Training state
        self.current_exercise_type = None
        self.current_answer = None
        self.score = {"correct": 0, "total": 0}
        
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100)
            
        # Create the UI components
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all UI widgets"""
        # Title label
        title = tk.Label(self, 
                       text="NEURAL EAR TRAINING SYSTEM", 
                       font=("Orbitron", 16, "bold"),
                       fg=self.colors["accent2"],
                       bg=self.colors["bg_dark"],
                       padx=10,
                       pady=5)
        title.pack(fill=tk.X, pady=10)
        
        # Main content frame
        content_frame = tk.Frame(self, bg=self.colors["bg_dark"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Exercise selector
        selector_frame = tk.LabelFrame(content_frame, 
                                     text="TRAINING PROTOCOLS", 
                                     font=("Orbitron", 10, "bold"),
                                     fg=self.colors["text_secondary"],
                                     bg=self.colors["bg_light"])
        selector_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Exercise type buttons
        exercises = [
            ("Chord Types", lambda: self._select_exercise("chord_types")),
            ("Chord Progressions", lambda: self._select_exercise("chord_progressions")),
            ("Intervals", lambda: self._select_exercise("intervals")),
            ("Scale Types", lambda: self._select_exercise("scale_types"))
        ]
        
        for text, command in exercises:
            btn = tk.Button(
                selector_frame,
                text=text,
                command=command,
                relief=tk.RAISED,
                borderwidth=2,
                font=("Orbitron", 9),
                bg=self.colors["bg_dark"],
                fg=self.colors["text_primary"],
                activebackground=self.colors["accent1"],
                activeforeground=self.colors["bg_dark"],
                width=18,
                height=2,
                padx=5,
                pady=3
            )
            btn.pack(fill=tk.X, padx=5, pady=5)
            
        # Add hover effects
        for child in selector_frame.winfo_children():
            if isinstance(child, tk.Button):
                child.bind("<Enter>", lambda e, b=child: self._on_button_hover(b, True))
                child.bind("<Leave>", lambda e, b=child: self._on_button_hover(b, False))
                
        # Center - Exercise area
        self.exercise_frame = tk.Frame(content_frame, bg=self.colors["bg_dark"])
        self.exercise_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Exercise title
        self.exercise_title = tk.Label(self.exercise_frame, 
                                    text="Select a training protocol", 
                                    font=("Orbitron", 12, "bold"),
                                    fg=self.colors["text_primary"],
                                    bg=self.colors["bg_dark"])
        self.exercise_title.pack(pady=10)
        
        # Initial message
        self.message = tk.Label(self.exercise_frame, 
                              text="Choose an exercise type from the left panel", 
                              font=("Orbitron", 10),
                              fg=self.colors["text_secondary"],
                              bg=self.colors["bg_dark"],
                              wraplength=400)
        self.message.pack(pady=10)
        
        # Play button (initially disabled)
        self.play_button = tk.Button(
            self.exercise_frame,
            text="PLAY SOUND",
            command=self._play_current_sound,
            relief=tk.RAISED,
            borderwidth=2,
            font=("Orbitron", 12, "bold"),
            bg=self.colors["bg_med"],
            fg=self.colors["accent1"],
            activebackground=self.colors["accent1"],
            activeforeground=self.colors["bg_dark"],
            state=tk.DISABLED,
            width=15,
            height=2
        )
        self.play_button.pack(pady=20)
        
        # Answer frame (will contain buttons dynamically)
        self.answer_frame = tk.Frame(self.exercise_frame, bg=self.colors["bg_dark"])
        self.answer_frame.pack(fill=tk.X, pady=20)
        
        # Next button (initially disabled)
        self.next_button = tk.Button(
            self.exercise_frame,
            text="NEXT EXERCISE",
            command=self._next_exercise,
            relief=tk.RAISED,
            borderwidth=2,
            font=("Orbitron", 10),
            bg=self.colors["bg_med"],
            fg=self.colors["text_primary"],
            activebackground=self.colors["text_primary"],
            activeforeground=self.colors["bg_dark"],
            state=tk.DISABLED,
            width=15,
            height=1
        )
        self.next_button.pack(pady=10)
        
        # Score display
        self.score_display = tk.Label(self.exercise_frame, 
                                   text="Score: 0/0", 
                                   font=("Orbitron", 10),
                                   fg=self.colors["text_secondary"],
                                   bg=self.colors["bg_dark"])
        self.score_display.pack(pady=5)
        
        # Right side - Learning info
        self.info_frame = tk.LabelFrame(content_frame, 
                                      text="NEURAL INTERFACE DATA", 
                                      font=("Orbitron", 10, "bold"),
                                      fg=self.colors["text_secondary"],
                                      bg=self.colors["bg_light"])
        self.info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Information text
        self.info_text = tk.Text(
            self.info_frame,
            font=("Orbitron", 10),
            bg=self.colors["bg_dark"],
            fg=self.colors["text_primary"],
            wrap=tk.WORD,
            padx=10,
            pady=10,
            height=20
        )
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for info text
        info_scrollbar = ttk.Scrollbar(self.info_frame, command=self.info_text.yview)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=info_scrollbar.set)
        
        # Make the text widget read-only
        self.info_text.config(state=tk.DISABLED)
        
        # Add default info text
        self._update_info_text("Select a training protocol to begin...")
        
    def _on_button_hover(self, button, is_hover):
        """Handle button hover effects"""
        if is_hover:
            button.config(bg=self.colors["bg_light"])
        else:
            button.config(bg=self.colors["bg_dark"])
            
    def _select_exercise(self, exercise_type):
        """Select an exercise type and start the first exercise"""
        self.current_exercise_type = exercise_type
        
        # Update exercise title
        titles = {
            "chord_types": "CHORD TYPE RECOGNITION",
            "chord_progressions": "CHORD PROGRESSION RECOGNITION",
            "intervals": "INTERVAL RECOGNITION",
            "scale_types": "SCALE TYPE RECOGNITION"
        }
        
        self.exercise_title.config(text=titles.get(exercise_type, "Unknown Exercise"))
        
        # Enable play button
        self.play_button.config(state=tk.NORMAL)
        
        # Update info text with details about this exercise
        self._update_info_text_for_exercise(exercise_type)
        
        # Start the first exercise
        self._next_exercise()
        
    def _next_exercise(self):
        """Start the next exercise"""
        # Clear any previous answers
        for widget in self.answer_frame.winfo_children():
            widget.destroy()
            
        # Disable next button until answer is selected
        self.next_button.config(state=tk.DISABLED)
        
        # Generate a new exercise based on type
        if self.current_exercise_type == "chord_types":
            self._generate_chord_type_exercise()
        elif self.current_exercise_type == "chord_progressions":
            self._generate_chord_progression_exercise()
        elif self.current_exercise_type == "intervals":
            self._generate_interval_exercise()
        elif self.current_exercise_type == "scale_types":
            self._generate_scale_type_exercise()
            
        # Update message
        self.message.config(text="Listen to the audio and select the correct answer")
        
    def _generate_chord_type_exercise(self):
        """Generate a chord type recognition exercise"""
        # Possible chord types to use
        chord_types = ["Major", "Minor", "7", "maj7", "m7", "sus4", "aug", "dim"]
        
        # Possible root notes
        root_notes = ["C", "D", "E", "F", "G", "A", "B"]
        
        # Randomly select a root note and chord type
        root = random.choice(root_notes)
        chord_type = random.choice(chord_types)
        
        # Create the chord
        try:
            self.current_answer = chord_type
            root_note = root + "4"  # Use octave 4
            self.current_chord = self.theory.get_chord(Note(root_note), chord_type)
        except Exception as e:
            print(f"Error creating chord: {e}")
            self.message.config(text="Error creating exercise. Try again.")
            return
            
        # Create answer buttons
        self._create_answer_buttons(chord_types)
        
    def _generate_chord_progression_exercise(self):
        """Generate a chord progression recognition exercise"""
        # Common chord progressions to recognize
        progressions = [
            ("I-IV-V", ["Major", "Major", "Major"]),
            ("I-V-vi-IV", ["Major", "Major", "Minor", "Major"]),
            ("ii-V-I", ["Minor", "Major", "Major"]),
            ("i-iv-v", ["Minor", "Minor", "Minor"]),
            ("I-vi-IV-V", ["Major", "Minor", "Major", "Major"])
        ]
        
        # Randomly select a progression
        progression_name, chord_types = random.choice(progressions)
        
        # Use C as the root to keep it simple
        root = "C"
        
        # Create the progression
        try:
            self.current_answer = progression_name
            self.current_progression = []
            
            if progression_name.startswith("i"):
                # Minor key progression
                scale = self.theory.get_scale(Note(root + "4"), "Minor")
            else:
                # Major key progression
                scale = self.theory.get_scale(Note(root + "4"), "Major")
                
            # This is simplified - normally we'd build actual chords based on the scale degrees
            self.current_progression = [progression_name]  # Just store the name for now
        except Exception as e:
            print(f"Error creating progression: {e}")
            self.message.config(text="Error creating exercise. Try again.")
            return
            
        # Create answer buttons
        progression_names = [p[0] for p in progressions]
        self._create_answer_buttons(progression_names)
        
    def _generate_interval_exercise(self):
        """Generate an interval recognition exercise"""
        # Possible intervals to use
        intervals = [
            ("Minor 2nd", 1),
            ("Major 2nd", 2),
            ("Minor 3rd", 3),
            ("Major 3rd", 4),
            ("Perfect 4th", 5),
            ("Tritone", 6),
            ("Perfect 5th", 7),
            ("Minor 6th", 8),
            ("Major 6th", 9),
            ("Minor 7th", 10),
            ("Major 7th", 11),
            ("Octave", 12)
        ]
        
        # Randomly select an interval
        interval_name, semitones = random.choice(intervals)
        
        # Possible root notes
        root_notes = ["C", "D", "E", "F", "G", "A", "B"]
        
        # Randomly select a root note
        root = random.choice(root_notes)
        
        # Create the interval
        try:
            self.current_answer = interval_name
            root_note = Note(root + "4")  # Use octave 4
            second_note = root_note.transpose(semitones)
            self.current_interval = (root_note, second_note)
        except Exception as e:
            print(f"Error creating interval: {e}")
            self.message.config(text="Error creating exercise. Try again.")
            return
            
        # Create answer buttons
        interval_names = [i[0] for i in intervals]
        self._create_answer_buttons(interval_names)
        
    def _generate_scale_type_exercise(self):
        """Generate a scale type recognition exercise"""
        # Possible scale types to use
        scale_types = [
            "Major", 
            "Minor", 
            "Pentatonic Major", 
            "Pentatonic Minor",
            "Blues",
            "Harmonic Minor"
        ]
        
        # Possible root notes
        root_notes = ["C", "D", "E", "F", "G", "A", "B"]
        
        # Randomly select a root note and scale type
        root = random.choice(root_notes)
        scale_type = random.choice(scale_types)
        
        # Create the scale
        try:
            self.current_answer = scale_type
            root_note = root + "4"  # Use octave 4
            self.current_scale = self.theory.get_scale(Note(root_note), scale_type)
        except Exception as e:
            print(f"Error creating scale: {e}")
            self.message.config(text="Error creating exercise. Try again.")
            return
            
        # Create answer buttons
        self._create_answer_buttons(scale_types)
        
    def _create_answer_buttons(self, options):
        """Create answer buttons for the given options"""
        # Randomize the order
        random.shuffle(options)
        
        # Number of buttons per row
        buttons_per_row = 4
        
        # Create buttons
        for i, option in enumerate(options):
            row = i // buttons_per_row
            col = i % buttons_per_row
            
            btn = tk.Button(
                self.answer_frame,
                text=option,
                command=lambda opt=option: self._check_answer(opt),
                relief=tk.RAISED,
                borderwidth=2,
                font=("Orbitron", 9),
                bg=self.colors["bg_dark"],
                fg=self.colors["text_primary"],
                activebackground=self.colors["accent1"],
                activeforeground=self.colors["bg_dark"],
                width=15,
                height=2
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
            
            # Add hover effects
            btn.bind("<Enter>", lambda e, b=btn: self._on_button_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._on_button_hover(b, False))
            
    def _play_current_sound(self):
        """Play the current sound for the exercise"""
        # This would be implemented with sound generation
        # For now, just show a message
        self.message.config(text="[Sound would play here in a full implementation]")
        
    def _check_answer(self, selected_option):
        """Check if the selected answer is correct"""
        # Update score
        self.score["total"] += 1
        if selected_option == self.current_answer:
            self.score["correct"] += 1
            result_message = "Correct! Well done."
        else:
            result_message = f"Incorrect. The answer was {self.current_answer}."
            
        # Update score display
        self.score_display.config(text=f"Score: {self.score['correct']}/{self.score['total']}")
        
        # Update message
        self.message.config(text=result_message)
        
        # Enable next button
        self.next_button.config(state=tk.NORMAL)
        
        # Color answer buttons
        for btn in self.answer_frame.winfo_children():
            if btn["text"] == self.current_answer:
                btn.config(bg=self.colors["accent1"], fg=self.colors["bg_dark"])
            elif btn["text"] == selected_option and selected_option != self.current_answer:
                btn.config(bg=self.colors["accent2"], fg=self.colors["bg_dark"])
                
            # Disable all buttons
            btn.config(state=tk.DISABLED)
            
    def _update_info_text(self, text):
        """Update the information text"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.config(state=tk.DISABLED)
        
    def _update_info_text_for_exercise(self, exercise_type):
        """Update the information text with details about the current exercise"""
        if exercise_type == "chord_types":
            text = (
                "CHORD TYPE RECOGNITION\n\n"
                "This exercise trains your ear to identify different chord types by sound.\n\n"
                "Each chord has a unique sonic quality:\n"
                "• Major chords sound bright and happy\n"
                "• Minor chords sound dark and melancholic\n"
                "• 7th chords have a bluesy tension\n"
                "• Major 7th chords have a jazzy, lush quality\n"
                "• Minor 7th chords sound smooth and contemplative\n"
                "• Sus4 chords have an unresolved, floating quality\n"
                "• Augmented chords sound tense and dreamlike\n"
                "• Diminished chords sound unstable and spooky\n\n"
                "Listen carefully to the character of each chord. With practice, "
                "you'll be able to instantly recognize chord types by ear."
            )
        elif exercise_type == "chord_progressions":
            text = (
                "CHORD PROGRESSION RECOGNITION\n\n"
                "This exercise trains your ear to identify common chord progressions.\n\n"
                "Each progression has a characteristic sound:\n"
                "• I-IV-V: The classic progression of blues and rock\n"
                "• I-V-vi-IV: The modern pop progression\n"
                "• ii-V-I: The essential jazz progression\n"
                "• i-iv-v: The minor key classic progression\n"
                "• I-vi-IV-V: The doo-wop/50s progression\n\n"
                "Focus on the movement and emotional journey of the chords. "
                "Recognizing these patterns will help you understand and play songs by ear."
            )
        elif exercise_type == "intervals":
            text = (
                "INTERVAL RECOGNITION\n\n"
                "This exercise trains your ear to identify the distance between two notes.\n\n"
                "Each interval has a unique sound character:\n"
                "• Minor 2nd: Tense, dissonant (Jaws theme)\n"
                "• Major 2nd: Step-wise motion (Happy Birthday start)\n"
                "• Minor 3rd: First step down in a minor scale (Greensleeves start)\n"
                "• Major 3rd: First step up in a major chord (Oh When The Saints)\n"
                "• Perfect 4th: Clear, pure sound (Wedding March start)\n"
                "• Tritone: Very tense, unstable (The Simpsons theme start)\n"
                "• Perfect 5th: Open, stable sound (Star Wars theme start)\n"
                "• Minor/Major 6th: Expressive leap (Love Story theme/My Bonnie)\n"
                "• Minor/Major 7th: Large, tense leap (Star Trek theme/Take On Me)\n"
                "• Octave: Complete, same note higher (Somewhere Over The Rainbow)\n\n"
                "Intervals are the building blocks of all music. Recognizing them "
                "is fundamental to developing your ear."
            )
        elif exercise_type == "scale_types":
            text = (
                "SCALE TYPE RECOGNITION\n\n"
                "This exercise trains your ear to identify different scale types.\n\n"
                "Each scale has a distinctive mood and character:\n"
                "• Major: Bright, happy (Happy Birthday)\n"
                "• Minor: Dark, melancholic (Greensleeves)\n"
                "• Pentatonic Major: Simple, folk-like (My Girl)\n"
                "• Pentatonic Minor: Bluesy, rock (Sweet Child O' Mine solo)\n"
                "• Blues: Expressive, emotional (Crossroads)\n"
                "• Harmonic Minor: Exotic, Middle-Eastern (Miserlou)\n\n"
                "Listen for the unique flavor of each scale. This skill helps with "
                "improvisation and understanding the emotional quality of music."
            )
        else:
            text = "Select a training protocol to see information about the exercise."
            
        self._update_info_text(text)