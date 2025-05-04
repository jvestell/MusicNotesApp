"""
Core music theory concepts and calculations
"""

from typing import List, Dict, Tuple, Optional
import json
import logging
from pathlib import Path
from dataclasses import dataclass

from core.note_system import Note, Interval
from core.chord_system import ChordType, Chord
from core.scale_system import Scale

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChordPosition:
    """Represents a chord position on the fretboard"""
    frets: List[int]  # List of fret numbers (0-12) for each string
    fingers: List[int]  # Recommended finger numbers (1-4)
    barre: Optional[Tuple[int, int]] = None  # (string, fret) for barre chords

class MusicTheory:
    """Music theory engine that handles relationships between notes, chords, and scales"""
    
    def __init__(self, data_path: Path):
        """Initialize the music theory engine with data from JSON files"""
        self.data_path = data_path
        self._load_data()
        
    def _load_data(self):
        """Load chord and scale formulas from JSON files"""
        try:
            # Load chord formulas
            with open(self.data_path / "chord_formulas.json", "r") as f:
                self.chord_formulas = json.load(f)
                
            # Load scale formulas
            with open(self.data_path / "scale_formulas.json", "r") as f:
                self.scale_formulas = json.load(f)
                
            # Load tunings
            with open(self.data_path / "tunings.json", "r") as f:
                self.tunings = json.load(f)
                
            logger.info("Successfully loaded music theory data")
            
        except FileNotFoundError as e:
            logger.error(f"Failed to load data files: {e}")
            raise RuntimeError("Required data files are missing") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in data files: {e}")
            raise RuntimeError("Data files are corrupted") from e
    
    def get_chord(self, root: Note, chord_type: str) -> Chord:
        """Create a chord object based on root note and chord type"""
        if not isinstance(root, Note):
            raise TypeError("root must be a Note object")
            
        if chord_type not in self.chord_formulas:
            raise ValueError(f"Unknown chord type: {chord_type}")
            
        formula = self.chord_formulas[chord_type]
        return Chord(root, chord_type, formula)
    
    def get_scale(self, root: Note, scale_type: str) -> Scale:
        """Create a scale object based on root note and scale type"""
        if not isinstance(root, Note):
            raise TypeError("root must be a Note object")
            
        if scale_type not in self.scale_formulas:
            raise ValueError(f"Unknown scale type: {scale_type}")
            
        formula = self.scale_formulas[scale_type]
        return Scale(root, scale_type, formula)
    
    def get_chords_in_scale(self, scale: Scale) -> List[Chord]:
        """Get all chords that naturally occur in a given scale"""
        if not isinstance(scale, Scale):
            raise TypeError("scale must be a Scale object")
            
        chords = []
        # For each degree of the scale
        for i, degree in enumerate(scale.notes):
            # Try to build different chord types from this degree
            for chord_type, formula in self.chord_formulas.items():
                # Check if all chord tones are in the scale
                all_in_scale = True
                for interval in formula:
                    if not scale.contains_note(degree.transpose(interval)):
                        all_in_scale = False
                        break
                
                if all_in_scale:
                    chords.append(Chord(degree, chord_type, formula))
        
        return chords
    
    def get_scales_for_chord(self, chord: Chord) -> List[Scale]:
        """Find scales that contain all notes in the given chord"""
        if not isinstance(chord, Chord):
            raise TypeError("chord must be a Chord object")
            
        compatible_scales = []
        
        # Check each scale type
        for scale_type, formula in self.scale_formulas.items():
            # Try the scale starting from each chord tone
            for note in chord.notes:
                scale = Scale(note, scale_type, formula)
                if all(scale.contains_note(chord_note) for chord_note in chord.notes):
                    compatible_scales.append(scale)
        
        return compatible_scales
    
    def get_chord_positions(self, chord: Chord, tuning: str = "standard", max_fret: int = 12) -> List[ChordPosition]:
        """
        Get common positions/fingerings for a chord on the fretboard
        
        Args:
            chord: The chord to find positions for
            tuning: Guitar tuning to use (e.g., "standard", "drop_d")
            max_fret: Maximum fret to consider
            
        Returns:
            List of ChordPosition objects representing valid fingerings
        """
        if not isinstance(chord, Chord):
            raise TypeError("chord must be a Chord object")
            
        if tuning not in self.tunings:
            raise ValueError(f"Unknown tuning: {tuning}")
            
        if not 0 <= max_fret <= 24:
            raise ValueError("max_fret must be between 0 and 24")
            
        # Get the tuning notes
        tuning_notes = [Note(note) for note in self.tunings[tuning]]
        positions = []
        
        # Generate all possible fret combinations
        def find_positions(current_string: int, current_frets: List[int], current_fingers: List[int]):
            if current_string == len(tuning_notes):
                # Check if this position forms a valid chord
                notes = [tuning_notes[i].transpose(fret) for i, fret in enumerate(current_frets)]
                if all(any(note.name == chord_note.name for chord_note in chord.notes) for note in notes):
                    # Check for barre chords
                    barre = None
                    if len(set(current_frets)) == 1 and current_frets[0] > 0:
                        barre = (0, current_frets[0])
                    
                    positions.append(ChordPosition(
                        frets=current_frets.copy(),
                        fingers=current_fingers.copy(),
                        barre=barre
                    ))
                return
                
            # Try each fret on this string
            for fret in range(max_fret + 1):
                # Skip if this would create an impossible stretch
                if current_frets and abs(fret - current_frets[-1]) > 4:
                    continue
                    
                # Try different finger assignments
                for finger in range(1, 5):
                    # Skip if finger is already used
                    if finger in current_fingers:
                        continue
                        
                    current_frets.append(fret)
                    current_fingers.append(finger)
                    find_positions(current_string + 1, current_frets, current_fingers)
                    current_frets.pop()
                    current_fingers.pop()
        
        # Start the recursive search
        find_positions(0, [], [])
        
        # Sort positions by playability (fewer fingers, lower frets)
        positions.sort(key=lambda p: (len(p.fingers), max(p.frets)))
        
        return positions[:10]  # Return top 10 most playable positions