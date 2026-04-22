import { useStore, GameMode, HighlightType } from '../state/store';
import { NOTE_NAMES, NATURAL_NOTES, SHARP_NOTES, NoteName } from '../theory/note';
import { CHORD_TYPES } from '../data/chordFormulas';
import { UI_SCALE_TYPES } from '../data/scaleFormulas';
import { TUNING_LABELS } from '../data/tunings';
import { playChord, playScale } from '../audio/engine';

const GAME_MODES: Array<{ id: GameMode; label: string; blurb: string }> = [
  { id: 'normal', label: 'Explore', blurb: 'View chords & scales on the neck' },
  { id: 'notePlacement', label: 'Note Drop', blurb: 'Drag notes onto the fretboard' },
];

const HIGHLIGHTS: Array<{ id: HighlightType; label: string }> = [
  { id: 'none', label: 'All Tones' },
  { id: 'triad', label: 'Triad' },
  { id: 'seventh', label: '7th' },
  { id: 'root', label: 'Root Only' },
];

export function ControlPanel() {
  const gameMode = useStore((s) => s.gameMode);
  const setGameMode = useStore((s) => s.setGameMode);
  const selectedRoot = useStore((s) => s.selectedRoot);
  const setRoot = useStore((s) => s.setRoot);
  const selectedChordType = useStore((s) => s.selectedChordType);
  const setChordType = useStore((s) => s.setChordType);
  const selectedScaleType = useStore((s) => s.selectedScaleType);
  const setScaleType = useStore((s) => s.setScaleType);
  const showChord = useStore((s) => s.showChord);
  const showScale = useStore((s) => s.showScale);
  const clearDisplay = useStore((s) => s.clearDisplay);
  const highlight = useStore((s) => s.highlight);
  const setHighlight = useStore((s) => s.setHighlight);
  const validationMode = useStore((s) => s.validationMode);
  const toggleValidation = useStore((s) => s.toggleValidation);
  const clearPlacedNotes = useStore((s) => s.clearPlacedNotes);
  const tuning = useStore((s) => s.tuning);
  const setTuning = useStore((s) => s.setTuning);
  const currentChord = useStore((s) => s.currentChord);
  const currentScale = useStore((s) => s.currentScale);

  return (
    <div className="glass rounded-2xl p-4 flex flex-col gap-4 h-full overflow-y-auto">
      {/* Mode Switcher */}
      <div>
        <Label>Game Mode</Label>
        <div className="grid grid-cols-2 gap-2">
          {GAME_MODES.map((m) => (
            <button
              key={m.id}
              onClick={() => setGameMode(m.id)}
              className={`btn !py-2.5 ${gameMode === m.id ? 'btn-active' : ''}`}
              title={m.blurb}
            >
              {m.label}
            </button>
          ))}
        </div>
        <div className="text-[11px] text-slate-400 mt-1.5">
          {GAME_MODES.find((m) => m.id === gameMode)?.blurb}
        </div>
      </div>

      {/* Root */}
          <div>
            <Label>Root Note</Label>
            <div className="grid grid-cols-7 gap-1.5">
              {NATURAL_NOTES.map((n) => (
                <NoteBtn
                  key={n}
                  note={n}
                  active={selectedRoot === n}
                  onClick={() => setRoot(n)}
                />
              ))}
            </div>
            <div className="grid grid-cols-7 gap-1.5 mt-1.5">
              <div />
              {SHARP_NOTES.map((n) => (
                <NoteBtn
                  key={n}
                  note={n}
                  active={selectedRoot === n}
                  onClick={() => setRoot(n)}
                  sharp
                />
              ))}
              <div />
            </div>
          </div>

          {/* Chord Types */}
          <div>
            <Label>Chord Type</Label>
            <div className="grid grid-cols-5 gap-1.5">
              {CHORD_TYPES.map((t) => (
                <button
                  key={t}
                  onClick={() => setChordType(t)}
                  className={`btn !text-[10px] !px-1.5 !py-1.5 ${selectedChordType === t ? 'btn-active' : ''}`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Scale Types */}
          <div>
            <Label>Scale Type</Label>
            <div className="grid grid-cols-3 gap-1.5">
              {UI_SCALE_TYPES.map((t) => (
                <button
                  key={t}
                  onClick={() => setScaleType(t)}
                  className={`btn !text-[10px] !px-1.5 !py-1.5 ${selectedScaleType === t ? 'btn-active' : ''}`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => {
                showChord();
              }}
              className="btn !py-2.5 !text-sm bg-gradient-to-br from-neon-cyan/25 to-neon-violet/25 border-neon-cyan/70"
            >
              Show Chord
            </button>
            <button
              onClick={() => {
                showScale();
              }}
              className="btn !py-2.5 !text-sm bg-gradient-to-br from-neon-pink/25 to-neon-violet/25 border-neon-pink/70"
            >
              Show Scale
            </button>
            <button
              onClick={() => {
                if (currentChord) void playChord(currentChord.notes);
              }}
              disabled={!currentChord}
              className="btn disabled:opacity-40"
            >
              ▶ Play Chord
            </button>
            <button
              onClick={() => {
                if (currentScale) void playScale(currentScale.notes);
              }}
              disabled={!currentScale}
              className="btn disabled:opacity-40"
            >
              ▶ Play Scale
            </button>
          </div>

          {/* Highlight */}
          <div>
            <Label>Highlight</Label>
            <div className="grid grid-cols-4 gap-1.5">
              {HIGHLIGHTS.map((h) => (
                <button
                  key={h.id}
                  onClick={() => setHighlight(h.id)}
                  className={`btn !text-[10px] !px-1.5 ${highlight === h.id ? 'btn-active' : ''}`}
                >
                  {h.label}
                </button>
              ))}
            </div>
          </div>

          {/* Note Placement controls */}
          {gameMode === 'notePlacement' && (
            <div className="border-t border-white/10 pt-3 flex flex-col gap-2">
              <label className="flex items-center gap-2 text-xs text-slate-300 select-none">
                <input
                  type="checkbox"
                  checked={validationMode}
                  onChange={toggleValidation}
                  className="accent-neon-cyan w-4 h-4"
                />
                <span>
                  Validation mode{' '}
                  <span className="text-slate-500">(block wrong placements)</span>
                </span>
              </label>
              <button onClick={clearPlacedNotes} className="btn">
                Clear Placed Notes
              </button>
              <div className="text-[11px] text-slate-400 leading-snug">
                Tip: pick a chord or scale first, then try to place every matching note.
              </div>
            </div>
          )}

      <button onClick={clearDisplay} className="btn-ghost w-fit">
        Clear display
      </button>

      {/* Tuning */}
      <div className="border-t border-white/10 pt-3">
        <Label>Tuning</Label>
        <select
          value={tuning}
          onChange={(e) => setTuning(e.target.value)}
          className="w-full bg-ink-700/70 border border-neon-cyan/30 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-neon-cyan"
        >
          {Object.entries(TUNING_LABELS).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-[10px] font-display uppercase tracking-[0.3em] text-neon-cyan/80 mb-1.5">
      {children}
    </div>
  );
}

function NoteBtn({
  note,
  active,
  onClick,
  sharp,
}: {
  note: NoteName;
  active: boolean;
  onClick: () => void;
  sharp?: boolean;
}) {
  void NOTE_NAMES;
  return (
    <button
      onClick={onClick}
      className={`font-display font-semibold text-sm h-9 rounded-md border transition-all ${
        active
          ? 'bg-gradient-to-br from-neon-cyan/40 to-neon-pink/40 border-neon-cyan text-white shadow-glow-cyan'
          : sharp
            ? 'bg-ink-800/80 border-white/15 text-slate-200 hover:border-neon-pink/60'
            : 'bg-ink-700/70 border-white/15 text-slate-100 hover:border-neon-cyan/60'
      }`}
    >
      {note}
    </button>
  );
}
