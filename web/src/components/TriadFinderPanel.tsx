import { AnimatePresence, motion } from 'framer-motion';
import { useStore } from '../state/store';
import { NATURAL_NOTES, SHARP_NOTES, NoteName } from '../theory/note';
import { chordName } from '../theory/chord';

export function TriadFinderPanel() {
  const tf = useStore((s) => s.triadFinder);
  const select = useStore((s) => s.triadFinderSelectNote);
  const restart = useStore((s) => s.startTriadFinder);
  const stop = useStore((s) => s.stopTriadFinder);
  const setGameMode = useStore((s) => s.setGameMode);

  const total = tf.targetPositions.size;
  const found = tf.foundPositions.size;
  const remaining = total - found;

  return (
    <div className="flex flex-col gap-3">
      {/* Chord target display */}
      <div className="rounded-xl p-3 border border-neon-cyan/30 bg-gradient-to-br from-neon-cyan/10 to-neon-violet/10 text-center">
        <div className="text-[10px] font-display tracking-[0.3em] uppercase text-neon-cyan/70">
          {tf.phase === 1 ? 'Identify the triad tones for' : 'Find every occurrence on the neck'}
        </div>
        <div className="font-display text-2xl font-bold text-white mt-1">
          {tf.chord ? chordName(tf.chord) : '—'}
        </div>
        {tf.phase === 2 && (
          <motion.div
            key={remaining}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="mt-1.5"
          >
            <span className="chip">
              {remaining === 0 ? 'Chord Complete!' : `Notes remaining: ${remaining}`}
            </span>
          </motion.div>
        )}
      </div>

      {/* Phase 1: 12 note buttons */}
      <AnimatePresence>
        {tf.phase === 1 && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="grid grid-cols-2 gap-2"
          >
            <div className="flex flex-col gap-1.5">
              {NATURAL_NOTES.map((n) => (
                <TFNoteButton key={n} note={n} tf={tf} onClick={() => select(n)} />
              ))}
            </div>
            <div className="flex flex-col gap-1.5">
              {SHARP_NOTES.map((n) => (
                <TFNoteButton key={n} note={n} tf={tf} onClick={() => select(n)} />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Phase 2 hint */}
      {tf.phase === 2 && (
        <div className="text-[11px] text-slate-400 leading-snug rounded-lg border border-white/10 bg-ink-800/40 p-3">
          Drag the three triad notes from the palette onto every fret where they appear
          (between frets 1–13). Correct drops lock in with a green glow.
        </div>
      )}

      {/* Controls */}
      <div className="flex gap-2">
        <button onClick={restart} className="btn flex-1">
          New Chord
        </button>
        <button
          onClick={() => {
            stop();
            setGameMode('normal');
          }}
          className="btn-ghost"
        >
          Exit Hunt
        </button>
      </div>
    </div>
  );
}

function TFNoteButton({
  note,
  tf,
  onClick,
}: {
  note: NoteName;
  tf: ReturnType<typeof useStore.getState>['triadFinder'];
  onClick: () => void;
}) {
  const selected = tf.selectedNotes.has(note);
  const wrong = tf.wrongNote === note;
  const disabled = tf.phase !== 1 || selected;

  let cls =
    'font-display font-bold text-base h-10 rounded-lg border transition-all ';
  if (wrong) {
    cls += 'bg-neon-red/30 border-neon-red text-white shadow-glow-red animate-pulse';
  } else if (selected) {
    cls += 'bg-neon-green/25 border-neon-green text-neon-green shadow-glow-green';
  } else {
    cls += 'bg-ink-700/70 border-neon-cyan/30 text-neon-cyan hover:bg-neon-cyan/15';
  }
  if (disabled && !wrong) cls += ' cursor-not-allowed opacity-70';

  return (
    <button onClick={onClick} disabled={disabled} className={cls}>
      {note}
    </button>
  );
}
