import { CHORD_FORMULAS } from '../data/chordFormulas';
import { Note, NoteName, transpose } from './note';

export interface Chord {
  root: Note;
  chordType: string;
  formula: number[];
  notes: Note[];
}

export function buildChord(root: Note, chordType: string): Chord {
  const formula = CHORD_FORMULAS[chordType];
  if (!formula) throw new Error(`Unknown chord type: ${chordType}`);
  const notes = formula.map((semis) => transpose(root, semis));
  return { root, chordType, formula, notes };
}

export function chordName(chord: Chord): string {
  return `${chord.root.name} ${chord.chordType}`;
}

export function chordContainsNote(chord: Chord, noteName: NoteName): boolean {
  return chord.notes.some((n) => n.name === noteName);
}

/**
 * Return up to 3 triad tones: root, third/second/fourth, fifth.
 * Mirrors Python core/chord_system.py Chord.get_triad.
 */
export function getTriad(chord: Chord): Note[] {
  const out: Note[] = [chord.notes[0]]; // root
  const formula = chord.formula;
  const chordType = chord.chordType.toLowerCase();

  if (chordType.includes('sus2')) {
    const idx = formula.indexOf(2);
    if (idx > 0) out.push(chord.notes[idx]);
  } else if (chordType.includes('sus4')) {
    const idx = formula.indexOf(5);
    if (idx > 0) out.push(chord.notes[idx]);
  } else {
    const thirdIdx = formula.findIndex((s, i) => i > 0 && (s === 3 || s === 4));
    if (thirdIdx > 0) out.push(chord.notes[thirdIdx]);
  }

  const fifthIdx = formula.findIndex((s, i) => i > 0 && (s === 6 || s === 7 || s === 8));
  if (fifthIdx > 0) out.push(chord.notes[fifthIdx]);

  return out;
}

export function triadNoteNames(chord: Chord): NoteName[] {
  const seen = new Set<NoteName>();
  const out: NoteName[] = [];
  for (const n of getTriad(chord)) {
    if (!seen.has(n.name)) {
      seen.add(n.name);
      out.push(n.name);
    }
  }
  return out;
}
