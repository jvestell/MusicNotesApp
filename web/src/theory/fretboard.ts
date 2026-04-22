import { Note, NoteName, parseNote, transpose, fromMidi, midiNumber } from './note';
import { TUNINGS } from '../data/tunings';

export interface FretPosition {
  string: number;
  fret: number;
}

/** Note at a given string (tuning index 0 = highest) and fret. */
export function noteAt(tuning: string[], stringIdx: number, fret: number): Note {
  const open = parseNote(tuning[stringIdx]);
  return transpose(open, fret);
}

/** Return every (string, fret) between minFret and maxFret whose note-name is in the set. */
export function findPositions(
  tuning: string[],
  noteNames: Iterable<NoteName>,
  minFret = 0,
  maxFret = 15,
): FretPosition[] {
  const target = new Set(noteNames);
  const out: FretPosition[] = [];
  for (let s = 0; s < tuning.length; s++) {
    for (let f = minFret; f <= maxFret; f++) {
      const n = noteAt(tuning, s, f);
      if (target.has(n.name)) out.push({ string: s, fret: f });
    }
  }
  return out;
}

export function getStandardTuning(): string[] {
  return TUNINGS.standard;
}

export { midiNumber, fromMidi };
