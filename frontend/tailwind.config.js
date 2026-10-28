/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        localsubs: {
          orange: '#FF7A1A',
          ink: '#0B1020',
          panel: '#11182B',
        },
      },
    },
  },
  plugins: [],
}
