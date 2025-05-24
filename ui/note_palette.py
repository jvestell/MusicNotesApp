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
        
        # Track drag state
        self.drag_data = {
            "widget": None,
            "note": None,
            "x": 0,
            "y": 0
        }
        
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
        
        # Add drag and drop events
        button.bind("<ButtonPress-1>", lambda e, n=note: self._on_button_press(e, n))
        button.bind("<B1-Motion>", self._on_button_drag)
        button.bind("<ButtonRelease-1>", self._on_button_release)
        
        return button
        
    def _on_button_hover(self, button: tk.Button, is_hover: bool):
        """Handle button hover effects"""
        if is_hover:
            button.config(bg=self.colors["bg_light"])
        else:
            button.config(bg=self.colors["bg_dark"])
            
    def _on_button_press(self, event, note: str):
        """Handle the start of a drag operation from a button"""
        # Store the widget and note being dragged
        self.drag_data["widget"] = event.widget
        self.drag_data["note"] = Note(note + "4")  # Default to octave 4
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
        
        # Create a custom event for the fretboard
        custom_event = type('CustomEvent', (), {
            'x': event.x_root,
            'y': event.y_root,
            'note': self.drag_data["note"]
        })
        
        # Start the drag operation on the fretboard
        self.on_drag_start(self.drag_data["note"], custom_event)
        
    def _on_button_drag(self, event):
        """Handle dragging of a note button"""
        if self.drag_data["widget"] is None:
            return
            
        # Create a custom event for the fretboard
        custom_event = type('CustomEvent', (), {
            'x': event.x_root,
            'y': event.y_root,
            'note': self.drag_data["note"]
        })
        
        # Update the drag operation on the fretboard
        self.on_drag_start(self.drag_data["note"], custom_event)
        
    def _on_button_release(self, event):
        """Handle the end of a drag operation"""
        if self.drag_data["widget"] is None:
            return
            
        # Create a custom event for the fretboard
        custom_event = type('CustomEvent', (), {
            'x': event.x_root,
            'y': event.y_root,
            'note': self.drag_data["note"]
        })
        
        # End the drag operation on the fretboard
        self.on_drag_start(self.drag_data["note"], custom_event)
        
        # Reset drag data
        self.drag_data = {
            "widget": None,
            "note": None,
            "x": 0,
            "y": 0
        } 