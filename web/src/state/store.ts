import { create } from 'zustand';
import { CHORD_TYPES } from '../data/chordFormulas';
import { SCALE_FORMULAS } from '../data/scaleFormulas';
import { TUNINGS, DEFAULT_TUNING } from '../data/tunings';
import { buildChord, Chord, triadNoteNames } from '../theory/chord';
import { buildScale, Scale } from '../theory/scale';
import { NoteName, parseNote } from '../theory/note';
import { noteAt } from '../theory/fretboard';

export type GameMode = 'normal' | 'notePlacement';
export type HighlightType = 'none' | 'triad' | 'seventh' | 'root' | 'all';

export interface DragState {
  note: NoteName;
  x: number;
  y: number;
}

export interface PlacedNote {
  string: number;
  fret: number;
  note: NoteName;
  correct?: boolean;
}

interface AppState {
  gameMode: GameMode;
  tuning: string;

  selectedRoot: NoteName;
  selectedChordType: string;
  selectedScaleType: string;

  currentChord: Chord | null;
  currentScale: Scale | null;
  highlight: HighlightType;

  placedNotes: PlacedNote[];
  validationMode: boolean;

  drag: DragState | null;
  dropHandler: ((clientX: number, clientY: number) => boolean) | null;

  // actions
  setGameMode: (mode: GameMode) => void;
  setTuning: (name: string) => void;
  setRoot: (name: NoteName) => void;
  setChordType: (name: string) => void;
  setScaleType: (name: string) => void;
  showChord: () => void;
  showScale: () => void;
  clearDisplay: () => void;
  setHighlight: (h: HighlightType) => void;
  toggleValidation: () => void;
  clearPlacedNotes: () => void;

  startDrag: (note: NoteName, x: number, y: number) => void;
  updateDrag: (x: number, y: number) => void;
  endDrag: () => void;
  dropNoteOnFret: (string: number, fret: number) => boolean;
  setDropHandler: (fn: ((clientX: number, clientY: number) => boolean) | null) => void;
}

export const useStore = create<AppState>((set, get) => ({
  gameMode: 'normal',
  tuning: DEFAULT_TUNING,

  selectedRoot: 'C',
  selectedChordType: 'Major',
  selectedScaleType: 'Major',

  currentChord: null,
  currentScale: null,
  highlight: 'none',

  placedNotes: [],
  validationMode: false,

  drag: null,
  dropHandler: null,

  setGameMode: (mode) => {
    set({ gameMode: mode });
    if (mode === 'normal') {
      set({ placedNotes: [] });
    }
    if (mode === 'notePlacement') {
      set({ placedNotes: [], currentChord: null, currentScale: null });
    }
  },

  setTuning: (name) => set({ tuning: name }),

  setRoot: (name) => {
    set({ selectedRoot: name });
    const s = get();
    if (s.gameMode !== 'normal') return;
    if (s.currentScale) s.showScale();
    else s.showChord();
  },
  setChordType: (name) => {
    set({ selectedChordType: name });
    if (get().gameMode === 'normal') get().showChord();
  },
  setScaleType: (name) => {
    set({ selectedScaleType: name });
    if (get().gameMode === 'normal') get().showScale();
  },

  showChord: () => {
    const { selectedRoot, selectedChordType } = get();
    const root = parseNote(`${selectedRoot}4`);
    set({ currentChord: buildChord(root, selectedChordType), currentScale: null });
  },
  showScale: () => {
    const { selectedRoot, selectedScaleType } = get();
    const root = parseNote(`${selectedRoot}4`);
    set({ currentScale: buildScale(root, selectedScaleType), currentChord: null });
  },
  clearDisplay: () =>
    set({ currentChord: null, currentScale: null, highlight: 'none', placedNotes: [] }),
  setHighlight: (h) => set({ highlight: h }),
  toggleValidation: () => set((s) => ({ validationMode: !s.validationMode })),
  clearPlacedNotes: () => set({ placedNotes: [] }),

  startDrag: (note, x, y) => set({ drag: { note, x, y } }),
  updateDrag: (x, y) =>
    set((s) => (s.drag ? { drag: { ...s.drag, x, y } } : {})),
  endDrag: () => set({ drag: null }),
  setDropHandler: (fn) => set({ dropHandler: fn }),

  dropNoteOnFret: (stringIdx, fret) => {
    const state = get();
    const drag = state.drag;
    if (!drag) return false;
    const tuning = TUNINGS[state.tuning];
    const actual = noteAt(tuning, stringIdx, fret);

    if (state.gameMode === 'notePlacement') {
      const isCorrect = actual.name === drag.note;
      if (state.validationMode && !isCorrect) return false;
      const filtered = state.placedNotes.filter(
        (p) => !(p.string === stringIdx && p.fret === fret),
      );
      set({
        placedNotes: [
          ...filtered,
          { string: stringIdx, fret, note: drag.note, correct: isCorrect },
        ],
      });
      return true;
    }

    return false;
  },
}));

export function highlightedNotes(
  chord: Chord | null,
  scale: Scale | null,
  h: HighlightType,
): NoteName[] {
  if (h === 'none') return [];
  if (chord) {
    if (h === 'root') return [chord.root.name];
    if (h === 'triad') return triadNoteNames(chord);
    if (h === 'seventh') {
      const sevIdx = chord.formula.findIndex((s, i) => i > 0 && (s === 10 || s === 11));
      return sevIdx > 0 ? [chord.notes[sevIdx].name] : [];
    }
    if (h === 'all') return chord.notes.map((n) => n.name);
  }
  if (scale) {
    if (h === 'root') return [scale.root.name];
    if (h === 'all') return scale.notes.map((n) => n.name);
  }
  return [];
}

export { CHORD_TYPES, SCALE_FORMULAS, TUNINGS };
