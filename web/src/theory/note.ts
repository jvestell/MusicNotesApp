export const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'] as const;
export type NoteName = (typeof NOTE_NAMES)[number];

export const NATURAL_NOTES: NoteName[] = ['C', 'D', 'E', 'F', 'G', 'A', 'B'];
export const SHARP_NOTES: NoteName[] = ['C#', 'D#', 'F#', 'G#', 'A#'];

const FLAT_TO_SHARP: Record<string, NoteName> = {
  Db: 'C#',
  Eb: 'D#',
  Gb: 'F#',
  Ab: 'G#',
  Bb: 'A#',
  Cb: 'B',
  Fb: 'E',
};

export interface Note {
  name: NoteName;
  octave: number;
}

export function parseNote(input: string): Note {
  const match = /^([A-Ga-g])([#b]?)(-?\d+)?$/.exec(input.trim());
  if (!match) throw new Error(`Invalid note: ${input}`);
  const letter = match[1].toUpperCase();
  const accidental = match[2];
  const octaveStr = match[3];
  const raw = `${letter}${accidental}`;
  let name: NoteName;
  if (accidental === 'b') {
    const normalized = FLAT_TO_SHARP[raw];
    if (!normalized) throw new Error(`Invalid flat: ${raw}`);
    name = normalized;
  } else {
    name = raw as NoteName;
  }
  if (!NOTE_NAMES.includes(name)) throw new Error(`Unknown note: ${name}`);
  const octave = octaveStr !== undefined ? parseInt(octaveStr, 10) : 4;
  return { name, octave };
}

export function noteToString(note: Note): string {
  return `${note.name}${note.octave}`;
}

export function midiNumber(note: Note): number {
  return (note.octave + 1) * 12 + NOTE_NAMES.indexOf(note.name);
}

export function fromMidi(midi: number): Note {
  const name = NOTE_NAMES[((midi % 12) + 12) % 12];
  const octave = Math.floor(midi / 12) - 1;
  return { name, octave };
}

export function transpose(note: Note, semitones: number): Note {
  return fromMidi(midiNumber(note) + semitones);
}

export function noteInterval(a: Note, b: Note): number {
  return midiNumber(b) - midiNumber(a);
}

export function sameName(a: Note, b: Note): boolean {
  return a.name === b.name;
}

export function notesEqual(a: Note, b: Note): boolean {
  return a.name === b.name && a.octave === b.octave;
}
