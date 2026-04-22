# NeckNavigator — Web

A browser-first rebuild of the Python/tkinter NeckNavigator guitar-theory explorer.
Same music theory, same three game modes, holographic new look.

## Stack
- **Vite + React + TypeScript**
- **Tailwind CSS** for the holographic-neon theme
- **Framer Motion** for micro-animations
- **Tone.js** for in-browser audio
- **Zustand** for global state
- Deploys to **Netlify** as a static site

## Local dev

```bash
cd web
npm install
npm run dev
```

## Production build

```bash
npm run build
npm run preview
```

## Deploying to Netlify

The root `netlify.toml` already points at `web/` with `npm run build` → `web/dist`.
Connect the repo in Netlify and it should deploy without further config.

## Game modes

1. **Explorer** — pick a root + chord/scale, see it on the neck. Highlight triad / 7th / root.
2. **Note Drop** — drag notes from the palette onto any fret. Optional validation mode locks out wrong placements.
3. **Triad Hunt** — a random chord is drawn; pick its three triad tones, then drag them onto every fret where they appear. Auto-advances.

## Layout mirror (from the Python app)

| Python                              | Web                                        |
|-------------------------------------|--------------------------------------------|
| `core/note_system.py`               | `src/theory/note.ts`                       |
| `core/chord_system.py`              | `src/theory/chord.ts`                      |
| `core/scale_system.py`              | `src/theory/scale.ts`                      |
| `core/music_theory.py`              | inlined in theory + `src/state/store.ts`   |
| `data/chord_formulas.json`          | `src/data/chordFormulas.ts`                |
| `data/scale_formulas.json`          | `src/data/scaleFormulas.ts`                |
| `data/tunings.json`                 | `src/data/tunings.ts`                      |
| `ui/fretboard.py`                   | `src/components/Fretboard.tsx`             |
| `ui/control_panel.py`               | `src/components/ControlPanel.tsx`          |
| `ui/note_palette.py`                | `src/components/NotePalette.tsx`           |
| triad-finder state machine          | `src/state/store.ts` + `TriadFinderPanel`  |
| `utils/audio_engine.py` (pygame)    | `src/audio/engine.ts` (Tone.js)            |
