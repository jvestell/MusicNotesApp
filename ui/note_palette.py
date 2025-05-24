"""
Note palette widget for drag-and-drop note placement
"""

import tkinter as tk
from typing import Dict, List, Callable
from core.note_system import Note

class NotePalette(tk.Frame):
    """Widget that displays draggable notes in a grid layout"""
    
    def __init__(self, parent, colors: Dict, on_drag_start: Callable, **kwargs):
        """Initialize the note palette"""
        bg_color = colors["bg_med"]
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.colors = colors
        self.on_drag_start = on_drag_start
        
        # Create the UI components
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all UI widgets"""
        # Title label
        title = tk.Label(self, 
                       text="NOTE PALETTE", 
                       font=("Orbitron", 10, "bold"),
                       fg=self.colors["text_secondary"],
                       bg=self.colors["bg_light"],
                       padx=10,
                       pady=5)
        title.pack(fill=tk.X, pady=5)
        
        # Frame for note buttons
        notes_frame = tk.Frame(self, bg=self.colors["bg_light"])
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Natural notes
        natural_notes = ["C", "D", "E", "F", "G", "A", "B"]
        sharps = ["C#", "D#", "F#", "G#", "A#"]
        
        # Create a grid of note buttons
        for i, note in enumerate(natural_notes):
            btn = self._create_note_button(notes_frame, note)
            btn.grid(row=i, column=0, padx=3, pady=3, sticky="ew")
            
        for i, note in enumerate(sharps):
            btn = self._create_note_button(notes_frame, note)
            btn.grid(row=i, column=1, padx=3, pady=3, sticky="ew")
            
    def _create_note_button(self, parent, note: str) -> tk.Button:
        """Create a draggable note button"""
        button = tk.Button(
            parent,
            text=note,
            relief=tk.RAISED,
            borderwidth=2,
            font=("Orbitron", 12, "bold"),
            bg=self.colors["bg_dark"],
            fg=self.colors["text_primary"],
            activebackground=self.colors["accent1"],
            activeforeground=self.colors["bg_dark"],
            width=3,
            height=1,
            padx=5,
            pady=3
        )
        
        # Add hover effects
        button.bind("<Enter>", lambda e, b=button: self._on_button_hover(b, True))
        button.bind("<Leave>", lambda e, b=button: self._on_button_hover(b, False))
        
        # Add drag start event
        button.bind("<ButtonPress-1>", lambda e, n=note: self._on_drag_start(e, n))
        
        return button
        
    def _on_button_hover(self, button: tk.Button, is_hover: bool):
        """Handle button hover effects"""
        if is_hover:
            button.config(bg=self.colors["bg_light"])
        else:
            button.config(bg=self.colors["bg_dark"])
            
    def _on_drag_start(self, event, note: str):
        """Handle the start of a drag operation"""
        # Create a Note object
        note_obj = Note(note + "4")  # Default to octave 4
        
        # Call the callback with the note and event info
        self.on_drag_start(note_obj, event) 