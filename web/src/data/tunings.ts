export const TUNINGS: Record<string, string[]> = {
  standard: ['E4', 'B3', 'G3', 'D3', 'A2', 'E2'],
  drop_d: ['E4', 'B3', 'G3', 'D3', 'A2', 'D2'],
  half_step_down: ['D#4', 'A#3', 'F#3', 'C#3', 'G#2', 'D#2'],
  full_step_down: ['D4', 'A3', 'F3', 'C3', 'G2', 'D2'],
  dadgad: ['D4', 'A3', 'G3', 'D3', 'A2', 'D2'],
  open_d: ['D4', 'A3', 'F#3', 'D3', 'A2', 'D2'],
  open_g: ['D4', 'B3', 'G3', 'D3', 'G2', 'D2'],
  open_e: ['E4', 'B3', 'G#3', 'E3', 'B2', 'E2'],
};

export const TUNING_LABELS: Record<string, string> = {
  standard: 'Standard (E A D G B E)',
  drop_d: 'Drop D',
  half_step_down: 'Half Step Down',
  full_step_down: 'Whole Step Down',
  dadgad: 'DADGAD',
  open_d: 'Open D',
  open_g: 'Open G',
  open_e: 'Open E',
};

export const DEFAULT_TUNING = 'standard';
