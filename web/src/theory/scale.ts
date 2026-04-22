import { SCALE_FORMULAS } from '../data/scaleFormulas';
import { Note, NoteName, transpose } from './note';

export interface Scale {
  root: Note;
  scaleType: string;
  formula: number[];
  notes: Note[];
}

export function buildScale(root: Note, scaleType: string): Scale {
  const formula = SCALE_FORMULAS[scaleType];
  if (!formula) throw new Error(`Unknown scale type: ${scaleType}`);
  const notes = formula.map((semis) => transpose(root, semis));
  return { root, scaleType, formula, notes };
}

export function scaleName(scale: Scale): string {
  return `${scale.root.name} ${scale.scaleType}`;
}

export function scaleContainsNote(scale: Scale, name: NoteName): boolean {
  return scale.notes.some((n) => n.name === name);
}
