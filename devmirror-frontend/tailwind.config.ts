import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        dm: {
          bg:          '#FFFFFF',
          dark:        '#1A1A14',
          orange:      '#F04E00',
          cream:       '#F5F0E8',
          surface:     '#F5F0E8',
          'surface-2': '#EDEAE2',
          'surface-3': '#D8D4CC',
          border:      '#B8B4AC',       // darker border — visible on cream & white
          // Re-mapped so existing dashboard components keep working
          purple:      '#1A1A14',
          'purple-l':  '#2E2E28',
          'purple-ll': '#4A4A44',
          'purple-dim':'rgba(0,0,0,0.06)',
          green:       '#1A5C3A',       // darker green — readable on light bg
          cyan:        '#0F5280',       // darker cyan
          amber:       '#92400E',       // darker amber
          red:         '#991B1B',       // darker red
          text:        '#0A0A0A',       // near-black
          muted:       '#3D3D38',       // was #7A7A6E — 2× better contrast
          dim:         '#6B6B65',       // was #C8C5BE — usable on cream/white
        },
      },
      fontFamily: {
        sans:  ['Inter', 'Helvetica Neue', 'system-ui', 'sans-serif'],
        head:  ['Inter', 'Helvetica Neue', 'system-ui', 'sans-serif'],
        mono:  ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-sm':   'none',
        'glow':      'none',
        'glow-lg':   'none',
        'glow-green':'none',
      },
      backgroundImage: {
        'grid':        'none',
        'hero-radial': 'none',
        'card-glow':   'none',
      },
      animation: {
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'fade-in':    'fadeIn 0.5s ease-out',
        'slide-up':   'slideUp 0.5s ease-out',
        'blink':      'blink 1s step-end infinite',
        'ticker':     'ticker 40s linear infinite',
      },
      keyframes: {
        fadeIn:   { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp:  { from: { opacity: '0', transform: 'translateY(16px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        blink:    { '0%,100%': { opacity: '1' }, '50%': { opacity: '0' } },
        ticker:   { from: { transform: 'translateX(0)' }, to: { transform: 'translateX(-50%)' } },
      },
    },
  },
  plugins: [],
} satisfies Config
