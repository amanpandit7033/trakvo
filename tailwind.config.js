/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          ink: '#10182B',
          paper: '#F7F5F0',
          brass: '#B98B3E',
          hairline: '#E4DFD3',
          teal: '#1F6F63',
          rust: '#B54A3C',
          light: '#F8FAFC',
          dark: '#1E293B',
          gray: '#64748B'
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Source Serif 4', 'serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      boxShadow: {
        card: '0 2px 4px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02)',
      }
    },
  },
  plugins: [],
}
