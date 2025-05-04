"""
Note and interval handling system
"""

from typing import List, Dict, Tuple, Optional
import re

class Note:
    """Represents a musical note with pitch and octave"""
    
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    def __init__(self, note_str: str):
        """Initialize a note from string like 'C#4'"""
        match = re.match(r'([A-G][#b]?)(\d+)?', note_str)
        if not match:
            raise ValueError(f"Invalid note format: {note_str}")
            
        self.name = match.group(1)
        self.octave = int(match.group(2)) if match.group(2) else 4
        
        # Normalize flats to sharps
        if 'b' in self.name:
            idx = self.NOTES.index(self.name[0])
            self.name = self.NOTES[(idx - 1) % 12]
            
    @property
    def midi_number(self) -> int:
        """Get MIDI note number"""
        return ((self.octave + 1) * 12) + self.NOTES.index(self.name)
    
    def transpose(self, semitones: int) -> 'Note':
        """Return a new note transposed by semitones"""
        new_midi = self.midi_number + semitones
        new_octave = (new_midi // 12) - 1
        new_name = self.NOTES[new_midi % 12]
        return Note(f"{new_name}{new_octave}")
    
    def get_interval(self, other: 'Note') -> int:
        """Get interval in semitones between this note and another"""
        return other.midi_number - self.midi_number
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return False
        return self.name == other.name and self.octave == other.octave
    
    def __str__(self) -> str:
        return f"{self.name}{self.octave}"
    
    def __repr__(self) -> str:
        return f"Note('{self.name}{self.octave}')"


class Interval:
    """Music interval utilities"""
    
    # Interval names and semitones
    INTERVALS = {
        'P1': 0,   # Perfect unison
        'm2': 1,   # Minor second
        'M2': 2,   # Major second
        'm3': 3,   # Minor third
        'M3': 4,   # Major third
        'P4': 5,   # Perfect fourth
        'TT': 6,   # Tritone
        'P5': 7,   # Perfect fifth
        'm6': 8,   # Minor sixth
        'M6': 9,   # Major sixth
        'm7': 10,  # Minor seventh
        'M7': 11,  # Major seventh
        'P8': 12   # Perfect octave
    }
    
    @classmethod
    def get_name(cls, semitones: int) -> str:
        """Get interval name from semitones"""
        for name, value in cls.INTERVALS.items():
            if value == semitones % 12:
                return name
        return "Unknown"
    
    @classmethod
    def get_semitones(cls, name: str) -> int:
        """Get semitones from interval name"""
        if name not in cls.INTERVALS:
            raise ValueError(f"Unknown interval: {name}")
        return cls.INTERVALS[name]