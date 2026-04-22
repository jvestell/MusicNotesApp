import { useEffect, useMemo, useRef, useState } from 'react';
import { useStore, highlightedNotes } from '../state/store';
import { noteAt } from '../theory/fretboard';
import { TUNINGS } from '../data/tunings';
import { NoteName } from '../theory/note';
import { playNote } from '../audio/engine';

const FRETS = 15;
const STRINGS = 6;
const FRET_MARKER_SINGLE = [3, 5, 7, 9];
const FRET_MARKER_DOUBLE = [12];

interface Props {
  width: number;
  height: number;
}

export function Fretboard({ width, height }: Props) {
  const tuningName = useStore((s) => s.tuning);
  const tuning = TUNINGS[tuningName];
  const currentChord = useStore((s) => s.currentChord);
  const currentScale = useStore((s) => s.currentScale);
  const highlight = useStore((s) => s.highlight);
  const placedNotes = useStore((s) => s.placedNotes);
  const gameMode = useStore((s) => s.gameMode);
  const drag = useStore((s) => s.drag);
  const dropNoteOnFret = useStore((s) => s.dropNoteOnFret);
  const endDrag = useStore((s) => s.endDrag);
  const setDropHandler = useStore((s) => s.setDropHandler);

  const svgRef = useRef<SVGSVGElement | null>(null);
  const [hover, setHover] = useState<{ s: number; f: number } | null>(null);

  // Geometry
  const nutX = Math.max(46, width * 0.05);
  const boardX0 = nutX;
  const boardX1 = width - 16;
  const boardY0 = 36;
  const boardY1 = height - 36;
  const boardW = boardX1 - boardX0;
  const boardH = boardY1 - boardY0;
  const fretSpacing = boardW / FRETS;
  const stringSpacing = boardH / (STRINGS - 1);

  const stringY = (s: number) => boardY0 + s * stringSpacing;
  const fretCenterX = (f: number) =>
    f === 0 ? boardX0 - nutX / 2 + 14 : boardX0 + (f - 0.5) * fretSpacing;
  const fretLineX = (f: number) => boardX0 + f * fretSpacing;

  // Which note-names to show
  const displayedNoteNames = useMemo<Set<NoteName>>(() => {
    const out = new Set<NoteName>();
    if (currentChord) currentChord.notes.forEach((n) => out.add(n.name));
    if (currentScale) currentScale.notes.forEach((n) => out.add(n.name));
    return out;
  }, [currentChord, currentScale]);

  const highlightSet = useMemo<Set<NoteName>>(() => {
    return new Set(highlightedNotes(currentChord, currentScale, highlight));
  }, [currentChord, currentScale, highlight]);

  const rootName: NoteName | null =
    currentChord?.root.name ?? currentScale?.root.name ?? null;

  // Positions to render (from displayed notes)
  const displayedPositions = useMemo(() => {
    const out: Array<{ string: number; fret: number; name: NoteName; isRoot: boolean; isHighlighted: boolean }> = [];
    if (gameMode === 'notePlacement') return out;
    if (displayedNoteNames.size === 0) return out;
    for (let s = 0; s < STRINGS; s++) {
      for (let f = 0; f <= FRETS; f++) {
        const n = noteAt(tuning, s, f);
        if (displayedNoteNames.has(n.name)) {
          const isRoot = rootName === n.name;
          const showAsHighlight = highlight === 'none' ? false : highlightSet.has(n.name);
          const shouldShow = highlight === 'none' || showAsHighlight;
          if (shouldShow) {
            out.push({ string: s, fret: f, name: n.name, isRoot, isHighlighted: showAsHighlight });
          }
        }
      }
    }
    return out;
  }, [displayedNoteNames, tuning, gameMode, highlight, highlightSet, rootName]);

  // Convert client coords → (string, fret) on the board. Returns null if outside.
  function posFromClient(clientX: number, clientY: number): { s: number; f: number } | null {
    const svg = svgRef.current;
    if (!svg) return null;
    const rect = svg.getBoundingClientRect();
    if (
      clientX < rect.left ||
      clientX > rect.right ||
      clientY < rect.top ||
      clientY > rect.bottom
    ) {
      return null;
    }
    const scaleX = width / rect.width;
    const scaleY = height / rect.height;
    const x = (clientX - rect.left) * scaleX;
    const y = (clientY - rect.top) * scaleY;

    if (y < boardY0 - stringSpacing / 2 || y > boardY1 + stringSpacing / 2) return null;
    const s = Math.max(0, Math.min(STRINGS - 1, Math.round((y - boardY0) / stringSpacing)));

    if (x < boardX0 - nutX) return null;
    if (x < boardX0) return { s, f: 0 };
    if (x > boardX1) return null;
    const f = Math.max(1, Math.min(FRETS, Math.floor((x - boardX0) / fretSpacing) + 1));
    return { s, f };
  }

  function onPointerDown(e: React.PointerEvent) {
    if (drag) return;
    const p = posFromClient(e.clientX, e.clientY);
    if (!p) return;
    const n = noteAt(tuning, p.s, p.f);
    void playNote(n);
  }

  function onPointerMove(e: React.PointerEvent) {
    const p = posFromClient(e.clientX, e.clientY);
    setHover(p);
  }

  function onPointerLeave() {
    setHover(null);
  }

  // Register a global drop handler so drops from the palette commit here
  // regardless of which element received the pointerup (implicit touch capture, etc.)
  useEffect(() => {
    const handler = (cx: number, cy: number): boolean => {
      const p = posFromClient(cx, cy);
      if (!p) return false;
      const ok = dropNoteOnFret(p.s, p.f);
      if (ok) {
        const n = noteAt(tuning, p.s, p.f);
        void playNote(n);
      }
      return ok;
    };
    setDropHandler(handler);
    return () => setDropHandler(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [width, height, tuning, dropNoteOnFret, setDropHandler]);

  return (
    <div className="relative w-full h-full" style={{ userSelect: 'none' }}>
      <svg
        ref={svgRef}
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        height="100%"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerLeave={onPointerLeave}
        style={{ touchAction: 'none' }}
      >
        <defs>
          <linearGradient id="board-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#18122b" />
            <stop offset="0.5" stopColor="#0d0a1c" />
            <stop offset="1" stopColor="#18122b" />
          </linearGradient>
          <linearGradient id="nut-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#c9d6ff" />
            <stop offset="0.5" stopColor="#f6f8ff" />
            <stop offset="1" stopColor="#8a97c6" />
          </linearGradient>
          <radialGradient id="dot-accent" cx="0.3" cy="0.3" r="0.8">
            <stop offset="0" stopColor="#7affd8" />
            <stop offset="0.45" stopColor="#39ff88" />
            <stop offset="1" stopColor="#0a5c35" />
          </radialGradient>
          <radialGradient id="dot-root" cx="0.3" cy="0.3" r="0.8">
            <stop offset="0" stopColor="#ffd0e4" />
            <stop offset="0.45" stopColor="#ff5072" />
            <stop offset="1" stopColor="#6a0a24" />
          </radialGradient>
          <radialGradient id="dot-cyan" cx="0.3" cy="0.3" r="0.8">
            <stop offset="0" stopColor="#d4faff" />
            <stop offset="0.45" stopColor="#00e5ff" />
            <stop offset="1" stopColor="#083a4a" />
          </radialGradient>
          <radialGradient id="dot-target" cx="0.5" cy="0.5" r="0.7">
            <stop offset="0" stopColor="rgba(0,229,255,0.35)" />
            <stop offset="1" stopColor="rgba(0,229,255,0)" />
          </radialGradient>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Board background */}
        <rect
          x={boardX0 - nutX}
          y={boardY0 - 14}
          width={boardW + nutX + 16}
          height={boardH + 28}
          rx={12}
          fill="url(#board-grad)"
          stroke="rgba(0,229,255,0.22)"
        />

        {/* Fret markers (inlays) */}
        {FRET_MARKER_SINGLE.map((f) => (
          <circle
            key={`mk-${f}`}
            cx={fretCenterX(f)}
            cy={(boardY0 + boardY1) / 2}
            r={Math.min(fretSpacing * 0.15, 6)}
            fill="rgba(0,229,255,0.18)"
            stroke="rgba(0,229,255,0.35)"
          />
        ))}
        {FRET_MARKER_DOUBLE.map((f) => (
          <g key={`mk2-${f}`}>
            <circle
              cx={fretCenterX(f)}
              cy={boardY0 + boardH * 0.3}
              r={Math.min(fretSpacing * 0.15, 6)}
              fill="rgba(255,62,200,0.22)"
              stroke="rgba(255,62,200,0.45)"
            />
            <circle
              cx={fretCenterX(f)}
              cy={boardY0 + boardH * 0.7}
              r={Math.min(fretSpacing * 0.15, 6)}
              fill="rgba(255,62,200,0.22)"
              stroke="rgba(255,62,200,0.45)"
            />
          </g>
        ))}

        {/* Nut */}
        <rect
          x={boardX0 - 6}
          y={boardY0 - 8}
          width={6}
          height={boardH + 16}
          fill="url(#nut-grad)"
          rx={2}
        />

        {/* Frets */}
        {Array.from({ length: FRETS + 1 }, (_, f) => (
          <line
            key={`fret-${f}`}
            x1={fretLineX(f)}
            x2={fretLineX(f)}
            y1={boardY0 - 6}
            y2={boardY1 + 6}
            stroke={f === 0 ? 'transparent' : 'rgba(180, 190, 230, 0.45)'}
            strokeWidth={1.5}
          />
        ))}

        {/* Fret numbers */}
        {Array.from({ length: FRETS }, (_, i) => {
          const f = i + 1;
          return (
            <text
              key={`fn-${f}`}
              x={fretCenterX(f)}
              y={boardY1 + 22}
              fill="rgba(140, 160, 200, 0.7)"
              fontSize={10}
              textAnchor="middle"
              fontFamily="Orbitron, sans-serif"
            >
              {f}
            </text>
          );
        })}

        {/* Strings */}
        {Array.from({ length: STRINGS }, (_, s) => {
          const thickness = 1 + (STRINGS - 1 - s) * 0.45;
          return (
            <line
              key={`s-${s}`}
              x1={boardX0 - nutX + 20}
              x2={boardX1}
              y1={stringY(s)}
              y2={stringY(s)}
              stroke="rgba(200,210,240,0.85)"
              strokeWidth={thickness}
            />
          );
        })}

        {/* String labels (open tuning) */}
        {tuning.map((n, s) => (
          <text
            key={`lbl-${s}`}
            x={boardX0 - nutX + 6}
            y={stringY(s) + 4}
            fontFamily="Orbitron, sans-serif"
            fontSize={11}
            fill="#ff3ec8"
            textAnchor="start"
          >
            {n.replace(/\d+$/, '')}
          </text>
        ))}

        {/* Displayed chord/scale notes */}
        {displayedPositions.map(({ string, fret, name, isRoot, isHighlighted }) => {
          const r = Math.min(fretSpacing, stringSpacing) * 0.38;
          const fill = isRoot ? 'url(#dot-root)' : isHighlighted ? 'url(#dot-accent)' : 'url(#dot-cyan)';
          const ring = isRoot ? 'rgba(255,80,114,0.9)' : isHighlighted ? 'rgba(57,255,136,0.8)' : 'rgba(0,229,255,0.7)';
          return (
            <g key={`dn-${string}-${fret}`} filter="url(#glow)">
              <circle
                cx={fretCenterX(fret)}
                cy={stringY(string)}
                r={r}
                fill={fill}
                stroke={ring}
                strokeWidth={1.5}
              />
              <text
                x={fretCenterX(fret)}
                y={stringY(string) + 4}
                textAnchor="middle"
                fontFamily="Orbitron, sans-serif"
                fontSize={11}
                fontWeight={700}
                fill="#05060d"
              >
                {name}
              </text>
            </g>
          );
        })}

        {/* Placed notes (note placement mode) */}
        {gameMode === 'notePlacement' &&
          placedNotes.map((p) => {
            const r = Math.min(fretSpacing, stringSpacing) * 0.38;
            const fill =
              p.correct === false ? 'url(#dot-root)' : p.correct ? 'url(#dot-accent)' : 'url(#dot-cyan)';
            return (
              <g key={`pn-${p.string}-${p.fret}`} filter="url(#glow)">
                <circle
                  cx={fretCenterX(p.fret)}
                  cy={stringY(p.string)}
                  r={r}
                  fill={fill}
                  stroke="rgba(0,229,255,0.7)"
                />
                <text
                  x={fretCenterX(p.fret)}
                  y={stringY(p.string) + 4}
                  textAnchor="middle"
                  fontFamily="Orbitron, sans-serif"
                  fontSize={11}
                  fontWeight={700}
                  fill="#05060d"
                >
                  {p.note}
                </text>
              </g>
            );
          })}

        {/* Hover indicator */}
        {hover && (
          <circle
            cx={fretCenterX(hover.f)}
            cy={stringY(hover.s)}
            r={Math.min(fretSpacing, stringSpacing) * 0.42}
            fill="none"
            stroke="rgba(0,229,255,0.45)"
            strokeDasharray="3 3"
            pointerEvents="none"
          />
        )}
      </svg>
    </div>
  );
}
