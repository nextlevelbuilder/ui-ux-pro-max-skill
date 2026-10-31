// FIXTURE: Tailwind config with font families (see ../README.md). Not a real project.
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js}'],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Space Grotesk', 'sans-serif'],
        body: ["Nunito", "sans-serif"],
        mono: 'Fira Code, monospace',
        brand: ['var(--font-brand)', 'Fredoka'],
        system: ['system-ui', 'sans-serif'],
      },
      colors: { accent: '#FF8A4C' },
    },
  },
}
