import { useStore } from '../state/store';
import { chordName } from '../theory/chord';
import { scaleName } from '../theory/scale';

export function InfoBar() {
  const chord = useStore((s) => s.currentChord);
  const scale = useStore((s) => s.currentScale);
  const gameMode = useStore((s) => s.gameMode);
  const placed = useStore((s) => s.placedNotes);

  return (
    <div className="flex flex-wrap items-center gap-2 text-[11px] font-display uppercase tracking-[0.2em]">
      {chord && (
        <span className="chip">
          {chordName(chord)} · {chord.notes.map((n) => n.name).join(' · ')}
        </span>
      )}
      {scale && (
        <span className="chip">
          {scaleName(scale)} · {scale.notes.map((n) => n.name).join(' · ')}
        </span>
      )}
      {gameMode === 'notePlacement' && (
        <span className="chip">Placed: {placed.length}</span>
      )}
      {!chord && !scale && gameMode === 'normal' && (
        <span className="text-slate-500 normal-case tracking-normal text-xs">
          Pick a root and chord/scale, then hit <b>Show Chord</b>.
        </span>
      )}
    </div>
  );
}
