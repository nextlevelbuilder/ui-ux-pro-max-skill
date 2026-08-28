import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6366F1', // Indigo 500
          hover: '#4F46E5',
          muted: '#818CF8',
        },
        accent: '#22D3EE', // Cyan 400
        surface: {
          DEFAULT: '#FFFFFF', // Light
          dark: '#0F172A', // Slate 950
          alt: {
            DEFAULT: '#F8FAFC',
            dark: '#1E293B',
          },
        },
        text: {
          DEFAULT: '#0F172A', // Light
          dark: '#F8FAFC',
          muted: {
            DEFAULT: '#475569',
            dark: '#94A3B8',
          },
        },
        border: {
          DEFAULT: '#E2E8F0',
          dark: '#334155',
        },
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'ui-sans-serif', 'system-ui'],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1.5' }],
        sm: ['0.875rem', { lineHeight: '1.6' }],
        base: ['1rem', { lineHeight: '1.75' }],
        lg: ['1.125rem', { lineHeight: '1.75' }],
        xl: ['1.25rem', { lineHeight: '1.75' }],
        '2xl': ['1.5rem', { lineHeight: '1.5' }],
        '3xl': ['1.875rem', { lineHeight: '1.4' }],
        '4xl': ['2.25rem', { lineHeight: '1.3' }],
      },
      borderRadius: {
        xl: '12px',
        full: '9999px',
      },
    }
  },
  plugins: [],
};

export default config;
