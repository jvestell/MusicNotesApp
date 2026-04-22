import { create } from 'zustand';
import { CHORD_TYPES, TRIAD_QUIZ_TYPES } from '../data/chordFormulas';
import { SCALE_FORMULAS } from '../data/scaleFormulas';
import { TUNINGS, DEFAULT_TUNING } from '../data/tunings';
import { buildChord, Chord, chordName, getTriad, triadNoteNames } from '../theory/chord';
import { buildScale, Scale } from '../theory/scale';
import { NOTE_NAMES, NoteName, parseNote, Note } from '../theory/note';
import { findPositions, noteAt } from '../theory/fretboard';

export type GameMode = 'normal' | 'notePlacement' | 'triadFinder';
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
  correct?: boolean; // for validation mode
}

export interface TriadFinderState {
  active: boolean;
  phase: 0 | 1 | 2;
  chord: Chord | null;
  triadNotes: NoteName[];
  selectedNotes: Set<NoteName>;
  wrongNote: NoteName | null;
  targetPositions: Set<string>; // "s,f"
  foundPositions: Set<string>;
  completedFlash: boolean;
}

const posKey = (s: number, f: number) => `${s},${f}`;

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

  paletteFilter: NoteName[] | null;
  drag: DragState | null;
  dropHandler: ((clientX: number, clientY: number) => boolean) | null;

  triadFinder: TriadFinderState;

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

  startTriadFinder: () => void;
  stopTriadFinder: () => void;
  triadFinderSelectNote: (n: NoteName) => void;
}

function pickRandom<T>(arr: readonly T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
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

  paletteFilter: null,
  drag: null,
  dropHandler: null,

  triadFinder: {
    active: false,
    phase: 0,
    chord: null,
    triadNotes: [],
    selectedNotes: new Set(),
    wrongNote: null,
    targetPositions: new Set(),
    foundPositions: new Set(),
    completedFlash: false,
  },

  setGameMode: (mode) => {
    // stop triad finder if leaving
    const prev = get().gameMode;
    if (prev === 'triadFinder' && mode !== 'triadFinder') {
      get().stopTriadFinder();
    }
    set({ gameMode: mode });
    if (mode === 'normal') {
      set({ placedNotes: [], paletteFilter: null });
    }
    if (mode === 'notePlacement') {
      set({ placedNotes: [], paletteFilter: null, currentChord: null, currentScale: null });
    }
    if (mode === 'triadFinder') {
      set({ placedNotes: [], currentChord: null, currentScale: null });
      get().startTriadFinder();
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

    // Triad Finder phase 2
    if (state.gameMode === 'triadFinder' && state.triadFinder.phase === 2) {
      const key = posKey(stringIdx, fret);
      if (!state.triadFinder.targetPositions.has(key)) return false;
      if (state.triadFinder.foundPositions.has(key)) return false;
      if (actual.name !== drag.note) return false;
      const found = new Set(state.triadFinder.foundPositions);
      found.add(key);
      const allFound = found.size >= state.triadFinder.targetPositions.size;
      set({
        triadFinder: {
          ...state.triadFinder,
          foundPositions: found,
          completedFlash: allFound,
        },
      });
      if (allFound) {
        setTimeout(() => {
          get().startTriadFinder();
        }, 1400);
      }
      return true;
    }

    // Note Placement mode
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

  startTriadFinder: () => {
    const root = pickRandom(NOTE_NAMES);
    const chordType = pickRandom(TRIAD_QUIZ_TYPES);
    const chord = buildChord(parseNote(`${root}4`), chordType);
    const triad = triadNoteNames(chord);
    set({
      gameMode: 'triadFinder',
      paletteFilter: null,
      placedNotes: [],
      currentChord: chord,
      currentScale: null,
      triadFinder: {
        active: true,
        phase: 1,
        chord,
        triadNotes: triad,
        selectedNotes: new Set(),
        wrongNote: null,
        targetPositions: new Set(),
        foundPositions: new Set(),
        completedFlash: false,
      },
    });
  },

  stopTriadFinder: () => {
    set({
      paletteFilter: null,
      currentChord: null,
      triadFinder: {
        active: false,
        phase: 0,
        chord: null,
        triadNotes: [],
        selectedNotes: new Set(),
        wrongNote: null,
        targetPositions: new Set(),
        foundPositions: new Set(),
        completedFlash: false,
      },
    });
  },

  triadFinderSelectNote: (n) => {
    const { triadFinder, tuning } = get();
    if (!triadFinder.active || triadFinder.phase !== 1) return;
    if (triadFinder.selectedNotes.has(n)) return;
    if (!triadFinder.triadNotes.includes(n)) {
      // wrong-note flash
      set({ triadFinder: { ...triadFinder, wrongNote: n } });
      setTimeout(() => {
        const current = get().triadFinder;
        if (current.wrongNote === n) {
          set({ triadFinder: { ...current, wrongNote: null } });
        }
      }, 450);
      return;
    }
    const selected = new Set(triadFinder.selectedNotes);
    selected.add(n);
    if (selected.size >= 3) {
      const tuningArr = TUNINGS[tuning];
      const positions = findPositions(tuningArr, triadFinder.triadNotes, 1, 13);
      const targets = new Set(positions.map((p) => posKey(p.string, p.fret)));
      set({
        triadFinder: {
          ...triadFinder,
          selectedNotes: selected,
          phase: 2,
          targetPositions: targets,
          foundPositions: new Set(),
        },
        paletteFilter: triadFinder.triadNotes,
      });
    } else {
      set({ triadFinder: { ...triadFinder, selectedNotes: selected } });
    }
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
      // 10 or 11 semitones
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
export const posKeyFn = posKey;
