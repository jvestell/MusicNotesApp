import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useStore } from '../state/store';
import { NATURAL_NOTES, SHARP_NOTES, NoteName } from '../theory/note';

export function NotePalette() {
  const filter = useStore((s) => s.paletteFilter);
  const drag = useStore((s) => s.drag);
  const startDrag = useStore((s) => s.startDrag);
  const updateDrag = useStore((s) => s.updateDrag);
  const endDrag = useStore((s) => s.endDrag);

  useEffect(() => {
    if (!drag) return;
    document.body.classList.add('dragging');
    const move = (e: PointerEvent) => updateDrag(e.clientX, e.clientY);
    const up = (e: PointerEvent) => {
      const handler = useStore.getState().dropHandler;
      if (handler) handler(e.clientX, e.clientY);
      endDrag();
    };
    const cancel = () => endDrag();
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up);
    window.addEventListener('pointercancel', cancel);
    return () => {
      document.body.classList.remove('dragging');
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', up);
      window.removeEventListener('pointercancel', cancel);
    };
  }, [drag, updateDrag, endDrag]);

  const showNote = (n: NoteName) => !filter || filter.includes(n);

  return (
    <div className="glass rounded-2xl p-3 flex flex-col gap-2">
      <div className="text-[10px] font-display uppercase tracking-[0.3em] text-neon-cyan/80 text-center pt-1">
        Note Palette
      </div>
      <div className="grid grid-cols-2 gap-1.5">
        <div className="flex flex-col gap-1.5">
          {NATURAL_NOTES.map((n) => (
            <PaletteButton key={n} note={n} visible={showNote(n)} onDrag={startDrag} />
          ))}
        </div>
        <div className="flex flex-col gap-1.5">
          {SHARP_NOTES.map((n) => (
            <PaletteButton key={n} note={n} visible={showNote(n)} onDrag={startDrag} />
          ))}
        </div>
      </div>
      <div className="text-[10px] text-slate-400/70 text-center pt-1 leading-tight">
        Drag onto the neck
      </div>
    </div>
  );
}

function PaletteButton({
  note,
  visible,
  onDrag,
}: {
  note: NoteName;
  visible: boolean;
  onDrag: (n: NoteName, x: number, y: number) => void;
}) {
  return (
    <motion.button
      whileHover={{ scale: visible ? 1.04 : 1 }}
      whileTap={{ scale: 0.95 }}
      disabled={!visible}
      onPointerDown={(e) => {
        if (!visible) return;
        e.preventDefault();
        onDrag(note, e.clientX, e.clientY);
      }}
      style={{ touchAction: 'none' }}
      className={`font-display font-bold text-lg h-10 rounded-lg border transition-all ${
        visible
          ? 'bg-ink-700/70 border-neon-cyan/40 text-neon-cyan hover:bg-neon-cyan/15 hover:shadow-glow-cyan cursor-grab'
          : 'bg-ink-800/40 border-white/5 text-slate-600 cursor-not-allowed opacity-40'
      }`}
    >
      {note}
    </motion.button>
  );
}

export function DragGhost() {
  const drag = useStore((s) => s.drag);
  if (!drag) return null;
  return (
    <div
      className="pointer-events-none fixed z-50 -translate-x-1/2 -translate-y-1/2"
      style={{ left: drag.x, top: drag.y }}
    >
      <div className="font-display font-bold text-lg h-12 w-12 rounded-full flex items-center justify-center border-2 border-neon-cyan text-neon-cyan bg-ink-800/90 shadow-glow-cyan">
        {drag.note}
      </div>
    </div>
  );
}
