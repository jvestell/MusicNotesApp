"""
Scale construction and analysis system
"""

from typing import List, Dict, Tuple, Optional
from core.note_system import Note, Interval

class Scale:
    """Represents a musical scale"""
    
    def __init__(self, root: Note, scale_type: str, formula: List[int]):
        """
        Initialize a scale
        
        Args:
            root: Root note of the scale
            scale_type: Type of scale (e.g., "Major", "Minor Pentatonic")
            formula: Semitones from root for each scale degree
        """
        self.root = root
        self.scale_type = scale_type
        self.formula = formula
        self._build_notes()
        
    def _build_notes(self):
        """Build scale notes from root and formula"""
        self.notes = [self.root]
        for interval in self.formula[1:]:  # Skip root (first element)
            self.notes.append(self.root.transpose(interval))
            
    @property
    def name(self) -> str:
        """Get full scale name"""
        return f"{self.root.name} {self.scale_type}"
        
    def contains_note(self, note: Note) -> bool:
        """Check if scale contains a specific note (ignoring octave)"""
        for scale_note in self.notes:
            if scale_note.name == note.name:
                return True
        return False
        
    def get_mode(self, degree: int) -> 'Scale':
        """Get a mode of this scale starting from a given degree"""
        if degree < 1 or degree > len(self.notes):
            raise ValueError(f"Invalid degree: {degree}")
            
        # Calculate the formula for the mode
        mode_formula = []
        mode_root = self.notes[degree - 1]
        
        # Calculate intervals from the new root
        prev_interval = 0
        for i in range(len(self.notes)):
            # Calculate index with wraparound
            idx = (degree - 1 + i) % len(self.notes)
            # Handle octave wraparound
            octave_shift = 0 if (degree - 1 + i) < len(self.notes) else 12
            
            # Calculate the interval from the new root
            if i == 0:
                mode_formula.append(0)  # First note is always 0
            else:
                interval = (self.formula[idx] - self.formula[degree - 1]) % 12
                mode_formula.append(interval)
                
        return Scale(mode_root, f"{self.scale_type} mode {degree}", mode_formula)
        
    def __str__(self) -> str:
        return self.name
        
    def __repr__(self) -> str:
        return f"Scale({repr(self.root)}, '{self.scale_type}', {self.formula})"