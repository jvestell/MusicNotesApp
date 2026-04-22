/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          900: '#05060d',
          800: '#0a0c1a',
          700: '#11142a',
          600: '#1a1e3d',
          500: '#252a52',
        },
        neon: {
          cyan: '#00e5ff',
          pink: '#ff3ec8',
          green: '#39ff88',
          red: '#ff5072',
          amber: '#ffc857',
          violet: '#9d5cff',
        },
      },
      fontFamily: {
        display: ['Orbitron', 'ui-sans-serif', 'system-ui'],
        body: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      boxShadow: {
        'glow-cyan': '0 0 18px rgba(0, 229, 255, 0.55), 0 0 4px rgba(0, 229, 255, 0.8)',
        'glow-pink': '0 0 18px rgba(255, 62, 200, 0.55), 0 0 4px rgba(255, 62, 200, 0.8)',
        'glow-green': '0 0 18px rgba(57, 255, 136, 0.6), 0 0 4px rgba(57, 255, 136, 0.9)',
        'glow-red': '0 0 18px rgba(255, 80, 114, 0.6), 0 0 4px rgba(255, 80, 114, 0.9)',
      },
      animation: {
        'aurora': 'aurora 22s ease-in-out infinite',
        'pulse-soft': 'pulse-soft 2.4s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        aurora: {
          '0%, 100%': { transform: 'translate3d(-5%, -5%, 0) rotate(0deg)' },
          '50%': { transform: 'translate3d(5%, 5%, 0) rotate(180deg)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '0.85' },
          '50%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' },
        },
      },
    },
  },
  plugins: [],
};
