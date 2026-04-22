import * as Tone from 'tone';
import { Note, noteToString } from '../theory/note';

let synth: Tone.PolySynth | null = null;
let started = false;

function ensureSynth(): Tone.PolySynth {
  if (!synth) {
    synth = new Tone.PolySynth(Tone.Synth, {
      oscillator: { type: 'triangle' },
      envelope: { attack: 0.004, decay: 0.3, sustain: 0.25, release: 1.2 },
    }).toDestination();
    synth.volume.value = -8;
  }
  return synth;
}

async function ensureStarted(): Promise<void> {
  if (!started) {
    await Tone.start();
    started = true;
  }
}

export async function playNote(note: Note, duration = 0.9): Promise<void> {
  await ensureStarted();
  ensureSynth().triggerAttackRelease(noteToString(note), duration);
}

export async function playChord(notes: Note[], duration = 1.4): Promise<void> {
  await ensureStarted();
  ensureSynth().triggerAttackRelease(notes.map(noteToString), duration);
}

export async function playScale(notes: Note[], stepDur = 0.28): Promise<void> {
  await ensureStarted();
  const s = ensureSynth();
  const now = Tone.now();
  const ascending = [...notes];
  const descending = [...notes].reverse().slice(1);
  const seq = [...ascending, ...descending];
  seq.forEach((n, i) => {
    s.triggerAttackRelease(noteToString(n), stepDur * 0.9, now + i * stepDur);
  });
}
