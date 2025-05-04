"""
Chord construction and analysis system
"""

from typing import List, Dict, Tuple, Optional
from core.note_system import Note, Interval

class ChordType:
    """Defines a chord type with its formula and properties"""
    
    def __init__(self, name: str, formula: List[int], symbol: str = None):
        """
        Initialize a chord type
        
        Args:
            name: Chord type name (e.g., "Major", "Minor7")
            formula: List of semitones from root (e.g., [0, 4, 7] for major)
            symbol: Chord symbol (e.g., "maj", "m7")
        """
        self.name = name
        self.formula = formula
        self.symbol = symbol or name
        
    def __str__(self) -> str:
        return self.name
        
    def __repr__(self) -> str:
        return f"ChordType('{self.name}', {self.formula}, '{self.symbol}')"


class Chord:
    """Represents a musical chord"""
    
    def __init__(self, root: Note, chord_type: str, formula: List[int]):
        """
        Initialize a chord
        
        Args:
            root: Root note of the chord
            chord_type: Type of chord (e.g., "Major", "Minor7")
            formula: Semitones from root for each chord tone
        """
        self.root = root
        self.chord_type = chord_type
        self.formula = formula
        self._build_notes()
        
    def _build_notes(self):
        """Build chord notes from root and formula"""
        self.notes = [self.root]
        for interval in self.formula[1:]:  # Skip root (first element)
            self.notes.append(self.root.transpose(interval))
            
    @property
    def name(self) -> str:
        """Get full chord name"""
        return f"{self.root.name} {self.chord_type}"
        
    def contains_note(self, note: Note) -> bool:
        """Check if chord contains a specific note (ignoring octave)"""
        for chord_note in self.notes:
            if chord_note.name == note.name:
                return True
        return False
        
    def get_triad(self) -> List[Note]:
        """Extract just the triad (root, third/fourth/second, fifth) from the chord"""
        if len(self.notes) < 3:
            return self.notes  # Return whatever we have
            
        # Find the root, third/fourth/second and fifth positions
        triad_indices = [0]  # Root is always first
        
        # For sus2 and sus4 chords, we need to find the second or fourth instead of third
        if "sus2" in self.chord_type:
            # Find second (2 semitones from root)
            for i, note in enumerate(self.notes[1:], 1):
                interval = self.root.get_interval(note)
                if interval % 12 == 2:  # Check for any note that's 2 semitones from root
                    triad_indices.append(i)
                    break
        elif "sus4" in self.chord_type:
            # Find fourth (5 semitones from root)
            for i, note in enumerate(self.notes[1:], 1):
                interval = self.root.get_interval(note)
                if interval % 12 == 5:  # Check for any note that's 5 semitones from root
                    triad_indices.append(i)
                    break
        else:
            # Find third (3 or 4 semitones from root)
            for i, note in enumerate(self.notes[1:], 1):
                interval = self.root.get_interval(note)
                if interval % 12 in [3, 4]:  # Check for any note that's 3 or 4 semitones from root
                    triad_indices.append(i)
                    break
                
        # Find fifth (7 semitones from root)
        for i, note in enumerate(self.notes[1:], 1):
            interval = self.root.get_interval(note)
            if interval % 12 == 7:  # Check for any note that's 7 semitones from root
                triad_indices.append(i)
                break
                
        return [self.notes[i] for i in triad_indices]
        
    def __str__(self) -> str:
        return self.name
        
    def __repr__(self) -> str:
        return f"Chord({repr(self.root)}, '{self.chord_type}', {self.formula})"