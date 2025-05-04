"""
Audio generation and playback system
"""

import numpy as np
import pygame
from typing import Dict, List, Optional, Tuple

from core.note_system import Note
from core.chord_system import Chord
from core.scale_system import Scale

class AudioEngine:
    """Audio generation and playback system with cyberpunk aesthetics"""
    
    def __init__(self, sample_rate=44100):
        """Initialize the audio engine"""
        self.sample_rate = sample_rate
        
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=sample_rate)
            
        # Sound cache for better performance
        self.note_cache = {}
        
    def generate_note(self, note: Note, duration=1.0, decay=0.5) -> np.ndarray:
        """Generate audio data for a single note"""
        # Check cache first
        cache_key = (str(note), duration, decay)
        if cache_key in self.note_cache:
            return self.note_cache[cache_key]
            
        # Convert note to frequency (A4 = 440Hz)
        a4_midi = 69  # MIDI note number for A4
        a4_freq = 440.0  # Hz
        
        # Calculate frequency based on distance from A4
        note_midi = note.midi_number
        semitones_from_a4 = note_midi - a4_midi
        freq = a4_freq * (2 ** (semitones_from_a4 / 12.0))
        
        # Generate time array
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Generate sine wave
        sine = 0.4 * np.sin(2 * np.pi * freq * t)
        
        # Add harmonics for a richer sound
        sine += 0.2 * np.sin(2 * np.pi * freq * 2 * t)  # First overtone
        sine += 0.1 * np.sin(2 * np.pi * freq * 3 * t)  # Second overtone
        sine += 0.05 * np.sin(2 * np.pi * freq * 4 * t)  # Third overtone
        
        # Apply decay envelope
        envelope = np.exp(-decay * t)
        audio_data = sine * envelope
        
        # Ensure we're within [-1, 1]
        audio_data = np.clip(audio_data, -1, 1)
        
        # Convert to 16-bit PCM
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Cache the result
        self.note_cache[cache_key] = audio_data
        
        return audio_data
        
    def generate_chord(self, chord: Chord, duration=1.5, decay=0.5) -> np.ndarray:
        """Generate audio data for a chord"""
        # Start with silence
        chord_data = np.zeros(int(self.sample_rate * duration), dtype=np.int32)
        
        # Add each note
        for note in chord.notes:
            note_data = self.generate_note(note, duration, decay)
            chord_data += note_data.astype(np.int32)
            
        # Scale to avoid clipping
        max_val = np.max(np.abs(chord_data))
        if max_val > 0:
            chord_data = chord_data * 32767 / max_val
            
        # Convert to 16-bit PCM
        return chord_data.astype(np.int16)
        
    def generate_scale(self, scale: Scale, duration=0.5, decay=0.8) -> np.ndarray:
        """Generate audio data for a scale (ascending and descending)"""
        # Calculate total duration
        total_notes = len(scale.notes) * 2 - 1  # Up and down, sharing top note
        total_duration = total_notes * duration
        
        # Start with silence
        scale_data = np.zeros(int(self.sample_rate * total_duration), dtype=np.int32)
        
        # Add ascending notes
        for i, note in enumerate(scale.notes):
            note_data = self.generate_note(note, duration, decay)
            offset = int(i * duration * self.sample_rate)
            end = offset + len(note_data)
            scale_data[offset:end] += note_data.astype(np.int32)
            
        # Add descending notes (excluding the root which was already played)
        for i, note in enumerate(reversed(scale.notes[1:])):
            note_data = self.generate_note(note, duration, decay)
            offset = int((len(scale.notes) + i) * duration * self.sample_rate)
            end = offset + len(note_data)
            scale_data[offset:end] += note_data.astype(np.int32)
            
        # Scale to avoid clipping
        max_val = np.max(np.abs(scale_data))
        if max_val > 0:
            scale_data = scale_data * 32767 / max_val
            
        # Convert to 16-bit PCM
        return scale_data.astype(np.int16)
        
    def generate_interval(self, notes: Tuple[Note, Note], duration=1.0, decay=0.5) -> np.ndarray:
        """Generate audio data for an interval (two notes played together and separately)"""
        # Calculate total duration (together then separate)
        total_duration = duration * 3
        
        # Start with silence
        interval_data = np.zeros(int(self.sample_rate * total_duration), dtype=np.int32)
        
        # Generate data for each note
        note1_data = self.generate_note(notes[0], duration, decay)
        note2_data = self.generate_note(notes[1], duration, decay)
        
        # Both notes together
        interval_data[:len(note1_data)] += note1_data.astype(np.int32)
        interval_data[:len(note2_data)] += note2_data.astype(np.int32)
        
        # First note alone
        offset = int(duration * self.sample_rate)
        end = offset + len(note1_data)
        interval_data[offset:end] += note1_data.astype(np.int32)
        
        # Second note alone
        offset = int(2 * duration * self.sample_rate)
        end = offset + len(note2_data)
        interval_data[offset:end] += note2_data.astype(np.int32)
        
        # Scale to avoid clipping
        max_val = np.max(np.abs(interval_data))
        if max_val > 0:
            interval_data = interval_data * 32767 / max_val
            
        # Convert to 16-bit PCM
        return interval_data.astype(np.int16)
        
    def generate_chord_progression(self, chords: List[Chord], duration=1.2, decay=0.5) -> np.ndarray:
        """Generate audio data for a chord progression"""
        # Calculate total duration
        total_duration = len(chords) * duration
        
        # Start with silence
        progression_data = np.zeros(int(self.sample_rate * total_duration), dtype=np.int32)
        
        # Add each chord
        for i, chord in enumerate(chords):
            chord_data = self.generate_chord(chord, duration, decay)
            offset = int(i * duration * self.sample_rate)
            end = offset + len(chord_data)
            progression_data[offset:end] += chord_data.astype(np.int32)
            
        # Scale to avoid clipping
        max_val = np.max(np.abs(progression_data))
        if max_val > 0:
            progression_data = progression_data * 32767 / max_val
            
        # Convert to 16-bit PCM
        return progression_data.astype(np.int16)
        
    def play_audio(self, audio_data: np.ndarray):
        """Play audio data using pygame"""
        # Create a sound object
        sound = pygame.mixer.Sound(audio_data.tobytes())
        
        # Play the sound
        sound.play()
        
    def play_note(self, note: Note, duration=1.0, decay=0.5):
        """Generate and play a note"""
        audio_data = self.generate_note(note, duration, decay)
        self.play_audio(audio_data)
        
    def play_chord(self, chord: Chord, duration=1.5, decay=0.5):
        """Generate and play a chord"""
        audio_data = self.generate_chord(chord, duration, decay)
        self.play_audio(audio_data)
        
    def play_scale(self, scale: Scale, duration=0.5, decay=0.8):
        """Generate and play a scale (ascending and descending)"""
        audio_data = self.generate_scale(scale, duration, decay)
        self.play_audio(audio_data)
        
    def play_interval(self, notes: Tuple[Note, Note], duration=1.0, decay=0.5):
        """Generate and play an interval"""
        audio_data = self.generate_interval(notes, duration, decay)
        self.play_audio(audio_data)
        
    def play_chord_progression(self, chords: List[Chord], duration=1.2, decay=0.5):
        """Generate and play a chord progression"""
        audio_data = self.generate_chord_progression(chords, duration, decay)
        self.play_audio(audio_data)