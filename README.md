# NEON FRETBOARD - Cyberpunk Guitar Theory Explorer

A visual learning tool for guitar music theory with a cyberpunk aesthetic. This application helps guitarists learn scales, chords, and their relationships through an interactive interface.

## Features

- Interactive fretboard visualization
- Scale and chord construction
- Scale-chord relationship analysis
- Chord position finder
- Ear training exercises
- Cyberpunk-themed UI

## Requirements

- Python 3.8 or higher
- Tkinter (usually comes with Python)
- Pygame
- Pillow
- NumPy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GuitarTheoryApp.git
cd GuitarTheoryApp
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure you're in the project directory and your virtual environment is activated.

2. Run the main script:
```bash
python main.py
```

## Usage

- Use the control panel to select scales and chords
- Click on the fretboard to see note names and intervals
- Use the visualizers to explore different aspects of music theory
- Keyboard shortcuts:
  - Ctrl+N: New session
  - Ctrl+S: Save configuration
  - Ctrl+O: Load configuration
  - F1: Show chord builder
  - F2: Show scale-chord relationships
  - F3: Show ear trainer

## Project Structure

```
GuitarTheoryApp/
├── core/               # Core music theory implementation
│   ├── note_system.py
│   ├── chord_system.py
│   ├── scale_system.py
│   └── music_theory.py
├── ui/                 # User interface components
│   ├── main_window.py
│   ├── fretboard.py
│   ├── control_panel.py
│   └── visualizers/
├── data/              # JSON data files
│   ├── chord_formulas.json
│   ├── scale_formulas.json
│   └── tunings.json
├── utils/             # Utility functions
├── main.py           # Application entry point
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 