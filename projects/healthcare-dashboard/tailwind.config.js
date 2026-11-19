// Source for styles.css — regenerate with projects/build-styles.sh
module.exports = {
  content: ['./index.html'],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#60A5FA',
        accent: '#F97316',
        surface: '#F8FAFC',
        text: '#1E293B',
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
      },
      fontFamily: {
        heading: ['Fira Sans', 'sans-serif'],
        body: ['Fira Sans', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      }
    }
  }
};
