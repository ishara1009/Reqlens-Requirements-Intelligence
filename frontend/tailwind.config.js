/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: { ink: '#102a43', ocean: '#0b7285', mint: '#d3f9d8', coral: '#e8590c', paper: '#f7f8f5' },
      boxShadow: { soft: '0 18px 50px rgba(16,42,67,.08)' },
      fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui'], display: ['Manrope', 'Inter', 'sans-serif'] },
    },
  },
  plugins: [],
}

