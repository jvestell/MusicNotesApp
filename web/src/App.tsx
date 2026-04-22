import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Fretboard } from './components/Fretboard';
import { NotePalette, DragGhost } from './components/NotePalette';
import { ControlPanel } from './components/ControlPanel';
import { InfoBar } from './components/InfoBar';
import { useElementSize } from './hooks/useElementSize';
import { useStore } from './state/store';

export default function App() {
  const { ref, width, height } = useElementSize<HTMLDivElement>();
  const gameMode = useStore((s) => s.gameMode);
  const showPalette = gameMode === 'notePlacement' || gameMode === 'triadFinder';

  // Seed a chord on first load for Explorer mode.
  useEffect(() => {
    if (gameMode === 'normal') {
      useStore.getState().showChord();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <div className="aurora-bg" />
      <div className="fixed inset-0 grid-noise opacity-[0.06] pointer-events-none" />

      <div className="min-h-screen flex flex-col px-4 md:px-8 pb-6">
        <Header />

        <div className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4 mt-4">
          {/* Main stage */}
          <div className="flex flex-col gap-3 min-w-0">
            <div className="glass rounded-2xl p-3 md:p-4">
              <InfoBar />
            </div>

            <div className="glass rounded-2xl p-2 md:p-3 relative">
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3"
              >
                <div
                  ref={ref}
                  className="flex-1 min-w-0"
                  style={{ aspectRatio: '16 / 5', minHeight: 260 }}
                >
                  {width > 0 && height > 0 && <Fretboard width={width} height={height} />}
                </div>

                {showPalette && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="w-[116px] shrink-0"
                  >
                    <NotePalette />
                  </motion.div>
                )}
              </motion.div>
            </div>

            <Footer />
          </div>

          {/* Sidebar */}
          <aside className="min-w-0">
            <ControlPanel />
          </aside>
        </div>
      </div>

      <DragGhost />
    </>
  );
}

function Header() {
  return (
    <header className="pt-5 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <Logo />
        <div>
          <div className="font-display text-xl md:text-2xl font-bold tracking-widest bg-gradient-to-r from-neon-cyan via-white to-neon-pink bg-clip-text text-transparent">
            NECKNAVIGATOR
          </div>
          <div className="text-[10px] font-display uppercase tracking-[0.35em] text-neon-cyan/70">
            Holographic Fretboard
          </div>
        </div>
      </div>
      <nav className="hidden md:flex gap-2">
        <a
          href="https://github.com"
          onClick={(e) => e.preventDefault()}
          className="btn-ghost"
        >
          About
        </a>
      </nav>
    </header>
  );
}

function Logo() {
  return (
    <div className="w-10 h-10 rounded-xl bg-ink-800 border border-neon-cyan/40 shadow-glow-cyan flex items-center justify-center">
      <svg viewBox="0 0 64 64" width="26" height="26">
        <g stroke="#00e5ff" strokeWidth="3" strokeLinecap="round">
          <line x1="10" y1="18" x2="54" y2="18" />
          <line x1="10" y1="32" x2="54" y2="32" />
          <line x1="10" y1="46" x2="54" y2="46" />
        </g>
        <circle cx="26" cy="32" r="5" fill="#39ff88" />
        <circle cx="42" cy="18" r="4" fill="#ff3ec8" />
      </svg>
    </div>
  );
}

function Footer() {
  return (
    <div className="text-[11px] text-slate-500 text-center pt-1">
      Tap the neck to hear a note · Space for chord playback coming soon ·{' '}
      <a
        className="text-neon-cyan/80 hover:text-neon-cyan"
        href="https://www.netlify.com/"
        target="_blank"
        rel="noreferrer"
      >
        Powered by Netlify
      </a>
    </div>
  );
}
