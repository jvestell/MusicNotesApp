"""
Scale-to-chord relationship visualizer
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional

from core.music_theory import MusicTheory
from core.chord_system import Chord
from core.scale_system import Scale

class ScaleChordVisualizer(tk.Frame):
    """Visualizer that shows relationships between scales and chords"""
    
    def __init__(self, parent, theory: MusicTheory, colors: Dict, **kwargs):
        """Initialize the scale-chord visualizer"""
        bg_color = colors["bg_med"]
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.theory = theory
        self.colors = colors
        self.current_scale = None
        self.current_chord = None
        
        # Create the UI components
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all UI widgets"""
        # Title label
        title = tk.Label(self, 
                       text="SCALE-CHORD HARMONIC MATRIX", 
                       font=("Orbitron", 16, "bold"),
                       fg=self.colors["accent2"],
                       bg=self.colors["bg_dark"],
                       padx=10,
                       pady=5)
        title.pack(fill=tk.X, pady=10)
        
        # Main content frame
        content_frame = tk.Frame(self, bg=self.colors["bg_dark"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Scale degrees and chords
        self.degrees_frame = tk.LabelFrame(content_frame, 
                                        text="SCALE DEGREES & CHORDS", 
                                        font=("Orbitron", 10, "bold"),
                                        fg=self.colors["text_secondary"],
                                        bg=self.colors["bg_light"])
        self.degrees_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scale display
        self.scale_name = tk.Label(self.degrees_frame, 
                                text="Select a scale", 
                                font=("Orbitron", 12, "bold"),
                                fg=self.colors["text_primary"],
                                bg=self.colors["bg_light"])
        self.scale_name.pack(pady=5)
        
        # Scale degree buttons
        self.degrees_buttons_frame = tk.Frame(self.degrees_frame, bg=self.colors["bg_light"])
        self.degrees_buttons_frame.pack(fill=tk.X, pady=5)
        
        # Create 7 degree buttons (will be populated when a scale is selected)
        self.degree_buttons = []
        for i in range(7):
            btn = tk.Button(
                self.degrees_buttons_frame,
                text=f"{i+1}",
                font=("Orbitron", 9),
                bg=self.colors["bg_dark"],
                fg=self.colors["text_primary"],
                activebackground=self.colors["accent1"],
                activeforeground=self.colors["bg_dark"],
                width=3,
                height=1,
                state=tk.DISABLED
            )
            btn.grid(row=0, column=i, padx=3, pady=3)
            self.degree_buttons.append(btn)
            
        # Chord list
        self.chords_frame = tk.Frame(self.degrees_frame, bg=self.colors["bg_light"])
        self.chords_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollable chord list
        self.chords_list = tk.Listbox(
            self.chords_frame,
            font=("Orbitron", 10),
            bg=self.colors["bg_dark"],
            fg=self.colors["text_primary"],
            selectbackground=self.colors["accent1"],
            selectforeground=self.colors["bg_dark"],
            height=10
        )
        self.chords_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for chord list
        chords_scrollbar = ttk.Scrollbar(self.chords_frame, command=self.chords_list.yview)
        chords_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chords_list.config(yscrollcommand=chords_scrollbar.set)
        
        # Bind selection event
        self.chords_list.bind("<<ListboxSelect>>", self._on_chord_selected)
        
        # Right side - Chord and scale relationships info
        self.info_frame = tk.LabelFrame(content_frame, 
                                      text="HARMONIC ANALYSIS", 
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
        info_scrollbar = ttk.Scrollbar(self.info_text, command=self.info_text.yview)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=info_scrollbar.set)
        
        # Make the text widget read-only
        self.info_text.config(state=tk.DISABLED)
        
    def update_scale(self, scale: Scale):
        """Update the visualizer with a new scale"""
        self.current_scale = scale
        
        # Update scale name display
        self.scale_name.config(text=scale.name)
        
        # Get chords in this scale
        try:
            scale_chords = self.theory.get_chords_in_scale(scale)
        except Exception as e:
            scale_chords = []
            print(f"Error getting chords: {e}")
            
        # Clear the chord list
        self.chords_list.delete(0, tk.END)
        
        # Populate the chord list
        for chord in scale_chords:
            self.chords_list.insert(tk.END, chord.name)
            
        # Enable and update degree buttons
        for i, btn in enumerate(self.degree_buttons):
            if i < len(scale.notes):
                note_name = scale.notes[i].name
                btn.config(text=note_name, state=tk.NORMAL)
                
                # Command to show chord for this degree
                btn.config(command=lambda idx=i, chords=scale_chords: 
                                 self._on_degree_selected(idx, chords))
            else:
                btn.config(text="", state=tk.DISABLED)
                
        # Update info text
        self._update_info_text(scale=scale)
        
    def _on_degree_selected(self, degree_idx: int, scale_chords: List[Chord]):
        """Handle selection of a scale degree"""
        if degree_idx >= len(scale_chords):
            return
            
        # Find chords that start on this degree
        degree_chords = []
        degree_note = self.current_scale.notes[degree_idx]
        
        for chord in scale_chords:
            if chord.root.name == degree_note.name:
                degree_chords.append(chord)
                
        # Select the first chord in the list if any
        if degree_chords:
            # Find index in the full chord list
            for i in range(self.chords_list.size()):
                if self.chords_list.get(i) == degree_chords[0].name:
                    self.chords_list.selection_clear(0, tk.END)
                    self.chords_list.selection_set(i)
                    self.chords_list.see(i)
                    
                    # Trigger the selection event
                    self._on_chord_selected(None, selected_idx=i)
                    break
                    
    def _on_chord_selected(self, event, selected_idx=None):
        """Handle selection of a chord from the list"""
        if selected_idx is not None:
            selection = [selected_idx]
        else:
            selection = self.chords_list.curselection()
            
        if not selection:
            return
            
        selected_idx = selection[0]
        chord_name = self.chords_list.get(selected_idx)
        
        # Find the chord object
        try:
            scale_chords = self.theory.get_chords_in_scale(self.current_scale)
            selected_chord = None
            
            for chord in scale_chords:
                if chord.name == chord_name:
                    selected_chord = chord
                    break
                    
            if selected_chord:
                self.current_chord = selected_chord
                self._update_info_text(scale=self.current_scale, chord=selected_chord)
        except Exception as e:
            print(f"Error selecting chord: {e}")
            
    def _update_info_text(self, scale: Scale = None, chord: Chord = None):
        """Update the information text based on current selections"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        if scale:
            # Get scale information
            scale_notes = ", ".join([note.name for note in scale.notes])
            
            scale_info = (
                f"SCALE: {scale.name}\n\n"
                f"Notes: {scale_notes}\n\n"
                f"Characteristic: {self._get_scale_character(scale)}\n\n"
            )
            
            self.info_text.insert(tk.END, scale_info)
            
            # If a chord is also selected
            if chord:
                chord_notes = ", ".join([note.name for note in chord.notes])
                chord_function = self._get_chord_function(scale, chord)
                
                chord_info = (
                    f"CHORD: {chord.name}\n\n"
                    f"Notes: {chord_notes}\n\n"
                    f"Function: {chord_function}\n\n"
                    f"{self._get_chord_usage(chord)}\n\n"
                    f"Common Progressions:\n{self._get_common_progressions(scale, chord)}"
                )
                
                self.info_text.insert(tk.END, chord_info)
        
        # Make the text widget read-only again
        self.info_text.config(state=tk.DISABLED)
        
    def _get_scale_character(self, scale: Scale) -> str:
        """Get the character description of a scale"""
        scale_type = scale.scale_type.lower()
        
        if "major" in scale_type:
            return "Bright, happy, uplifting"
        elif "minor" in scale_type:
            if "harmonic" in scale_type:
                return "Exotic, mysterious, Middle-Eastern sound"
            elif "melodic" in scale_type:
                return "Smooth minor that resolves tension upward"
            else:
                return "Dark, melancholic, introspective"
        elif "pentatonic" in scale_type:
            if "major" in scale_type:
                return "Simple, happy, no tension - common in folk & pop"
            else:
                return "Bluesy, soulful, emotional - common in blues & rock"
        elif "blues" in scale_type:
            return "Raw, emotional, expressive - cornerstone of blues music"
        elif "dorian" in scale_type:
            return "Minor with a bright 6th - common in jazz & rock"
        elif "phrygian" in scale_type:
            return "Spanish/Flamenco sound, dark with tension"
        elif "lydian" in scale_type:
            return "Dreamy, floating, cosmic quality - common in film scores"
        elif "mixolydian" in scale_type:
            return "Bluesy major sound - common in classic rock"
        elif "locrian" in scale_type:
            return "Very tense and unstable - rarely used as a primary scale"
            
        return "Unique tonal quality with its own color and mood"
        
    def _get_chord_function(self, scale: Scale, chord: Chord) -> str:
        """Get the functional description of a chord in a scale"""
        # Find the degree of the chord in the scale
        degree = None
        for i, note in enumerate(scale.notes):
            if note.name == chord.root.name:
                degree = i + 1
                break
                
        if degree is None:
            return "Non-diatonic chord (not native to the scale)"
            
        # Determine chord function based on degree and quality
        if "major" in scale.scale_type.lower():
            # Major scale functions
            functions = {
                1: "Tonic (I) - Home/resolution chord",
                2: "Supertonic (ii) - Transitional minor chord",
                3: "Mediant (iii) - Emotional/supportive chord",
                4: "Subdominant (IV) - Movement away from home",
                5: "Dominant (V) - Creates tension wanting resolution",
                6: "Submediant (vi) - Relative minor/emotional contrast",
                7: "Leading Tone (vii°) - Strong tension toward tonic"
            }
        else:
            # Minor scale functions (natural minor)
            functions = {
                1: "Tonic (i) - Home/resolution chord",
                2: "Supertonic (ii°) - Diminished transitional chord",
                3: "Mediant (III) - Major emotional contrast",
                4: "Subdominant (iv) - Movement away from home",
                5: "Dominant (v) - Softer tension than major V",
                6: "Submediant (VI) - Relative major/emotional contrast",
                7: "Subtonic (VII) - Movement toward tonic"
            }
            
        return functions.get(degree, f"Scale degree {degree}")
        
    def _get_chord_usage(self, chord: Chord) -> str:
        """Get common usage description for this chord type"""
        chord_type = chord.chord_type.lower()
        
        if "major" in chord_type and not any(x in chord_type for x in ["maj7", "maj9"]):
            return "Usage: Foundational chord in most genres. Creates stable, happy feelings."
        elif "minor" in chord_type and not any(x in chord_type for x in ["m7", "m9"]):
            return "Usage: Foundational chord in most genres. Creates melancholic, serious feelings."
        elif "7" == chord_type:
            return "Usage: Creates tension in blues, jazz, rock. Essential for V7-I resolutions."
        elif "maj7" in chord_type:
            return "Usage: Common in jazz, bossa nova, and sophisticated pop. Creates a dreamy quality."
        elif "m7" in chord_type:
            return "Usage: Essential in jazz, soul, R&B. Creates smooth, contemplative feeling."
        elif "sus" in chord_type:
            return "Usage: Creates ambiguous tension, often resolving to major or minor. Common in rock, pop."
        elif "dim" in chord_type:
            return "Usage: Creates unstable tension, often used as passing chords or leading to resolution."
        elif "aug" in chord_type:
            return "Usage: Creates dreamlike tension, often in transitions. Common in psychedelic and jazz."
            
        return "This chord has specific applications based on its unique tonal qualities."
        
    def _get_common_progressions(self, scale: Scale, chord: Chord) -> str:
        """Get common chord progressions involving this chord"""
        # Find the degree of the chord in the scale
        degree = None
        for i, note in enumerate(scale.notes):
            if note.name == chord.root.name:
                degree = i + 1
                break
                
        if degree is None:
            return "As a non-diatonic chord, it often creates interest in standard progressions."
            
        # Common progressions based on the degree
        if "major" in scale.scale_type.lower():
            # Major scale progressions
            progressions = {
                1: "I - IV - V (classic)\nI - V - vi - IV (pop)\nI - vi - IV - V (doo-wop)",
                2: "ii - V - I (jazz)\nI - ii - IV - V (expanded pop)",
                3: "vi - iii - IV - I (dreamy)\nI - iii - IV (sparse)",
                4: "I - IV - V (classic)\nii - IV - I (gentle resolution)",
                5: "I - V - vi - IV (pop)\nii - V - I (jazz resolution)",
                6: "vi - IV - I - V (emotional pop)\nvi - ii - V - I (minor to major)",
                7: "I - vii° - vi (tension to release)\nii - V - I - vii° (passing diminished)"
            }
        else:
            # Minor scale progressions
            progressions = {
                1: "i - iv - V (harmonic minor)\ni - VI - VII (natural minor)\ni - iv - v (pure minor)",
                2: "i - ii° - V (minor jazz)\nii° - V - i (tension resolution)",
                3: "i - III - VI (minor uplift)\nIII - VI - VII - i (circular)",
                4: "i - iv - v (pure minor)\ni - iv - VII (soft resolution)",
                5: "i - iv - v - i (classic minor)\nIII - v - VI (tender)",
                6: "i - VI - III (brightest minor)\nVI - VII - i (common rock)",
                7: "i - VII - VI (descending)\nVII - i - v (minor resolution)"
            }
            
        return progressions.get(degree, "Various progressions based on context")